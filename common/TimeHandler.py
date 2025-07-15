import time
import datetime

class TimeHandler:
    def time_string_now(self, pattern="%Y-%m-%d %H%M%S"):
        return datetime.datetime.now().strftime(pattern)