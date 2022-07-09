from datetime import datetime


class Logger:
    def __init__(self, logging: bool = True):
        self.__is_on = logging

    def is_on(self) -> bool:
        return self.__is_on

    def log(self, text: str = 'Логгер вызван, но сообщение не передано'):
        if self.is_on():
            print(f'[{datetime.now()}]: {text}')
