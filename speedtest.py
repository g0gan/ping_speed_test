from PyQt5.QtWidgets import QApplication, QMainWindow, QPlainTextEdit, QPushButton
from PyQt5.QtCore import QTimer, QProcess
from PyQt5.QtGui import QTextCursor
import datetime
import time

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.dest_address = "google.com"
        self.ping_duration = 180 # seconds
        self.ping_interval = 3 # seconds

        self.central_widget = QPlainTextEdit(self)
        self.setCentralWidget(self.central_widget)

        self.start_button = QPushButton("Start", self)
        self.start_button.move(10, 10)
        self.start_button.clicked.connect(self.start_ping)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.move(100, 10)
        self.stop_button.clicked.connect(self.stop_ping)
        self.stop_button.setDisabled(True)

        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.on_stdout_ready)
        self.process.readyReadStandardError.connect(self.on_stderr_ready)
        self.process.finished.connect(self.on_finished)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.save_output)
        self.is_running = False
        self.output_file = None

    def start_ping(self):
        self.is_running = True
        self.start_button.setDisabled(True)
        self.stop_button.setDisabled(False)
        self.output_file = open("ping_output.txt", "a", encoding="cp866")
        self.write_output("PING {} started at {}\n".format(self.dest_address, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.process.start(f"ping -t {self.dest_address}")
        self.timer.start(self.ping_interval * 1000)

    def stop_ping(self):
        self.is_running = False
        self.start_button.setDisabled(False)
        self.stop_button.setDisabled(True)
        self.process.kill()
        self.timer.stop()
        if self.output_file:
            self.write_output("PING {} stopped at {}\n".format(self.dest_address, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            self.output_file.close()

    def save_output(self):
        if self.output_file and self.process.state() == QProcess.Running:
            cursor = self.central_widget.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.central_widget.setTextCursor(cursor)
            output = self.central_widget.toPlainText()
            self.output_file.write(output)
            self.central_widget.clear()

    def write_output(self, text):
        self.central_widget.appendPlainText(text)

    def on_stdout_ready(self):
        text = self.process.readAllStandardOutput().data().decode("cp866")
        self.write_output(text)

    def on_stderr_ready(self):
        text = self.process.readAllStandardError().data().decode("cp866")
        self.write_output(text)

    def on_finished(self):
        if self.is_running:
            self.write_output("PING {} stopped at {}\n".format(self.dest_address, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            self.start_ping()

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
