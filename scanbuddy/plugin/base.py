import abc

class AbstractPlugin(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, conf, db):
        pass

    @abc.abstractmethod
    def run(self):
        pass

