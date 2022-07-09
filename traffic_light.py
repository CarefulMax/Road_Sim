import settings
from tkinter import Canvas
from car import Car


class TrafficLight:
    left: bool
    green: bool
    green_left: int
    road: Canvas
    car: Car
    x: int

    def __init__(self, left: bool, road: Canvas, canvas_light, canvas_text, x):
        self.left = left
        self.x = x
        if self.left:
            self.car = Car(0, True, 1, 0, None, 0, self.x)
        else:
            self.car = Car(0, False, 1, 0, None, 0, self.x)
        self.road = road
        self.canvas_light = canvas_light
        self.canvas_text = canvas_text
        self.set_red()

    def subtract_green_time(self, value):
        if self.green_left > 0:
            self.green_left -= value
            if self.green_left <= 0:
                self.set_red()
            self.update_text()

    def is_green(self):
        return self.green

    def get_car(self):
        return self.car

    def set_green(self):
        self.green = True
        self.green_left = settings.model_settings['traffic_light_phase_len'] * 1000
        self.road.itemconfigure(self.canvas_light, fill='lightgreen')
        self.update_text()

    def set_red(self):
        self.green = False
        self.green_left = ''
        self.road.itemconfigure(self.canvas_light, fill='red')
        self.update_text()

    def update_text(self):
        if self.green_left == '':
            self.road.itemconfigure(self.canvas_text, text='')
        else:
            self.road.itemconfigure(self.canvas_text, text=int(self.green_left / 1000))
