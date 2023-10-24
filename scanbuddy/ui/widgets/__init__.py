import datetime
from textual.widgets import RichLog

class Logger(RichLog):
    def info(self, content, **kwargs):
        now = self.now()
        content = f'{now} - INFO - {content}'
        self.write(content, **kwargs)

    def warning(self, content, **kwargs):
        now = self.now()
        content = f'{now} - WARNING - {content}'
        self.write(content, **kwargs)

    def error(self, content, prefix=True, **kwargs):
        now = self.now()
        if prefix:
            prefix =  f'{now} - ERROR - '
        else:
            prefix = ""
        content = f'{prefix}{content}'
        self.write(content, **kwargs)

    def now(self):
        return datetime.datetime.now().strftime("%b %d, %Y %I:%M %p")
