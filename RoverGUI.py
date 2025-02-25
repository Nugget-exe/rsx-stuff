# Why it is called RoverGUI: This program is for faking the GUI of a rover control system.

import sys
import time
import random
from serial import Serial
import serial.tools.list_ports

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton,
    QLabel, QComboBox, QGroupBox, QVBoxLayout, QHBoxLayout, QGridLayout,
    QDoubleSpinBox, QScrollArea, QSizePolicy, QTableView
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QStandardItemModel, QStandardItem

# Get available serial ports
available_ports = serial.tools.list_ports.comports()
selected_port = available_ports[0] if available_ports else None
# arduino = None  # Uncomment below to initialize with actual serial port
print(selected_port.device)
arduino = Serial(port=selected_port.device, baudrate=115200, timeout=.1)

# communicate with the arduino: the write_read function
def write_read(x):
    if arduino is None:
        print("Not connected")
        return
    arduino.write(bytes(x, 'utf-8'))
    time.sleep(0.1)

    data = arduino.readline()
    print(data)

    return data


class StatusSelectionWidget(QWidget):
    """
    Widget for selecting and displaying different status group boxes.
    """
    def __init__(self, temp_label):
        super().__init__()

        self.temp_label = temp_label
        
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
            led_status = LEDStatusWidget(self.temp_label)
            self.main_layout.addWidget(led_status)
        self.status_selector.setCurrentIndex(0)  # Reset selection


class SignalStatusWidget(QGroupBox):
    """
    Base widget for signal status (Battery, Motor, LED).
    """
    def __init__(self, title: str):
        super().__init__(title)
        self.layout = QGridLayout(self)
        
        # Close button
        self.close_button = QPushButton("x")
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
    def __init__(self, temp_label):
        super().__init__("LED Status")
        
        self.layout.addWidget(QLabel("LED Status"), 0, 0)
        self.layout.addWidget(temp_label, 0, 1)
        # self.layout.addWidget(QLabel("Color"), 1, 0)
        # self.layout.addWidget(QLabel("Green"), 1, 1)

class FakeNumber(QLabel):
    def __init__(self, current_value: float, ideal_value: float, std_dev: float, alpha: float=0.1, beta: float=0.1):
        """
        Fake number label for displaying a number with ideal value and standard deviation.
        :param current_value: Number to display.
        :param ideal_value: Ideal value of the number.
        :param std_dev: Standard deviation of the number.
        :param alpha: 回归强度
        :param beta: 随机强度
        """
        super().__init__(str(current_value))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_value = current_value
        self.ideal_value = ideal_value
        self.std_dev = std_dev
        self.alpha = alpha
        self.beta = beta
        self.last_delta = ideal_value - current_value

    def generate_smooth_value(self):
        """
        生成平滑的电压/电流伪造数据。

        参数:
        - current_value: float, 当前电压/电流值。
        - last_delta: float, 上一次的变化值（类似于导数）。
        - ideal_value: float, 理想的电压/电流值。
        - sigma: float, 标准差，控制随机波动的幅度。
        - alpha: float, 默认0.1，控制向理想值回归的强度。
        - beta: float, 默认0.5，控制变化率的影响。

        返回:
        - new_value: float, 新的电压/电流值。
        - new_delta: float, 新的变化值（new_value - current_value）。
        """
        # 趋势项：使新值向理想值靠拢
        trend = self.alpha * (self.ideal_value - self.current_value)
        # 导数影响：考虑上一次的变化
        derivative_effect = self.beta * self.last_delta
        # 随机扰动：从正态分布中抽取
        noise = random.gauss(0, self.std_dev)
        # 计算新值
        new_value = self.current_value + trend + derivative_effect + noise
        # 计算新的变化值
        new_delta = new_value - self.current_value

        # 更新状态
        self.current_value = new_value
        self.last_delta = new_delta
        self.setText(f"{new_value:.2f}")


class RobotControlGUI(QMainWindow):
    """
    Main GUI for Robot Control.
    """
    def __init__(self):
        super().__init__()

        self.temp_label = QLabel("off")

        # store the voltage values and current values
        self.v_c_values = []

        # set the timer for updating the voltage and current values
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_v_c_values)
        self.timer.start(1000)

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
        self.status_widget = StatusSelectionWidget(self.temp_label)
        status_layout.addWidget(self.status_widget)
        left_layout.addWidget(status_group)

        # led control section:
        LED_control_group = QGroupBox("LED Control")
        LED_control_layout = QGridLayout(LED_control_group)
        LED_button_ON = QPushButton("LED ON")
        LED_button_OFF = QPushButton("LED OFF")
        LED_button_BLINK = QPushButton("LED BLINK")
        LED_control_layout.addWidget(LED_button_ON, 0,0)
        LED_control_layout.addWidget(LED_button_OFF, 0,1)
        LED_control_layout.addWidget(LED_button_BLINK, 0,2)
        left_layout.addWidget(LED_control_group)

        # click the led button:
        LED_button_ON.clicked.connect(self.handle_led_on)
        LED_button_OFF.clicked.connect(self.handle_led_off)
        LED_button_BLINK.clicked.connect(self.handle_led_blink)
        
        # Power Supply Section
        self.power_group = QGroupBox("Power Supply")
        self.power_layout = QGridLayout(self.power_group)

        self.power_layout.addWidget(QLabel("Voltage"), 0, 0)
        self.power_layout.addWidget(QLabel("Specification"), 0, 1)
        self.power_layout.addWidget(QLabel("Operation Voltage(V)"), 0, 2)   
        self.power_layout.addWidget(QLabel("Operation Current(mA)"), 0, 3)
        self.power_layout.addWidget(QLabel("Status"), 0, 4)
        self.power_layout.addWidget(QLabel("Control"), 0, 5)

        # voltage
        self.power_layout.addWidget(QLabel("3.3V"), 1, 0)
        self.power_layout.addWidget(QLabel("5V"), 2, 0)
        self.power_layout.addWidget(QLabel("12V"), 3, 0)
        self.power_layout.addWidget(QLabel("19V"), 4, 0)
        self.power_layout.addWidget(QLabel("24V"), 5, 0)
        self.power_layout.addWidget(QLabel("56V"), 6, 0)

        # specification
        self.power_layout.addWidget(QLabel("Main Controller"), 1, 1)
        self.power_layout.addWidget(QLabel("Tire Power Control Signals, Network Switch"), 2, 1)
        self.power_layout.addWidget(QLabel("AUX"), 3, 1)
        self.power_layout.addWidget(QLabel("Computer"), 4, 1)
        self.power_layout.addWidget(QLabel("Antenna, Cameras"), 5, 1)
        self.power_layout.addWidget(QLabel("Special Scientific Camera, Main Bus"), 6, 1)

        # real voltage
        self.v_c_values.append(FakeNumber(3.29, 3.3, 0.1))
        self.power_layout.addWidget(self.v_c_values[-1], 1, 2)
        self.v_c_values.append(FakeNumber(4.89, 5, 0.1))
        self.power_layout.addWidget(self.v_c_values[-1], 2, 2)
        self.v_c_values.append(FakeNumber(11.98, 12, 0.1))
        self.power_layout.addWidget(self.v_c_values[-1], 3, 2)
        self.v_c_values.append(FakeNumber(19.05, 19, 0.1))
        self.power_layout.addWidget(self.v_c_values[-1], 4, 2)
        self.v_c_values.append(FakeNumber(23.95, 24, 0.1))
        self.power_layout.addWidget(self.v_c_values[-1], 5, 2)
        self.v_c_values.append(FakeNumber(55.80, 56, 0.1))
        self.power_layout.addWidget(self.v_c_values[-1], 6, 2)

        # real current
        self.v_c_values.append(FakeNumber(11.9, 12, 0.1))
        self.power_layout.addWidget(self.v_c_values[-1], 1, 3)
        self.v_c_values.append(FakeNumber(29.5, 30, 0.1))
        self.power_layout.addWidget(self.v_c_values[-1], 2, 3)
        self.v_c_values.append(FakeNumber(1120, 1100, 10))
        self.power_layout.addWidget(self.v_c_values[-1], 3, 3)
        self.v_c_values.append(FakeNumber(5900, 6000, 50))
        self.power_layout.addWidget(self.v_c_values[-1], 4, 3)
        self.v_c_values.append(FakeNumber(3203, 3200, 20))
        self.power_layout.addWidget(self.v_c_values[-1], 5, 3)
        self.v_c_values.append(FakeNumber(4732, 4700, 30))
        self.power_layout.addWidget(self.v_c_values[-1], 6, 3)

        # status:
        self.status_3_3 = QLabel("--", self)
        self.status_5 = QLabel("--", self)
        self.status_12 = QLabel("--", self)
        self.status_19 = QLabel("--", self)
        self.status_24 = QLabel("--", self)
        self.status_56 = QLabel("--", self)

        self.power_layout.addWidget(self.status_3_3, 1, 4)
        self.power_layout.addWidget(self.status_5, 2, 4)
        self.power_layout.addWidget(self.status_12, 3, 4)
        self.power_layout.addWidget(self.status_19, 4, 4)
        self.power_layout.addWidget(self.status_24, 5, 4)
        self.power_layout.addWidget(self.status_56, 6, 4)

        # control
        #for i in range(1,7):
            # power_layout.addWidget(QPushButton("ON"), i, 5)
            # power_layout.addWidget(QPushButton("OFF"), i, 6)
        button_3_3_on = QPushButton("ON")
        button_3_3_off = QPushButton("OFF")
        button_5_on = QPushButton("ON")
        button_5_off = QPushButton("OFF")
        button_12_on = QPushButton("ON")
        button_12_off = QPushButton("OFF")
        button_19_on = QPushButton("ON")
        button_19_off = QPushButton("OFF")
        button_24_on = QPushButton("ON")
        button_24_off = QPushButton("OFF")
        button_56_on = QPushButton("ON")
        button_56_off = QPushButton("OFF")
        self.power_layout.addWidget(button_3_3_on, 1, 5)
        self.power_layout.addWidget(button_3_3_off, 1, 6)
        self.power_layout.addWidget(button_5_on, 2, 5)
        self.power_layout.addWidget(button_5_off, 2, 6)
        self.power_layout.addWidget(button_12_on, 3, 5)
        self.power_layout.addWidget(button_12_off, 3, 6)
        self.power_layout.addWidget(button_19_on, 4, 5)
        self.power_layout.addWidget(button_19_off, 4, 6)
        self.power_layout.addWidget(button_24_on, 5, 5)
        self.power_layout.addWidget(button_24_off, 5, 6)
        self.power_layout.addWidget(button_56_on, 6, 5)
        self.power_layout.addWidget(button_56_off, 6, 6)

        # handle click:
        button_3_3_on.clicked.connect(self.handle_on_3_3)
        button_3_3_off.clicked.connect(self.handle_off_3_3)
        button_5_on.clicked.connect(self.handle_on_5)
        button_5_off.clicked.connect(self.handle_off_5)
        button_12_on.clicked.connect(self.handle_on_12)
        button_12_off.clicked.connect(self.handle_off_12)
        button_19_on.clicked.connect(self.handle_on_19)
        button_19_off.clicked.connect(self.handle_off_19)
        button_24_on.clicked.connect(self.handle_on_24)
        button_24_off.clicked.connect(self.handle_off_24)
        button_56_on.clicked.connect(self.handle_on_56)
        button_56_off.clicked.connect(self.handle_off_56)

        # self.power_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        for widget in self.power_group.findChildren(QLabel):
            widget.setAlignment(Qt.AlignmentFlag.AlignCenter)


        right_layout.addWidget(self.power_group)
        
        # Emergency Stop Section
        emergency_group = QGroupBox("Emergency Stop")
        emergency_layout = QGridLayout(emergency_group)
        
        go_button = QPushButton("GO")
        turn_off_main_bus_button = QPushButton("Turn off the Main Bus")
        turn_off_partially = QPushButton("Turn off everything except 3.3V, 5V, 19V")
        stop_button = QPushButton("STOP")
        
        go_button.clicked.connect(self.on_go)
        turn_off_main_bus_button.clicked.connect(self.handle_turnoff_main_bus)
        turn_off_partially.clicked.connect(self.handle_turnoff_partially)
        stop_button.clicked.connect(self.on_stop)

        emergency_layout.addWidget(stop_button, 0, 0)
        emergency_layout.addWidget(turn_off_partially, 1, 0)
        emergency_layout.addWidget(turn_off_main_bus_button, 2,0)
        emergency_layout.addWidget(go_button, 3, 0)
        
        right_layout.addWidget(emergency_group)

    def update_v_c_values(self):
        # print("update voltage and current values")
        for v_c_value in self.v_c_values:
            v_c_value.generate_smooth_value()

    # Related functions:
    # functions in LED control section:
    def handle_led_on(self):
        write_read("green on\n")
        self.temp_label.setText("on")
        print("LED_ON")

    def handle_led_off(self):
        write_read("off\n")
        self.temp_label.setText("off")
        print("LED_OFF")

    def handle_led_blink(self):
        write_read("green blink\n")
        self.temp_label.setText("blink")
        print("LED_BLINK")

    # functions in E STOP section: 
    def on_go(self):
        print("Go pressed")
    
    def on_stop(self):
        print("Stop pressed")

    def handle_turnoff_main_bus(self):
        print("turn off the main bus")
    
    def handle_turnoff_partially(self):
        print("turn off everything except 19v, 3.3v, 5v")

    # functions in Power Supply Section:
    def handle_on_3_3(self):
        self.status_3_3.setText("ON")
        print("3.3 ON")

    def handle_off_3_3(self):
        self.status_3_3.setText("OFF")
        print("3.3 OFF")
        
    def handle_on_5(self):
        self.status_5.setText("ON")
        print("5 ON")

    def handle_off_5(self):
        self.status_5.setText("OFF")
        print("5 OFF")

    def handle_on_12(self):
        self.status_12.setText("ON")
        print("12 ON")

    def handle_off_12(self):
        self.status_12.setText("OFF")
        print("12 OFF")

    def handle_on_19(self):
        self.status_19.setText("ON")
        print("19 ON")

    def handle_off_19(self):
        self.status_19.setText("OFF")
        print("19 OFF")

    def handle_on_24(self):
        self.status_24.setText("ON")
        print("24 ON")

    def handle_off_24(self):
        self.status_24.setText("OFF")
        print("24 OFF")

    def handle_on_56(self):
        self.status_56.setText("ON")
        print("56 ON")

    def handle_off_56(self):
        self.status_56.setText("OFF")
        print("56 OFF")

# Main function to run the application
def main():
    try:
        app = QApplication(sys.argv)
        gui = RobotControlGUI()
        gui.show()
        sys.exit(app.exec())
    except Exception as e:
        print("Error: ", e)

if __name__ == "__main__":
    main()
