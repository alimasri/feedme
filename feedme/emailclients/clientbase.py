from abc import ABC, abstractmethod


class EmailClient(ABC):

    @abstractmethod
    def create_message(self, sender, to, subject, message_text):
        pass

    @abstractmethod
    def send_message(self, message):
        pass
