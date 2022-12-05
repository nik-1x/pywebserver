from threading import Thread

class NewTask:

    def __init__(self, function):
        self.function = function
        self.thread = Thread(target=self.cycle, daemon=True)

    def cycle(self):
        while True:
            self.function()

    def start(self):
        self.thread.start()