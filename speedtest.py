import sys
import time
import requests
import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import QTimer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # set window properties
        self.setWindowTitle("Ping Test")
        self.setGeometry(100, 100, 400, 300)
        self.setFixedSize(400, 300)

        # create labels and line edits for destination address and duration
        self.dest_address_label = QLabel(self)
        self.dest_address_label.setText("Destination Address:")
        self.dest_address_label.move(20, 20)

        self.dest_address_edit = QLineEdit(self)
        self.dest_address_edit.move(150, 20)

        self.duration_label = QLabel(self)
        self.duration_label.setText("Duration (in seconds):")
        self.duration_label.move(20, 60)

        self.duration_edit = QLineEdit(self)
        self.duration_edit.move(150, 60)

        # create a button to start the ping test
        self.start_button = QPushButton(self)
        self.start_button.setText("Start Ping Test")
        self.start_button.move(20, 100)
        self.start_button.clicked.connect(self.start_ping_test)

        # create a label to display the response time
        self.response_label = QLabel(self)
        self.response_label.move(20, 140)

        # create a timer to save the output to a file every 3 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.save_output_to_file)
        self.timer.start(3000)

        # set console encoding to cp866
        sys.stdout.reconfigure(encoding='cp866')

        # initialize output file
        self.output_file = None
        self.output_filename = None

    def start_ping_test(self):
        # get the destination address and duration from the user
        destination_address = self.dest_address_edit.text()
        duration = float(self.duration_edit.text())

        # create output file name based on current timestamp
        self.output_filename = datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".txt"

        # open output file in append mode
        self.output_file = open(self.output_filename, "a", encoding="cp866")

        # ping the website
        response_time = self.ping_website(destination_address, duration)

        # display the response time
        self.response_label.setText("Response time: {:.2f} seconds".format(response_time))

    def ping_website(self, destination_address, duration):
        # start the timer
        start_time = time.time()

        # ping the website
        response = requests.get(destination_address)

        # calculate the response time
        response_time = time.time() - start_time

        # wait for the remaining duration
        time.sleep(duration - response_time)

        # format the current timestamp with milliseconds
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        # write the ping output to the output file
        self.output_file.write("{}\t{}\n".format(current_time, response_time))

        # return the response time
        return response_time

    def save_output_to_file(self):
        # if output file is not None, close it and set it to None
        if self.output_file is not None:
            self.output_file.close()
            self.output_file = None

        # if output file name is not None, reset it to None
        if self.output_filename is not None:
            self.output_filename = None

if __name__ == "__main__":
    # create the application and main window
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()

    # execute the application
    sys.exit(app.exec_())
