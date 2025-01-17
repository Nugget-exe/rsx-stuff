import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton,
    QLabel, QLineEdit, QGridLayout, QComboBox, QGroupBox,
    QVBoxLayout, QHBoxLayout, QSpinBox, QDoubleSpinBox
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MplCanvas(FigureCanvas):
    """封装 Matplotlib 画布以便在 PyQt 中使用。"""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)


class RobotGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Robot GUI (PyQt版)")

        # 中心主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 总体布局
        main_layout = QHBoxLayout(central_widget)

        # 左侧布局（各种输入、按钮等）
        left_layout = QVBoxLayout()
        main_layout.addLayout(left_layout, stretch=1)

        # 右侧布局（放置绘图）
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        main_layout.addWidget(self.canvas, stretch=2)

        # =============== 1. Path Entry ===============
        path_entry_group = QGroupBox("Path Entery")
        path_entry_layout = QGridLayout(path_entry_group)

        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("示例: 10 30 35 70 62 -5")
        load_button = QPushButton("Load")
        add_button = QPushButton("Add")

        path_entry_layout.addWidget(QLabel("Enter Coordinates:"), 0, 0)
        path_entry_layout.addWidget(self.path_input, 0, 1, 1, 2)
        path_entry_layout.addWidget(load_button, 1, 1)
        path_entry_layout.addWidget(add_button, 1, 2)

        left_layout.addWidget(path_entry_group)

        # =============== 2. Calculate leg forces ===============
        calc_group = QGroupBox("Calculate leg forces")
        calc_layout = QGridLayout(calc_group)

        calc_layout.addWidget(QLabel("Leg #:"), 0, 0)
        self.leg_num_edit = QSpinBox()
        calc_layout.addWidget(self.leg_num_edit, 0, 1)

        calc_button = QPushButton("Calculate")
        calc_layout.addWidget(calc_button, 0, 2)

        calc_layout.addWidget(QLabel("theta0:"), 1, 0)
        self.theta0_edit = QDoubleSpinBox()
        self.theta0_edit.setDecimals(2)
        calc_layout.addWidget(self.theta0_edit, 1, 1)

        calc_layout.addWidget(QLabel("Fx:"), 2, 0)
        self.fx_label = QLabel("0")
        calc_layout.addWidget(self.fx_label, 2, 1)

        calc_layout.addWidget(QLabel("Fy:"), 3, 0)
        self.fy_label = QLabel("0")
        calc_layout.addWidget(self.fy_label, 3, 1)

        calc_layout.addWidget(QLabel("Fz:"), 4, 0)
        self.fz_label = QLabel("0")
        calc_layout.addWidget(self.fz_label, 4, 1)

        left_layout.addWidget(calc_group)

        # =============== 3. Port Control ===============
        port_group = QGroupBox("Port Control")
        port_layout = QGridLayout(port_group)

        update_button = QPushButton("Update")
        port_layout.addWidget(update_button, 0, 0)

        self.port_combo = QComboBox()
        # 示例串口号，可自行扩展
        self.port_combo.addItems(["COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7"])
        open_port_button = QPushButton("Open Port")
        close_port_button = QPushButton("Close Port")
        self.port_status_label = QLabel("Port Closed")

        port_layout.addWidget(self.port_combo, 1, 0)
        port_layout.addWidget(open_port_button, 1, 1)
        port_layout.addWidget(close_port_button, 1, 2)
        port_layout.addWidget(self.port_status_label, 2, 0, 1, 3)

        left_layout.addWidget(port_group)

        # =============== 4. Robot Control ===============
        robot_group = QGroupBox("Robot Control")
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

        robot_layout.addWidget(start_pos_button, 1, 0)
        robot_layout.addWidget(torque_button, 1, 1)
        robot_layout.addWidget(reset_z_button, 1, 2)

        robot_layout.addWidget(go_button, 2, 0)
        robot_layout.addWidget(stop_button, 2, 1)

        left_layout.addWidget(robot_group)

        # 关于/About 按钮
        about_button = QPushButton("About")
        left_layout.addWidget(about_button)

        # ============ 为示例添加一些简单事件处理 ============

        load_button.clicked.connect(self.on_load_clicked)
        add_button.clicked.connect(self.on_add_clicked)
        calc_button.clicked.connect(self.on_calc_clicked)
        open_port_button.clicked.connect(self.on_open_port)
        close_port_button.clicked.connect(self.on_close_port)
        update_button.clicked.connect(self.on_update_dynamics)
        go_button.clicked.connect(self.on_go)
        stop_button.clicked.connect(self.on_stop)
        about_button.clicked.connect(self.on_about)

        # 初始化绘图
        self.init_plot()

    def init_plot(self):
        """初始绘制空图或演示图。"""
        self.canvas.axes.clear()
        self.canvas.axes.set_title("Robot Path")
        self.canvas.axes.set_xlabel("x [mm]")
        self.canvas.axes.set_ylabel("y [mm]")
        self.canvas.axes.grid(True)
        self.canvas.draw()

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


def main():
    app = QApplication(sys.argv)
    gui = RobotGUI()
    gui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
