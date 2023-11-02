from abc import ABCMeta, abstractmethod;

class AbstractStrategy(metaclass=ABCMeta):
    @abstractmethod
    def sellStrategy(self):
        pass;
    
    @abstractmethod
    def buyStrategy(self):
        pass;
    
    @abstractmethod
    def orderCancel(self):
        pass;                