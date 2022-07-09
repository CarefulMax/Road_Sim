import tkinter as tk
import tkinter.font as tkFont
from debug_logger import Logger
from interface_functions import rcpath
import settings

from PIL import Image, ImageTk


class TrafficSignSetupWindow:
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
        self.root.title('Установка светофора')
        self.root.geometry(self.window_size)
        self.root.configure(bg='white')
        self.root.resizable(False, False)
        # endregion

        # region Установка геометрии окна
        for counter in range(6):
            self.root.columnconfigure(counter, weight=1)
        for counter in range(6):
            self.root.rowconfigure(counter, weight=1)
        # endregion

        # region Задание переменных знака
        self.sign_placed: bool = settings.default_settings['sign_placed']
        self.sign_direction: int = settings.default_settings['sign_direction']
        self.sign_x = settings.default_settings['sign_x']
        self.sign_y = settings.default_settings['sign_y']
        self.sign_value = tk.IntVar(self.root, name='sign_value')
        self.sign_value.set(settings.default_settings['sign_value'])
        self.sign_value.trace_add('write', self.value_changed)
        # endregion

        # region Создание элементов экранной формы
        self.logger.log('Идет создание экранных форм')
        title_font = tkFont.Font(family='Arial', size=24)
        title_label = tk.Label(self.root, text='Установка дорожного знака', font=title_font)
        title_label.configure(height=1, bg=self.header_color)
        self.road_canvas = tk.Canvas(self.root, height=600, width=1500, bg=self.grass_color)
        value_label = tk.Label(self.root, text='Ограничение:')
        value_menu = tk.OptionMenu(self.root, self.sign_value, *settings.sign_values_list)
        value_menu.configure(height=1, width=self.entry_width)
        cancel_button = tk.Button(self.root, text='Отмена', command=self.cancel)
        self.submit_button = tk.Button(self.root, text='Установить', command=self.submit, state=tk.DISABLED)
        # endregion

        # region Расположение элементов в окне
        title_label.grid(row=0, column=0, columnspan=12, sticky=tk.N + tk.S + tk.W + tk.E)
        self.road_canvas.grid(row=1, column=0, columnspan=10)
        value_label.grid(row=2, column=0, sticky=tk.E)
        value_menu.grid(row=2, column=1, sticky=tk.W)
        cancel_button.grid(row=2, column=4)
        self.submit_button.grid(row=2, column=5)
        # endregion

        # region Отрисовка дорожного полотна
        y = 300 - self.total_lanes * (self.lane_width/2)
        self.highest_y = y
        self.lowest_y = y + self.total_lanes * self.lane_width
        self.middle_y = y + self.total_lanes * (self.lane_width/2)
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
            self.middle_y = y
            self.road_canvas.create_line(0, y - 2, 1550, y - 2, fill=self.directions_separator_color)
            self.road_canvas.create_line(0, y + 2, 1550, y + 2, fill=self.directions_separator_color)
            for i in range(settings.model_settings['lanes_right'] - 1):
                self.logger.log(f'Межполосная линия на y={y}')
                y += self.lane_width
                self.road_canvas.create_line(0, y, 1550, y, fill=self.lanes_separator_color, dash=(6, 6))
        self.logger.log(f'highest y - {self.highest_y}')
        self.logger.log(f'middle y - {self.middle_y}')
        self.logger.log(f'lowest y - {self.lowest_y}')
        # endregion

        # Изображение знака
        sign_image = ImageTk.PhotoImage(Image.open(rcpath('images/sign.png')))
        self.sign = self.road_canvas.create_image(self.sign_x, self.sign_y, anchor=tk.N + tk.W, image=sign_image)
        sign_font = tkFont.Font(family='Arial', size=20)
        self.sign_text = self.road_canvas.create_text(self.sign_x + 11, self.sign_y + 11, anchor=tk.N + tk.W,
                                                      text=self.sign_value.get(), font=sign_font)

        self.root.protocol('WM_DELETE_WINDOW', self.on_closing)  # Протокол закрытия окна
        self.road_canvas.bind('<Button-1>', self.canvas_callback)  # Бинд нажатия на canvas

        self.root.mainloop()

    def value_changed(self, var, indx, mode):
        value = self.sign_value.get()
        self.logger.log(f'Значение поля {var} - \"{value}\"')
        self.road_canvas.itemconfigure(self.sign_text, text=value)

    def canvas_callback(self, event):
        click_x = event.x
        click_y = event.y
        placement_x = click_x
        placement_x = min(max(placement_x, 0), 1500-self.sign_size)
        if self.directions == 1:
            placement_y = self.highest_y - self.sign_size
            self.sign_direction = 'Влево'
        else:
            if click_y <= self.middle_y:
                placement_y = self.highest_y - self.sign_size
            else:
                placement_y = self.lowest_y
        self.logger.log(f'Установка знака в точку {placement_x},{placement_y}')
        if not self.sign_placed:
            self.sign_placed = True
            self.submit_button.configure(state=tk.NORMAL)
        move_x = placement_x - self.sign_x
        move_y = placement_y - self.sign_y
        self.road_canvas.move(self.sign, move_x, move_y)
        self.road_canvas.move(self.sign_text, move_x, move_y)
        self.sign_x = placement_x
        self.sign_y = placement_y

    def cancel(self):
        self.logger.log('Отмена установки знака')
        for key in settings.sign_parameters:
            settings.model_settings[key] = settings.default_settings[key]
        self.on_closing()

    def submit(self):
        self.logger.log('Сохранение данных знака')
        for key in settings.sign_parameters:
            exec('settings.model_settings[key] = self.' + key)
        settings.model_settings['sign_value'] = self.sign_value.get()
        self.settings_window.setvar('checkbox', True)
        self.on_closing()

    def on_closing(self):
        self.logger.log('Закрытие окна светофора, возвращение окна настроек')
        self.settings_window.deiconify()
        self.root.destroy()
        del self
