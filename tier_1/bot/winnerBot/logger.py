import datetime

def get_logger():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}.mylog.log"

    def log(message):
        with open(filename, "a", encoding="utf-8") as f:
            f.write(f"{message}\n")
    return log
