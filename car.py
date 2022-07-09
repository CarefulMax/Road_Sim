from PIL import Image, ImageTk
import settings


class Car(object):
    x: int
    y: int
    speed: int
    speed_px: float
    speed_y_px: int
    left: bool
    lane: int
    is_changing: bool
    lane_timer: int
    is_head: bool
    max_speed: int
    pixels_skipped: float
    texture: ImageTk.PhotoImage
    _speed_coefficient_: float

    def __init__(self, speed: int, left: bool, lane: int, max_speed: int, texture: Image, speed_coefficient: float, x: int = -1):
        # print('Создание машины')
        self.speed = speed
        self._speed_coefficient_ = speed_coefficient
        self.speed_px = speed * self._speed_coefficient_
        self.speed_y_px = 0
        self.lane_timer = 0
        self.is_changing = False
        self.is_head = False
        self.texture = texture
        self.left = left
        self.lane = lane
        self.canvas_element = None
        self.canvas_text = None
        self.max_speed = max_speed
        self.pixels_skipped = 0
        if self.left:
            self.speed = - self.speed
            self.speed_px = - self.speed_px
            self.x = 1500
            self.y = int(
                settings.road_settings['highest_y'] + settings.road_settings['lane_width'] * (self.lane - 1) + 3)
        else:
            self.x = -(settings.road_settings['lane_width'] - 8) * 2
            self.y = int(
                settings.road_settings['middle_y'] + settings.road_settings['lane_width'] * (self.lane - 1) + 3)
            '''if not self.left and settings.model_settings['road_type'] == 'Тоннель':
                self.y = int(
                    settings.road_settings['highest_y'] + settings.road_settings['lane_width'] * (self.lane - 1) + 3)'''
        if x != -1:
            self.x = x

    def __eq__(self, other):
        return self.get_canvas_element() == other.get_canvas_element()

    def get_x(self):
        return self.x

    def get_path_x(self):
        if self.left:
            return 1500-self.x
        else:
            return self.x

    def get_y(self):
        return self.y

    def get_texture(self):
        return self.texture

    def get_abs_speed(self):
        return abs(self.speed)

    def get_abs_speed_px(self):
        return abs(self.speed_px)

    def get_canvas_element(self):
        return self.canvas_element

    def get_canvas_text(self):
        return self.canvas_text

    def set_max_speed(self, max_speed: int):
        self.max_speed = max_speed

    def set_canvas_element(self, canvas_element):
        self.canvas_element = canvas_element

    def set_canvas_text(self, canvas_text_element):
        self.canvas_text = canvas_text_element

    def move(self, time_scale: int = 1):
        float_move_x = time_scale * self.speed_px
        move_x = int(float_move_x)
        self.pixels_skipped += float_move_x - move_x
        if abs(self.pixels_skipped) > 1:
            move_x += int(self.pixels_skipped)
            if self.left:
                self.pixels_skipped %= -1
            else:
                self.pixels_skipped %= 1
        self.x += move_x
        if self.lane_timer != 0:
            if self.lane_timer > 0:
                self.lane_timer -= 1 * time_scale
                if self.lane_timer <= 0:
                    self.speed_y_px = 0
                    self.is_changing = False
                    self.lane_timer = -150
            else:
                self.lane_timer += 1 * time_scale
        move_y = self.speed_y_px * time_scale
        self.y += move_y
        return move_x, move_y

    def update_speed(self, next_car: object, time_scale: int = 1, min_dist_multiplier: int = 1):
        distance = abs(next_car.get_x() - self.get_x())
        set_speed_distance = (settings.road_settings['lane_width'] - 6) * 3.5 * min_dist_multiplier
        if distance <= set_speed_distance:
            self.speed = next_car.speed
            self.speed_px = self.speed * self._speed_coefficient_
        else:
            if distance < ((settings.road_settings['lane_width'] - 6) * self.get_abs_speed_px()):
                speed_change = int(abs(next_car.speed - self.speed) * 0.1)
            elif distance < ((settings.road_settings['lane_width'] - 6) * 2 * self.get_abs_speed_px()):
                speed_change = int(abs(next_car.speed - self.speed) * 0.07)
            else:
                speed_change = int(abs(next_car.speed - self.speed) * 0.01)
            self.add_speed(-speed_change, time_scale)
            self.speed_px = self.speed * self._speed_coefficient_

    def add_speed(self, speed: int, time_scale: int = 1):
        new_speed = abs(self.speed) + speed * time_scale
        if new_speed < 0:
            new_speed = 0
        if new_speed > self.max_speed and speed > 0:
            new_speed = self.max_speed
        if self.left:
            self.speed = -new_speed
        else:
            self.speed = new_speed
        self.speed_px = self.speed * self._speed_coefficient_

    def change_lane(self, lane, add_speed: int = 0, time_scale: int = 1) -> bool:
        if time_scale == 0.5:
            time_scale = 0.75
        if self.is_changing or self.lane_timer < 0:
            return False
        if lane < self.lane:
            self.speed_y_px = -2 * time_scale
        else:
            self.speed_y_px = 2 * time_scale
        self.is_changing = True
        self.lane = lane
        self.lane_timer = (settings.road_settings['lane_width'] / time_scale + time_scale - 1) / 2
        if add_speed != 0:
            self.add_speed(add_speed, time_scale)
        return True

    def slower(self, time_scale: int = 1):
        if time_scale < 1:
            time_scale = 1
        self.add_speed(-5, time_scale)

    def faster(self, time_scale: int = 1):
        if time_scale < 1:
            time_scale = 1
        self.add_speed(5, time_scale)
