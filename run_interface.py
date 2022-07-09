import tkinter as tk
import tkinter.font as tkFont
from debug_logger import Logger
from interface_functions import rcpath
import settings
from traffic import Traffic
from traffic_light import TrafficLight
from PIL import Image, ImageTk


class RunWindow:
    # Параметры стилизации
    window_size = '1550x700'
    header_color = '#f1f1f1'
    frames_bg_color = 'white'
    frames_border_color = '#f1f1f1'
    entry_width = 8
    grass_color = 'green'
    road_color = '#505050'
    directions_separator_color = 'yellow'
    lanes_separator_color = 'white'
    lane_width = settings.road_settings['lane_width']
    sign_size = 45

    def __init__(self, settings_window: tk.Tk, debug_mode: bool = False):
        self.logger = Logger(debug_mode)
        self.settings_window = settings_window
        self.update_ms = 33
        self.lane_width = settings.road_settings['lane_width']

        if settings.model_settings['road_type'] == 'Тоннель':
            settings.model_settings['directions'] = 2
            settings.model_settings['lanes_left'] = 1
            settings.model_settings['lanes_right'] = 1
            self.lane_width = 30

        # region Определение общего количества полос
        self.directions = settings.model_settings['directions']
        if self.directions == 1:
            self.total_lanes = settings.model_settings['lanes_left']
        elif self.directions == 2:
            self.total_lanes = settings.model_settings['lanes_left'] + settings.model_settings['lanes_right']
        # endregion

        # region Создание окна и задание его параметров
        self.logger.log('Идет создание окна')
        self.root = tk.Toplevel()
        self.root.title('Симуляция')
        self.root.geometry(self.window_size)
        self.root.configure(bg='white')
        self.root.resizable(False, False)
        # endregion

        # region Установка геометрии окна
        for counter in range(12):
            self.root.columnconfigure(counter, weight=1)
        for counter in range(6):
            self.root.rowconfigure(counter, weight=1)
        # endregion

        self.time_scale = tk.DoubleVar(self.root, name='time_scale')
        self.time_scale.set(1)
        self.time_scale.trace_add('write', self.time_scale_changed)

        # region Создание элементов экранной формы
        self.logger.log('Идет создание экранных форм')
        title_font = tkFont.Font(family='Arial', size=24)
        title_label = tk.Label(self.root, text='Симуляция', font=title_font)
        title_label.configure(height=1, bg=self.header_color)
        time_info_label = tk.Label(self.root, font=tkFont.Font(family='Arial', size=16),
                                   text='Секунд до следующих машин:')
        self.time_label = tk.Label(self.root, font=tkFont.Font(family='Arial', size=18), text='58',
                                   height=1, width=10, anchor='w')
        self.road_canvas = tk.Canvas(self.root, height=600, width=1500, bg=self.grass_color)
        cancel_button = tk.Button(self.root, text='Назад', command=self.on_closing)
        # endregion

        # region Расположение элементов в окне
        title_label.grid(row=0, column=0, columnspan=24, sticky=tk.N + tk.S + tk.W + tk.E)
        self.road_canvas.grid(row=1, column=0, columnspan=10)
        tk.Radiobutton(self.root, text='Пауза', variable=self.time_scale, value=0).grid(row=2, column=0)
        tk.Radiobutton(self.root, text='0.5', variable=self.time_scale, value=0.5).grid(row=2, column=1)
        tk.Radiobutton(self.root, text='1', variable=self.time_scale, value=1).grid(row=2, column=2)
        tk.Radiobutton(self.root, text='2', variable=self.time_scale, value=2).grid(row=2, column=3)
        tk.Radiobutton(self.root, text='3', variable=self.time_scale, value=3).grid(row=2, column=4)
        time_info_label.grid(row=2, column=5, columnspan=2)
        self.time_label.grid(row=2, column=7)
        cancel_button.grid(row=2, column=9)
        # endregion

        # region Отрисовка дорожного полотна
        y = 300 - self.total_lanes * (self.lane_width / 2)
        self.highest_y = y
        self.lowest_y = y + self.total_lanes * self.lane_width
        self.middle_y = y + settings.model_settings['lanes_left'] * self.lane_width
        settings.road_settings['highest_y'] = self.highest_y
        settings.road_settings['middle_y'] = self.middle_y
        settings.road_settings['lowest_y'] = self.lowest_y
        self.road_canvas.create_rectangle(0, y, 1550, y + self.total_lanes * self.lane_width, fill=self.road_color)
        for i in range(settings.model_settings['lanes_left'] - 1):
            self.logger.log(f'Межполосная линия на y={y}')
            y += self.lane_width
            self.road_canvas.create_line(0, y, 1550, y, fill=self.lanes_separator_color, dash=(6, 6))
        if settings.model_settings['directions'] == 2:
            self.logger.log(f'Двойная сплошная линия на y={y}')
            y += self.lane_width
            if settings.model_settings['road_type'] == 'Тоннель':
                self.road_canvas.create_line(0, y - 2, 270, y - 2, fill=self.directions_separator_color)
                self.road_canvas.create_line(0, y + 2, 270, y + 2, fill=self.directions_separator_color)
                self.road_canvas.create_line(270, y, 1230, y, fill=self.lanes_separator_color, dash=(11, 6))
                self.road_canvas.create_line(1230, y - 2, 1550, y - 2, fill=self.directions_separator_color)
                self.road_canvas.create_line(1230, y + 2, 1550, y + 2, fill=self.directions_separator_color)
            else:
                self.road_canvas.create_line(0, y - 2, 1550, y - 2, fill=self.directions_separator_color)
                self.road_canvas.create_line(0, y + 2, 1550, y + 2, fill=self.directions_separator_color)
            for i in range(settings.model_settings['lanes_right'] - 1):
                self.logger.log(f'Межполосная линия на y={y}')
                y += self.lane_width
                self.road_canvas.create_line(0, y, 1650, y, fill=self.lanes_separator_color, dash=(6, 6))
        self.logger.log(f'highest y - {self.highest_y}')
        self.logger.log(f'middle y - {self.middle_y}')
        self.logger.log(f'lowest y - {self.lowest_y}')
        # endregion

        # region Изображение знака
        if settings.model_settings['sign_placed']:
            x = settings.model_settings["sign_x"]
            y = settings.model_settings["sign_y"]
            value = str(settings.model_settings['sign_value'])
            self.logger.log(f'x - {x}, y - {y}, value - {value}')
            sign_image = ImageTk.PhotoImage(Image.open(rcpath('images/sign2.png')))
            self.sign = self.road_canvas.create_image(x, y, anchor=tk.N + tk.W, image=sign_image)
            sign_font = tkFont.Font(family='Arial', size=20)
            self.sign_text = self.road_canvas.create_text(x + 11, y + 11, anchor=tk.N + tk.W, text=value,
                                                          font=sign_font)
        # endregion

        # region Светофоры и стенки тоннеля
        if settings.model_settings['road_type'] == 'Тоннель':
            print('Дорисовка тоннеля')
            # Гора
            self.road_canvas.create_rectangle(270, 0, 1230, 270, fill='gray', outline='gray')
            self.road_canvas.create_rectangle(270, 330, 1230, 650, fill='gray', outline='gray')
            # Корпус светофора
            self.road_canvas.create_rectangle(230, 330, 270, 370, fill='black')
            self.road_canvas.create_rectangle(1230, 230, 1270, 270, fill='black')
            # Разделитель с тоннелем
            self.road_canvas.create_line(270, 270, 270, 330, fill='#969696')
            self.road_canvas.create_line(1230, 270, 1230, 330, fill='#969696')
            # Лампы светофора
            right_light = self.road_canvas.create_rectangle(235, 335, 265, 365, fill='red')
            left_light = self.road_canvas.create_rectangle(1235, 235, 1265, 265, fill='lightgreen')
            right_light_text = self.road_canvas.create_text(250, 350, text='50')
            left_light_text = self.road_canvas.create_text(1250, 250, text='50')
            right_traffic_light = TrafficLight(False, self.road_canvas, right_light, right_light_text, 270)
            left_traffic_light = TrafficLight(True, self.road_canvas, left_light, left_light_text, 1230)
            self.traffic = Traffic(self.road_canvas, self.time_label, self.update_ms,
                                   left_traffic_light, right_traffic_light)
        else:
            self.traffic = Traffic(self.road_canvas, self.time_label, self.update_ms)

        self.root.protocol('WM_DELETE_WINDOW', self.on_closing)  # Протокол закрытия окна
        self.root.bind('<KeyPress>', self.traffic.key_press)
        # endregion

        self.start_simulation()
        self.root.mainloop()

    def time_scale_changed(self, var, indx, mode):
        self.traffic.time_scale = self.time_scale.get()

    def start_simulation(self):
        self.traffic.update()
        self.root.after(self.update_ms, self.start_simulation)

    def on_closing(self):
        self.logger.log('Закрытие окна светофора, возвращение окна настроек')
        self.settings_window.deiconify()
        self.root.destroy()
        del self
