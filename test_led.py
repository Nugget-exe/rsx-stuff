import sys
import time
from serial import Serial
import serial.tools.list_ports

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton,
    QLabel, QComboBox, QGroupBox, QVBoxLayout, QHBoxLayout, QGridLayout,
    QDoubleSpinBox, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt

# Get available serial ports
available_ports = serial.tools.list_ports.comports()
selected_port = available_ports[0] if available_ports else None
arduino = None  # Uncomment below to initialize with actual serial port
# arduino = Serial(port=selected_port.device, baudrate=9600, timeout=.1)

class StatusSelectionWidget(QWidget):
    """
    Widget for selecting and displaying different status group boxes.
    """
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Dynamic GroupBox Example")
        self.resize(400, 250)
        
        self.main_layout = QVBoxLayout()
        
        # Instruction Label
        self.instruction_label = QLabel("Select a status, press X to close the window")
        self.main_layout.addWidget(self.instruction_label)
        
        # Drop-down selection box
        self.status_selector = QComboBox()
        self.status_selector.addItems(["Select Status", "Batteries", "Motors", "LEDs"])
        self.main_layout.addWidget(self.status_selector)
        
        # Container for dynamically added group boxes
        self.status_group_container = QVBoxLayout()
        
        # Connect selection change event
        self.status_selector.currentIndexChanged.connect(self.add_status_groupbox)
        
        self.setLayout(self.main_layout)
    
    def add_status_groupbox(self, index):
        """
        Adds a status group box based on selection.
        """
        if index == 1:  # Batteries
            battery_status = BatteryStatusWidget()
            self.main_layout.addWidget(battery_status)
        elif index == 2:  # Motors
            motor_status = MotorStatusWidget()
            self.main_layout.addWidget(motor_status)
        elif index == 3:  # LEDs
            led_status = LEDStatusWidget()
            self.main_layout.addWidget(led_status)
        else:
            return

class SignalStatusWidget(QGroupBox):
    """
    Base widget for signal status (Battery, Motor, LED).
    """
    def __init__(self, title: str):
        super().__init__(title)
        self.layout = QGridLayout(self)
        
        # Close button
        self.close_button = QPushButton("X")
        self.close_button.setFixedSize(20, 20)
        self.close_button.clicked.connect(self.close)
        self.layout.addWidget(self.close_button, 0, 2)
        
        # Adjust layout stretch for aesthetics
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 1)
        self.layout.setColumnStretch(2, 0)

class BatteryStatusWidget(SignalStatusWidget):
    def __init__(self):
        super().__init__("Battery Status")
        
        self.layout.addWidget(QLabel("Battery Status"), 0, 0)
        self.layout.addWidget(QLabel("Charging"), 0, 1)
        self.layout.addWidget(QLabel("Voltage"), 1, 0)
        self.layout.addWidget(QLabel("12.5V"), 1, 1)
        self.layout.addWidget(QLabel("Current"), 2, 0)
        self.layout.addWidget(QLabel("0.5A"), 2, 1)
        self.layout.addWidget(QLabel("Temperature"), 3, 0)
        self.layout.addWidget(QLabel("25°C"), 3, 1)

class MotorStatusWidget(SignalStatusWidget):
    def __init__(self):
        super().__init__("Motor Status")
        
        self.layout.addWidget(QLabel("Motor Status"), 0, 0)
        self.layout.addWidget(QLabel("Running"), 0, 1)
        self.layout.addWidget(QLabel("Speed"), 1, 0)
        self.layout.addWidget(QLabel("1000 RPM"), 1, 1)
        self.layout.addWidget(QLabel("Torque"), 2, 0)
        self.layout.addWidget(QLabel("10 Nm"), 2, 1)
        self.layout.addWidget(QLabel("Temperature"), 3, 0)
        self.layout.addWidget(QLabel("45°C"), 3, 1)

class LEDStatusWidget(SignalStatusWidget):
    def __init__(self):
        super().__init__("LED Status")
        
        self.layout.addWidget(QLabel("LED Status"), 0, 0)
        self.layout.addWidget(QLabel("On"), 0, 1)
        self.layout.addWidget(QLabel("Color"), 1, 0)
        self.layout.addWidget(QLabel("Green"), 1, 1)

class RobotControlGUI(QMainWindow):
    """
    Main GUI for Robot Control.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Robot Operating System")
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        left_layout = QVBoxLayout()
        main_layout.addLayout(left_layout, stretch=1)
        
        right_layout = QVBoxLayout()
        main_layout.addLayout(right_layout, stretch=1)
        
        # Signals & Status Section
        status_group = QGroupBox("Signals and Status")
        status_layout = QVBoxLayout(status_group)
        self.status_widget = StatusSelectionWidget()
        status_layout.addWidget(self.status_widget)
        left_layout.addWidget(status_group)
        
        # Power Supply Section
        power_group = QGroupBox("Power Supply")
        power_layout = QGridLayout(power_group)
        power_layout.addWidget(QLabel("3.3V"), 0, 0)
        right_layout.addWidget(power_group)
        
        # Emergency Stop Section
        emergency_group = QGroupBox("Emergency Stop")
        emergency_layout = QGridLayout(emergency_group)
        self.dt_spin = QDoubleSpinBox()
        self.dt_spin.setValue(0.125)
        emergency_layout.addWidget(QLabel("dt ="), 0, 0)
        emergency_layout.addWidget(self.dt_spin, 0, 1)
        
        self.z_spin = QDoubleSpinBox()
        self.z_spin.setValue(20)
        emergency_layout.addWidget(QLabel("Z ="), 0, 2)
        emergency_layout.addWidget(self.z_spin, 0, 3)
        
        go_button = QPushButton("Go")
        stop_button = QPushButton("Stop")
        go_button.clicked.connect(self.on_go)
        stop_button.clicked.connect(self.on_stop)
        emergency_layout.addWidget(go_button, 1, 0)
        emergency_layout.addWidget(stop_button, 1, 1)
        
        right_layout.addWidget(emergency_group)
    
    def on_go(self):
        print(f"Go with dt={self.dt_spin.value()}, Z={self.z_spin.value()}")
    
    def on_stop(self):
        print("Stop pressed")

# Main function to run the application
def main():
    app = QApplication(sys.argv)
    gui = RobotControlGUI()
    gui.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
