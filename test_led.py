import sys
from serial import Serial

import time
import serial.tools.list_ports
ports = serial.tools.list_ports.comports()

port = ports[0] if ports else None
#arduino = Serial(port=port.device, baudrate=9600, timeout=.1)
arduino = None

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton,
    QLabel, QLineEdit, QGridLayout, QComboBox, QGroupBox,
    QVBoxLayout, QHBoxLayout, QSpinBox, QDoubleSpinBox, QLCDNumber,
    QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt


class Add_Status_GroupBox(QWidget):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.setWindowTitle("Dynamic GroupBox Example")
        self.resize(400, 250)

        # Create a layout for the main window
        self.layout = QVBoxLayout()

        # Create a QLabel for instructions
        self.label = QLabel("Add a status, press x to close the window")
        self.layout.addWidget(self.label)

        # Create a QComboBox with options
        self.combo_box = QComboBox()

        self.combo_box.addItems(["ADD STATUS", "BATTERIES", "MOTORS", "LEDs"])
        self.layout.addWidget(self.combo_box)

        # Create a placeholder layout to hold the group boxes
        self.group_box_container = QVBoxLayout()

        # Connect the combo box signal to a method that updates the UI
        self.combo_box.currentIndexChanged.connect(self.add_groupbox)

        # Set the layout for the main widget
        self.setLayout(self.layout)

    def add_groupbox(self, index):
        """Create a QGroupBox based on the selected option."""
        # Clear previous group boxes
        # for i in reversed(range(self.group_box_container.count())):
        #     widget = self.group_box_container.itemAt(i).widget()
        #     if widget is not None:
        #         widget.deleteLater()

        if index == 1:  # batteries selected
            groupbox = QGroupBox("Batteries")
            battery_box = BatteryStatusWidget()
            self.layout.addWidget(battery_box)


        elif index == 2:  # motors selected
            groupbox = QGroupBox("Motors")
            motor_box = MotorStatusWidget()
            self.layout.addWidget(motor_box)


        elif index == 3:  # LED selected
            groupbox = QGroupBox("LEDs")
            LEDs_box = LEDStatusWidget()
            self.layout.addWidget(LEDs_box)

        else:
            return  # Do nothing if the default option is selected

        # Add the new group box to the layout
        self.group_box_container.addWidget(groupbox)

class SignalStatusWidget(QGroupBox):
    """
    The custom widget for signal status.
    There are few types of widgets:
    1. battery status
    2. motor status
    3. LED status
    """

    def __init__(self, widget_type: str):
        super().__init__("Signal Status")

        ss_layout = QGridLayout(self)
        self._layout = ss_layout

        # The close button
        ss_close_button = QPushButton("X")
        ss_close_button.setFixedSize(20, 20)
        ss_close_button.clicked.connect(self.close)
        ss_layout.addWidget(ss_close_button, 0, 2)

        # Set the layout stretch to make the close button not consume too much space
        ss_layout.setColumnStretch(0, 1)
        ss_layout.setColumnStretch(1, 1)
        ss_layout.setColumnStretch(2, 0)


class BatteryStatusWidget(SignalStatusWidget):
    def __init__(self):
        super().__init__("battery")

        ss_layout = self._layout

        ss_layout.addWidget(QLabel("Battery Status"), 0, 0)
        battery_status = QLabel("Charging")
        ss_layout.addWidget(battery_status, 0, 1)

        ss_layout.addWidget(QLabel("Voltage"), 1, 0)
        battery_voltage = QLabel("12.5V")
        ss_layout.addWidget(battery_voltage, 1, 1)

        ss_layout.addWidget(QLabel("Current"), 2, 0)
        battery_current = QLabel("0.5A")
        ss_layout.addWidget(battery_current, 2, 1)

        ss_layout.addWidget(QLabel("Temperature"), 3, 0)
        battery_temp = QLabel("25°C")
        ss_layout.addWidget(battery_temp, 3, 1)


class MotorStatusWidget(SignalStatusWidget):
    def __init__(self):
        super().__init__("motor")

        ss_layout = self._layout

        ss_layout.addWidget(QLabel("Motor Status"), 0, 0)
        motor_status = QLabel("Running")
        ss_layout.addWidget(motor_status, 0, 1)

        ss_layout.addWidget(QLabel("Speed"), 1, 0)
        motor_speed = QLabel("1000 RPM")
        ss_layout.addWidget(motor_speed, 1, 1)

        ss_layout.addWidget(QLabel("Torque"), 2, 0)
        motor_torque = QLabel("10 Nm")
        ss_layout.addWidget(motor_torque, 2, 1)

        ss_layout.addWidget(QLabel("Temperature"), 3, 0)
        motor_temp = QLabel("45°C")
        ss_layout.addWidget(motor_temp, 3, 1)


class LEDStatusWidget(SignalStatusWidget):
    def __init__(self):
        super().__init__("LED")

        ss_layout = self._layout

        ss_layout.addWidget(QLabel("LED Status"), 0, 0)
        led_status = QLabel("On")
        ss_layout.addWidget(led_status, 0, 1)

        ss_layout.addWidget(QLabel("Color"), 1, 0)
        led_color = QLabel("Green")
        ss_layout.addWidget(led_color, 1, 1)


class PowerSupplyWidget(QGroupBox):
    def __init__(self, name: str):
        super().__init__("Power Supply")

        ps_layout = QGridLayout(self)

        ps_layout.addWidget(QLabel(name), 0, 0)
        self.power_label = QLabel("haha")
        ps_layout.addWidget(self.power_label, 0, 1)


class RobotGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Robot Operating System")

        # 中心主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 总体布局
        main_layout = QHBoxLayout(central_widget)

        # 左侧布局（各种输入、按钮等）
        left_layout = QVBoxLayout()
        main_layout.addLayout(left_layout, stretch=1)

        # 右侧布局（放置绘图）
        right_layout = QVBoxLayout()
        main_layout.addLayout(right_layout, stretch=1)

        # =============== 1. Signals & Status ===============

        path_entry_group = QGroupBox("Signals and Status")
        path_entry_layout = QGridLayout(path_entry_group)

        Add_button = Add_Status_GroupBox()

        path_entry_content = QWidget()

        path_entry_content.resize()

        path_entry_content_layout = QVBoxLayout(path_entry_content)
        path_entry_content_layout.addWidget(Add_button)

        # path_entry_content_layout.addWidget(BatteryStatusWidget())
        # path_entry_content_layout.addWidget(MotorStatusWidget())
        # path_entry_content_layout.addWidget(LEDStatusWidget())
        # path_entry_content_layout.addWidget(BatteryStatusWidget())
        # path_entry_content_layout.addWidget(MotorStatusWidget())
        # path_entry_content_layout.addWidget(LEDStatusWidget())

        # The add button
        #add_button = QPushButton("Add")
        #path_entry_layout.addWidget(add_button, 0, 0)

        # create a scrollable widget
        scroll_widget = QScrollArea()
        scroll_widget.setWidgetResizable(True)
        scroll_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        scroll_widget.setWidget(path_entry_content)
        path_entry_layout.addWidget(scroll_widget, 1, 0)
        left_layout.addWidget(path_entry_group)

        # =============== 2. Power Supply ===============
        port_group = QGroupBox("Power Supply")
        port_layout = QGridLayout(port_group)

        port_layout.addWidget(QLabel("3.3v"), 0, 0)

        right_layout.addWidget(port_group)

        # =============== 4. Robot Control ===============
        robot_group = QGroupBox("Emergency Stop")
        robot_layout = QGridLayout(robot_group)

        # dt
        robot_layout.addWidget(QLabel("dt ="), 0, 0)
        self.dt_spin = QDoubleSpinBox()
        self.dt_spin.setValue(0.125)
        robot_layout.addWidget(self.dt_spin, 0, 1)

        # z
        robot_layout.addWidget(QLabel("Z ="), 0, 2)
        self.z_spin = QDoubleSpinBox()
        self.z_spin.setValue(20)
        robot_layout.addWidget(self.z_spin, 0, 3)

        start_pos_button = QPushButton("Start Position")
        torque_button = QPushButton("Torque")
        reset_z_button = QPushButton("reset Z")

        go_button = QPushButton("Go")
        stop_button = QPushButton("Stop")

        LED_button_ON = QPushButton("LED ON")
        LED_button_OFF = QPushButton("LED OFF")
        LED_button_BLINK = QPushButton("LED BLINK")


        robot_layout.addWidget(start_pos_button, 1, 0)
        robot_layout.addWidget(torque_button, 1, 1)
        robot_layout.addWidget(reset_z_button, 1, 2)

        robot_layout.addWidget(go_button, 2, 0)
        robot_layout.addWidget(stop_button, 2, 1)


        robot_layout.addWidget(LED_button_ON, 3, 0)
        robot_layout.addWidget(LED_button_OFF, 3, 1)
        robot_layout.addWidget(LED_button_BLINK, 3, 2)

        right_layout.addWidget(robot_group)

        # ============ Some simple event handling ============

        go_button.clicked.connect(self.on_go)
        stop_button.clicked.connect(self.on_stop)

        LED_button_ON.clicked.connect(self.handle_led_on)
        LED_button_OFF.clicked.connect(self.handle_led_off)
        LED_button_BLINK.clicked.connect(self.handle_led_blink)


    # ============ 以下函数可按需实现实际逻辑 ============

    def on_load_clicked(self):
        """点击Load按钮事件"""
        coords_text = self.path_input.text()
        print("Load coordinates:", coords_text)
        # TODO: 实现加载逻辑

    def on_add_clicked(self):
        """点击Add按钮事件"""
        coords_text = self.path_input.text()
        print("Add coordinates:", coords_text)
        # TODO: 实现添加逻辑

    def on_calc_clicked(self):
        """点击Calculate按钮事件"""
        leg_num = self.leg_num_edit.value()
        theta0 = self.theta0_edit.value()
        # TODO: 实际计算 Fx, Fy, Fz
        # 这里只是演示，所以设为固定值
        Fx, Fy, Fz = 10.5, 20.5, 30.5
        self.fx_label.setText(str(Fx))
        self.fy_label.setText(str(Fy))
        self.fz_label.setText(str(Fz))
        print(f"Calculate leg forces for Leg#{leg_num}, theta0={theta0}")

    def on_open_port(self):
        """点击Open Port按钮事件"""
        port_name = self.port_combo.currentText()
        self.port_status_label.setText("Port Opened: " + port_name)
        print("Open port:", port_name)
        # TODO: 串口打开逻辑

    def on_close_port(self):
        """点击Close Port按钮事件"""
        self.port_status_label.setText("Port Closed")
        print("Close port")
        # TODO: 串口关闭逻辑

    def on_update_dynamics(self):
        """点击Update按钮事件"""
        print("Update dynamics")
        # TODO: 实现与动力学相关的更新

    def on_go(self):
        """点击Go按钮事件"""
        dt_val = self.dt_spin.value()
        z_val = self.z_spin.value()
        print(f"Go with dt={dt_val}, Z={z_val}")
        # TODO: 运动启动逻辑

    def on_stop(self):
        """点击Stop按钮事件"""
        print("Stop pressed")
        # TODO: 停止运动逻辑

    def on_about(self):
        """点击About按钮事件"""
        print("显示关于窗口或信息...")
        # TODO: 弹出一个关于框


    def handle_led_on(self):
        write_read("LED_ON")
        print("LED_ON")

    def handle_led_off(self):
        write_read("LED_OFF")
        print("LED_OFF")

    def handle_led_blink(self):
        write_read("LED_BLINK")
        print("LED_BLINK")




def write_read(x):
    arduino.write(bytes(x, 'utf-8'))
    time.sleep(0.1)
    data = arduino.readline()
    print(data)
    return data

def main():
    app = QApplication(sys.argv)
    gui = RobotGUI()
    gui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
