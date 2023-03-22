import subprocess
import sys
import time
import codecs
#from PyQt5.QtCore import QTimer

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
)


class PingWorker(QThread):
    pingOutput = pyqtSignal(str)

    def __init__(self, parent=None):
        super(PingWorker, self).__init__(parent)
        self.ping_process = None
        self.is_running = False

    def start_ping(self, destination):
        self.is_running = True
        self.ping_process = subprocess.Popen(
            f"ping -t {destination}", shell=True, stdout=subprocess.PIPE
        )

    def stop_ping(self):
        self.is_running = False
        if self.ping_process:
            self.ping_process.kill()
            self.ping_process = None

    def run(self):
        while self.is_running:
            line = self.ping_process.stdout.readline().decode("cp1251").strip()
            if line:
                self.pingOutput.emit(line)
            time.sleep(3)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ping Speed Test")

        # UI elements
        destination_label = QLabel("Destination:")
        self.destination_input = QLineEdit()
        duration_label = QLabel("Duration (seconds):")
        self.duration_input = QLineEdit()
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.log_output = QTextEdit()

        # Connect buttons to slots
        self.start_button.clicked.connect(self.start_ping)
        self.stop_button.clicked.connect(self.stop_ping)

        # Layout
        input_layout = QHBoxLayout()
        input_layout.addWidget(destination_label)
        input_layout.addWidget(self.destination_input)
        input_layout.addWidget(duration_label)
        input_layout.addWidget(self.duration_input)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(input_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.log_output)

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

        # Ping worker
        self.ping_worker = PingWorker()
        self.ping_worker.pingOutput.connect(self.log_output.append)
        self.ping_worker.finished.connect(self.ping_worker.deleteLater)

        # File output
        self.file_output = None

    def start_ping(self):
        # Start ping worker
        destination = self.destination_input.text()
        duration = int(self.duration_input.text())

        self.ping_worker.start_ping(destination)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        # Start file output
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{destination}_{timestamp}.txt"
        self.file_output = codecs.open(filename, "w", "cp1251")

        # Stop file output after duration
        QTimer.singleShot(duration * 1000, self.stop_file_output)

    def stop_ping(self):
        # Stop ping worker
        self.ping_worker.stop_ping()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

        # Stop file output
        self.stop_file_output()

    def stop_file_output(self):
        if self.file_output:
            self.file_output.close()
            self.file_output = None

    def closeEvent(self, event):
        self.stop_ping()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow
