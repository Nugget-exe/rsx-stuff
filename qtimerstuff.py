import sys
import random
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import QTimer, pyqtSlot

class UIUpdatesWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('UI Updates Example')
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        self.label = QLabel('Random Number: 0')
        self.button = QPushButton("update info")
        self.button.clicked.connect(self.update_label)

        layout.addWidget(self.label)
        layout.addWidget(self.button)

        self.setLayout(layout)

        self.timer = QTimer(self)
        self.timer.setInterval(0)  # Set interval to 1 second
        #self.timer.timeout.connect(self.update_label)
        self.timer.start()

    def update_label(self):
        random_number = random.randint(1, 100)
        self.label.setText(f'Random Number: {random_number}')

# Create an instance of QApplication
app = QApplication(sys.argv)

# Create and display the UI updates window
window = UIUpdatesWindow()
window.show()

# Run the application's event loop
sys.exit(app.exec())
