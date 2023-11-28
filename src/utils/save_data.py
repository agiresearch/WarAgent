import os
from datetime import datetime, date

class Logger(object):
    def __init__(self, log_path, on=True):
        self.log_path = log_path
        self.on = on
        if self.on:
            while os.path.isfile(self.log_path):
                self.log_path += "+"

    def log(self, string, newline=True):
        if self.on:
            with open(self.log_path, "a") as logf:
                # today = date.today()
                # today_date = today.strftime("%m/%d/%Y")
                # now = datetime.now()
                # current_time = now.strftime("%H:%M:%S")
                # string = today_date + ", " + current_time + ": " + string
                logf.write(string)
                if newline:
                    logf.write("\n")
    
    def log_board_and_stick(self, board_display, stick_text, agent_name):
        if self.on:
            with open(self.log_path, "a") as logf:
                logf.write("Board for {}\n".format(agent_name))
                logf.write(board_display)
                logf.write("\n")
                logf.write("Stick for {}\n".format(agent_name))
                logf.write(stick_text)
                logf.write("\n")
                logf.write("--------\n")

