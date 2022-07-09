from random import choice
from numpy.random import normal, exponential

import settings


class CarTimer:
    """Класс реализует вычисление времени до следующего автомобиля в зависимости от настроек модели"""
    time: classmethod

    def __init__(self):
        if settings.model_settings['flow_type'] == 'Детерминированный':
            self.time = self.__get_deterministic_time__
        else:
            if settings.model_settings['distribution_law'] == 'Нормальный':
                self.time = self.__get_normal_time__
            elif settings.model_settings['distribution_law'] == 'Равномерный':
                self.time = self.__get_uniform_time__
                self.range = range(settings.model_settings['uniform_low'], settings.model_settings['uniform_high'] + 1)
            elif settings.model_settings['distribution_law'] == 'Экспоненциальный':
                self.time = self.__get_exponential_time__

    # region Варианты распределения
    @staticmethod
    def __get_deterministic_time__() -> int:
        return int(settings.model_settings['deterministic_time'])

    @staticmethod
    def __get_normal_time__() -> int:
        return abs(int(normal(settings.model_settings['normal_exp'], settings.model_settings['normal_disp'])))

    def __get_uniform_time__(self) -> int:
        return int(choice(self.range))

    @staticmethod
    def __get_exponential_time__() -> int:
        return int(exponential(1 / settings.model_settings['exponential_intensity']))
    # endregion

    def next(self) -> int:
        """Возвращает время до следующего автомобиля"""
        return self.time()
