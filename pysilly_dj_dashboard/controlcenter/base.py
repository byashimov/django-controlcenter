from .utils import captitle


class BaseModel:
    title = None

    def __init__(self):
        self.__name__ = self.__class__.__name__
        self.slug = self.__name__.lower()
        if self.title is None:
            self.title = captitle(self.__name__)

    def __str__(self):
        return self.__name__
