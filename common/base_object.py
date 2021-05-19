from settings import Settings


class BaseObject:
    def __init__(self):
        self.config = Settings.get_settings()
