import random
import tkinter as tk
import tkinter.font as tkFont
from operator import attrgetter
from random import choice
from tkinter import Canvas, Label

from PIL import Image, ImageTk

import settings
from car import Car
from car_timer import CarTimer
from interface_functions import rcpath
from traffic_light import TrafficLight


class Traffic:
    """Класс транспортного потока. Отвечает за создание автомобилей и их взаимодействие"""
    headcar_mode = settings.debug_settings['headcar_mode']
    stop_mode = settings.debug_settings['stop_mode']
    all_lanes_spawn_mode = settings.debug_settings['all_lanes_spawn_mode']
    speed_difference_to_change = 8

    def __init__(self, road: Canvas, time_label: Label, update_ms: int,
                 left_traffic_light=None, right_traffic_light=None):
        """Конструктор объекта транспортного потока

        Args:
              road: Элемент экранной формы, на котором находится дорога
        """
        self.road = road
        self.time_label = time_label
        self.update_ms = update_ms
        self.road_type = settings.model_settings['road_type']
        self.lane_width = settings.road_settings['lane_width']
        self.car_l = (self.lane_width - 6) * 2
        self.cars = []
        self.texts = []
        self.label_font = tkFont.Font(family='Arial', size=int(self.lane_width / 2))
        self.textures_left = []
        self.textures_right = []
        self.timer = CarTimer()
        self.time_before_next_car = self.timer.next() * 1000
        self.sign_placed: bool = False
        self.sign_left: bool = True
        self.sign_x: int
        self.sign_value: int
        if settings.model_settings["sign_placed"]:
            self.sign_placed = True
            self.sign_x = settings.model_settings["sign_x"]
            self.sign_value = settings.model_settings["sign_value"]
            if settings.model_settings["sign_y"] > 300:
                self.sign_left = False

        # region Создание массива текстур
        for i in range(6):
            car_image_l = Image.open(rcpath(f'images/car/l/{i}.png'))
            car_image_l = car_image_l.resize(((self.lane_width - 6) * 2, self.lane_width - 6), Image.ANTIALIAS)
            car_image_l = ImageTk.PhotoImage(car_image_l)
            self.textures_left.append(car_image_l)
            car_image_r = Image.open(rcpath(f'images/car/r/{i}.png'))
            car_image_r = car_image_r.resize(((self.lane_width - 6) * 2, self.lane_width - 6), Image.ANTIALIAS)
            car_image_r = ImageTk.PhotoImage(car_image_r)
            self.textures_right.append(car_image_r)
        stop_img = Image.open(rcpath(f'images/stop.png'))
        stop_img = stop_img.resize(((self.lane_width - 6) * 2, self.lane_width - 6), Image.ANTIALIAS)
        self.stop_img = ImageTk.PhotoImage(stop_img)
        # endregion

        self.time_scale = 1
        self.head_car = None
        self.head_index = -1
        self.speed_coefficient = self.lane_width / 324  # для 30fps, для 60fps - 648
        self.light_applies = self.road_type == 'Тоннель'
        if self.light_applies:
            self.traffic_light_left: TrafficLight = left_traffic_light
            self.traffic_light_right: TrafficLight = right_traffic_light
            self.traffic_light_left.set_green()
            self.last_light_was_left = True

        # region Установка скоростного режима
        if self.road_type == 'Автострада':
            self.speed_low = 110  # 110
            self.speed_high = 129  # 129
        elif self.road_type == 'Шоссе':
            self.speed_low = 60  # 60
            self.speed_high = 79  # 79
        elif self.road_type == 'Тоннель':
            self.speed_low = 40
            self.speed_high = 59
        # endregion

    def add_car(self, speed: int = -1, x: int = -1):
        """Добавляет автомобиль.

        Args:
            speed (int): Скорость создаваемого автомобиля. Параметр нужен для тествовых прогонов модели
            :param x:
        """
        left, lane = self.find_lane()
        if lane == 0:
            return
        if left:
            texture = choice(self.textures_left)
        else:
            texture = choice(self.textures_right)
        if speed == -1:
            if settings.model_settings['speed_type'] == 'Детерминированный':
                speed = settings.model_settings['det_speed']
            else:
                speed = choice(range(self.speed_low, self.speed_high))
        car = Car(speed, left, lane, self.speed_high, texture, self.speed_coefficient, x)
        car_on_canvas = self.road.create_image(car.get_x(), car.get_y(), anchor=tk.N + tk.W, image=car.get_texture())
        text_on_canvas = self.road.create_text(car.get_x() - int(self.lane_width / 2), car.get_y(),
                                               text=car.get_abs_speed(), font=self.label_font, fill='white')
        if self.road_type == 'Тоннель' or self.headcar_mode:
            self.road.tag_bind(car_on_canvas, '<Button-1>', self.set_head_car)
        car.set_canvas_element(car_on_canvas)
        car.set_canvas_text(text_on_canvas)
        self.cars.append(car)
        self.texts.append(text_on_canvas)

    def fill_tunnel_with_ghost_cars(self):
        self.add_ghost_car(0, False, 1, 0)
        self.add_ghost_car(0, False, 1, 100)
        self.add_ghost_car(0, False, 1, 230)
        self.add_ghost_car(0, False, 1, 1200)
        self.add_ghost_car(0, False, 1, 1300)
        self.add_ghost_car(0, False, 1, 1400)
        self.add_ghost_car(0, False, 1, 1500)
        self.add_ghost_car(0, True, 2, 0)
        self.add_ghost_car(0, True, 2, 100)
        self.add_ghost_car(0, True, 2, 230)
        self.add_ghost_car(0, True, 2, 1200)
        self.add_ghost_car(0, True, 2, 1300)
        self.add_ghost_car(0, True, 2, 1400)
        self.add_ghost_car(0, True, 2, 1500)

    def add_ghost_car(self, speed: int, left: bool, lane: int, x: int):
        car = Car(speed, left, lane, 0, self.stop_img, self.speed_coefficient, x=x)
        self.cars.append(car)
        self.texts.append('')

    def find_lane(self):
        """Находит линии доступные для появления нового автомобиля и делает случайный выбор из них

        Returns:
            left (bool): True если свободная полоса в направлении влево, False - если вправо
            lane (int): Номер полосы в направлении.
            Нумерация полос начинается с 1, если свободных полос не найдено - возвращается lane = 0
        """
        free_lanes = []
        for lane in range(1, settings.model_settings['lanes_left'] + 1):
            cars = [car.x for car in self.cars if car.left and (car.lane == lane)]
            if len(cars) == 0:
                free_lanes.append(f'L{lane}')
                continue
            closest_x = max(cars)
            if (1500 - closest_x) >= (self.lane_width - 6) * 4:
                free_lanes.append(f'L{lane}')
        if settings.model_settings['directions'] == 2:
            for lane in range(1, settings.model_settings['lanes_right'] + 1):
                cars = [car.x for car in self.cars if not car.left and (car.lane == lane)]
                if len(cars) == 0:
                    free_lanes.append(f'R{lane}')
                    continue
                closest_x = min(cars)
                if closest_x >= (self.lane_width - 6) * 2:
                    free_lanes.append(f'R{lane}')
        if len(free_lanes) == 0:
            return False, 0
        else:
            place = random.choice(free_lanes)
            lane = int(place[1])
            if place[0] == 'L':
                return True, lane
            else:
                return False, lane

    def update_text(self, car):
        self.road.itemconfigure(car.get_canvas_text(), text=int(car.get_abs_speed()))

    def update(self):
        """Обновление машин в потоке. Происходит 30 раз в секунду"""
        if self.time_scale == 0:
            return
        # region Обновление сфетофора
        if self.light_applies:
            if self.traffic_light_left.is_green():
                self.traffic_light_left.subtract_green_time(self.update_ms * self.time_scale)
            elif self.traffic_light_right.is_green():
                self.traffic_light_right.subtract_green_time(self.update_ms * self.time_scale)
            elif self.tunnel_is_free():
                if self.last_light_was_left:
                    self.traffic_light_right.set_green()
                    self.last_light_was_left = False
                else:
                    self.traffic_light_left.set_green()
                    self.last_light_was_left = True
        # endregion

        to_delete = []
        self.time_before_next_car -= self.update_ms * self.time_scale
        if self.time_before_next_car <= 0:
            if self.all_lanes_spawn_mode:
                for j in range(6):
                    self.add_car()
            else:
                self.add_car()
            self.time_before_next_car = self.timer.next() * 1000
        label_time = round(self.time_before_next_car/1000, 3)
        self.time_label.configure(text=label_time)
        indexes = list(range(len(self.cars)))
        random.shuffle(indexes)

        for i in indexes:
            current_car: Car = self.cars[i]

            # Стоящие автомобили не ускоряются в стоп-режиме
            if self.stop_mode and current_car.speed == 0:
                continue

            # Если головной автомобиль стоит
            if current_car.is_head and current_car.get_abs_speed() == 0:
                continue

            # Если машина перестраивается с маленькой скоростью
            if current_car.is_changing and current_car.get_abs_speed() <= 10:
                current_car.add_speed(10)
                self.update_text(current_car)
            # Если установлен знак
            if self.sign_placed:
                sign_applies = current_car.left == self.sign_left
                if sign_applies:
                    if current_car.left:
                        sign_applies = current_car.get_x() - self.sign_x <= self.car_l * 2
                    else:
                        sign_applies = self.sign_x - current_car.get_x() <= self.car_l * 2
                    if sign_applies:
                        current_car.set_max_speed(self.sign_value)
                    else:
                        current_car.set_max_speed(self.speed_high)

            # region Вычисление других машин на полосе и следующей машины
            # Машины на полосе
            lane_cars = [car for car in self.cars if (car.left == current_car.left and
                         car.lane == current_car.lane)]
            # Следующие машины на полосе
            next_cars = [car for car in lane_cars if car.get_path_x() > current_car.get_path_x()]
            # Следующая машина на полосе
            if len(next_cars) > 0:
                if current_car.left:
                    next_car = max(next_cars, key=attrgetter('x'))
                else:
                    next_car = min(next_cars, key=attrgetter('x'))
            else:
                next_car = Car(-1, True, -1, 0, None, 0)
            if current_car.lane == 2 and next_car.lane != -1:
                pass
            # endregion

            # Обработка остановки на светофоре
            if self.light_applies:
                if current_car.left:
                    # Светофор красный, впереди машин нет либо
                    # следующая машина на полосе дальше светофора
                    if not self.traffic_light_left.is_green() and \
                            (next_car.lane == -1 or next_car.get_x() <= self.traffic_light_left.x - 15) and \
                            current_car.get_x() >= self.traffic_light_left.x:
                        current_car.update_speed(self.traffic_light_left.get_car(), min_dist_multiplier=0.2)
                        self.update_text(current_car)
                        continue
                else:
                    # Светофор красный, впереди машин нет либо
                    # следующая машина на полосе дальше светофора
                    if not self.traffic_light_right.is_green() and \
                            (next_car.lane == -1 or next_car.get_x() >= self.traffic_light_right.x) and \
                            current_car.get_x() < self.traffic_light_right.x - 40:
                        if current_car.lane == 2:
                            pass
                        current_car.update_speed(self.traffic_light_right.get_car(), min_dist_multiplier=0.75)
                        self.update_text(current_car)
                        continue

            # Если неголовной автомобиль едет медленнее минимальной скорости
            # и медленнее своей максимальной (проверка для знака) - прибавить скорость
            if 0 < current_car.get_abs_speed() < self.speed_low and \
                    current_car.get_abs_speed() < current_car.max_speed and \
                    not current_car.is_head:
                current_car.add_speed(1, self.time_scale)
            # Если автомобиль едет быстрее своей максимальной скорости - сбавить скорость
            if current_car.get_abs_speed() > current_car.max_speed:
                current_car.add_speed(-1, self.time_scale)

            # Если впереди нет машин:
            # Если машина стоит - прибавить скорость
            # В любом случае закончить определение скорости
            if next_car.lane == -1:
                if current_car.get_abs_speed() == 0:
                    current_car.add_speed(1, self.time_scale)
                self.update_text(current_car)
                continue
            # Обработка взаимодействия с машиной впереди
            else:
                distance = abs(next_car.get_x() - current_car.get_x())

                # Если машина стоит и рядом нет машины - прибавить
                if current_car.get_abs_speed() == 0 and distance >= self.car_l * 2:
                    current_car.add_speed(1, self.time_scale)

                # Если машина стоит близко впереди или движется медленнее -
                # делается проверка на смену полосы
                speed_check = (current_car.get_abs_speed() - next_car.get_abs_speed() > 8) or \
                              (next_car.get_abs_speed() < self.speed_low)
                distance_check = distance <= self.car_l * 4 and \
                                 (distance >= self.car_l * 3 or current_car.get_abs_speed() < self.speed_low)
                if speed_check and distance_check and not current_car.is_head:
                    can_change_down, can_change_up = self.check_lanes(self.cars[i])
                    possible_changes = []
                    if can_change_down:
                        possible_changes.append(self.cars[i].lane + 1)
                    if can_change_up:
                        possible_changes.append(self.cars[i].lane - 1)
                    if len(possible_changes) > 0:
                        change = random.choice(possible_changes)
                        result: bool = False
                        if current_car.get_abs_speed() < self.speed_low and \
                                current_car.get_abs_speed() < current_car.max_speed:
                            result = current_car.change_lane(change, add_speed=10, time_scale=self.time_scale)
                        else:
                            result = current_car.change_lane(change, time_scale=self.time_scale)
                        self.update_text(self.cars[i])
                        if result:
                            continue
                # Если впереди машина
                speed_check = next_car.get_abs_speed() <= current_car.get_abs_speed()
                distance_check = distance <= self.car_l * 8
                if speed_check and distance_check:
                    if current_car.lane == 2:
                        pass
                    current_car.update_speed(next_car, time_scale=self.time_scale)
            self.update_text(current_car)

        # region Перемещение автомобилей
        for i in range(len(self.cars)):
            movement_xy = self.cars[i].move(time_scale=self.time_scale)
            self.road.move(self.cars[i].canvas_element, movement_xy[0], movement_xy[1])
            self.road.move(self.texts[i], movement_xy[0], movement_xy[1])
            if self.cars[i].x < -100:  # Ушедшие за край автомобили добавляются в список на удаление
                to_delete.append(i)
            elif self.cars[i].x > 1520:
                to_delete.append(i)
        # endregion

        for i in range(len(to_delete)):  # Удаление автомобилей уехавших за край canvas
            removing_head = False
            index = to_delete[i]
            if self.head_car is not None:
                if self.cars[index] == self.head_car:
                    removing_head = True
            self.road.delete(self.cars[index].canvas_element)
            self.road.delete(self.texts[index])
            del self.texts[index]
            del self.cars[index]
            to_delete = [val - 1 for val in to_delete]
            if removing_head:
                self.head_car = None

    def check_lanes(self, car: object) -> (bool, bool):
        """Проверяет возможность перестроиться на полосу вверх или вниз

        Args:
            car (Car): Машина которая собирается перестроиться

        Returns:
            (bool, bool): Можно ли перестроиться вниз, можно ли перестроиться вверх
        """
        return self.check_lane(car, car.lane + 1), self.check_lane(car, car.lane - 1)

    def check_lane(self, car: object, new_lane: int) -> bool:
        """Проверяет доступность полосы для перестраивания

        Args:
            car (Car): Автомобиль, который собирается перестроиться
            new_lane (int): Номер полосы, в которую планируется перестроиться

        Returns:
            bool: True если можно перестроиться, False если нет
        """
        if car.left:  # Проверка, не выходит ли номер полосы за допустимые значения
            lanes_left = settings.model_settings['lanes_left']
            if new_lane not in range(1, lanes_left + 1):
                return False
        else:
            lanes_right = settings.model_settings['lanes_right']
            if new_lane not in range(1, lanes_right + 1):
                return False
        # Координаты всех машин на полосе
        lane_cars = [car_ for car_ in self.cars if (car_.left == car.left) and (car_.lane == new_lane)]
        # Машины, находящиеся в опасной близости
        # Стоящие машины
        possible_collisions = [car_.x for car_ in lane_cars if car_.speed == 0 and car_.get_x()
                               in range(int(car.get_x() - (self.lane_width - 6) * 4),
                                        int(car.get_x() + (self.lane_width - 6) * 4))]
        # Движущиеся машины на более длинном промежутке
        possible_collisions.extend([car_.x for car_ in lane_cars if car_.speed != 0 and car_.get_x()
                                    in range(int(car.get_x() - (self.lane_width - 6) * 8),
                                             int(car.get_x() + (self.lane_width - 6) * 8))])
        return len(possible_collisions) == 0

    def tunnel_is_free(self):
        tunnel_cars = [car for car in self.cars if (self.traffic_light_right.x - 40 < car.get_x()
                                                    < self.traffic_light_left.x)]
        return len(tunnel_cars) == 0

    def set_head_car(self, e):
        click_x = e.x
        click_y = e.y
        heads = [car.is_head for car in self.cars]
        if self.head_car is not None:
            self.head_car.is_head = False
            self.road.itemconfigure(self.head_car.get_canvas_text(), fill='white')
        clicked_canvas_element = e.widget.find_closest(e.x, e.y)[0]
        new_head_car = [car for car in self.cars if car.get_canvas_element() == clicked_canvas_element][0]
        new_head_car.is_head = True
        self.head_car = new_head_car
        self.road.itemconfigure(new_head_car.get_canvas_text(), fill='red')

    def key_press(self, e):
        if self.head_car is None:
            return
        if self.head_car.is_changing:
            return
        key_pressed = e.keysym
        if key_pressed == 'Right':
            if self.head_car.left:
                self.head_car.slower(time_scale=self.time_scale)
            else:
                self.head_car.faster(time_scale=self.time_scale)
        elif key_pressed == 'Left':
            if self.head_car.left:
                self.head_car.faster(time_scale=self.time_scale)
            else:
                self.head_car.slower(time_scale=self.time_scale)
        self.update_text(self.head_car)
