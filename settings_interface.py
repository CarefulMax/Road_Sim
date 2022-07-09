import sys
import tkinter as tk
import tkinter.font as tkFont

import info_system
import settings
from debug_logger import Logger
from interface_functions import rcpath
from run_interface import RunWindow
from traffic_sign_setup_interface import TrafficSignSetupWindow


class SettingsWindow:
    # Параметры стилизации
    window_size = '1200x600'
    header_color = '#f1f1f1'
    frames_bg_color = 'white'
    frames_border_color = '#f1f1f1'
    entry_width = 8

    def __init__(self, debug_mode: bool = False):

        # Создание дебаг логгера
        self.logger = Logger(logging=debug_mode)

        # region Создание окна и задание его параметров
        self.logger.log('Идет создание окна')
        self.root = tk.Tk()
        self.root.title('Настройки')
        self.root.geometry(self.window_size)
        self.root.configure(bg='white')
        self.root.resizable(False, False)
        icon_path = rcpath('images/icon/icon.gif')
        img = tk.PhotoImage(file=icon_path)
        self.root.tk.call('wm', 'iconphoto', self.root._w, img)
        # endregion

        # region Установка геометрии окна
        for counter in range(9):
            self.root.columnconfigure(counter, weight=1)
        for counter in range(8):
            self.root.rowconfigure(counter, weight=1)
        # endregion

        # region Задание переменных для отслеживания значений настроек
        self.road_type = tk.StringVar(self.root, name='road_type')
        self.road_type.trace_add('write', self.road_type_changed)
        self.directions = tk.IntVar(self.root, name='directions')
        self.directions.trace_add('write', self.directions_changed)
        self.lanes_left = tk.IntVar(self.root, name='lanes_left')
        self.lanes_left.trace_add('write', self.lanes_changed)
        self.lanes_right = tk.IntVar(self.root, name='lanes_right')
        self.lanes_right.trace_add('write', self.lanes_changed)
        self.traffic_light_phase_len = tk.IntVar(self.root, name='traffic_light_phase_len')
        self.flow_type = tk.StringVar(self.root, name='flow_type')
        self.flow_type.set(settings.default_settings['flow_type'])
        self.flow_type.trace_add('write', self.flow_type_changed)
        self.deterministic_time = tk.IntVar(self.root, name='deterministic_time')
        self.distribution_law = tk.StringVar(self.root, name='distribution')
        self.distribution_law.set(settings.default_settings['distribution_law'])
        self.distribution_law.trace_add('write', self.distribution_changed)
        self.normal_exp = tk.IntVar(self.root, name='normal_exp')
        self.normal_disp = tk.IntVar(self.root, name='normal_disp')
        self.uniform_low = tk.IntVar(self.root, name='uniform_low')
        self.uniform_high = tk.IntVar(self.root, name='uniform_high')
        self.exponential_intensity = tk.DoubleVar(self.root, name='exponential_intensity')
        self.checkbox_var = tk.BooleanVar(self.root, name='checkbox')
        self.speed_type = tk.StringVar(self.root, name='speed_type')
        self.speed_type.set(settings.default_settings['speed_type'])
        self.speed_type.trace_add('write', self.speed_type_changed)
        self.mot_speed = tk.IntVar(self.root, name='mot_speed')
        self.high_speed = tk.IntVar(self.root, name='high_speed')
        self.tun_speed = tk.IntVar(self.root, name='tun_speed')
        self.det_speed = tk.IntVar(self.root, name='det_speed')
        # endregion

        # region Создание элементов экранной формы
        # region Основные элементы
        self.logger.log('Идет создание экранных форм')
        title_font = tkFont.Font(family='Arial', size=24)
        title_label = tk.Label(self.root, text='Настройка параметров модели', font=title_font)
        title_label.configure(bg=self.header_color)
        road_settings_frame = tk.Frame(self.root)
        road_settings_frame.configure(bg=self.frames_bg_color,
                                      highlightthickness=4,
                                      highlightbackground=self.frames_border_color)
        start_simulation_button = tk.Button(self.root, text='Начать симуляцию', command=self.start_simulation)
        dev_info_button = tk.Button(self.root, text='Информация о разработчике',
                                    command=lambda: info_system.show_dev_info(self.root))
        system_info_button = tk.Button(self.root, text='Информация о системе', command=info_system.show_system_info)
        # endregion

        # region Элементы фрейма настройки дороги (Закончен)
        road_type_label = tk.Label(self.root, text='Тип дороги:')
        road_type_menu = tk.OptionMenu(self.root, self.road_type, *settings.road_types_list)
        road_type_menu.configure(height=1, width=self.entry_width)
        self.direction_num_label = tk.Label(self.root, text='Количество направлений:')
        self.direction_num_scale = tk.Scale(self.root, from_=1, to=2, orient=tk.HORIZONTAL,
                                            variable=self.directions)
        self.lanes_left_label = tk.Label(self.root, text='Количество полос\nв направлении влево:')
        self.lanes_left_scale = tk.Scale(self.root, from_=1, to=3, orient=tk.HORIZONTAL,
                                         variable=self.lanes_left)
        self.lanes_right_label = tk.Label(self.root, text='Количество полос\nв направлении вправо:')
        self.lanes_right_scale = tk.Scale(self.root, from_=1, to=3, orient=tk.HORIZONTAL,
                                          variable=self.lanes_right)
        self.traffic_light_phase_len_label = tk.Label(self.root, text='Длительность\nсветофорной фазы:')
        self.traffic_light_phase_len_scale = tk.Scale(self.root, from_=30, to=100, orient=tk.HORIZONTAL,
                                                      variable=self.traffic_light_phase_len)
        self.traffic_sign_button = tk.Button(self.root, text='Установить знак', command=self.set_traffic_light)
        self.traffic_sign_checkbutton = tk.Checkbutton(self.root, name='checkbox', state=tk.DISABLED,
                                                       variable=self.checkbox_var)
        # endregion

        # region Элементы фрейма настройки потока
        flow_settings_frame = tk.Frame(self.root)
        flow_settings_frame.configure(bg=self.frames_bg_color,
                                      highlightthickness=4,
                                      highlightbackground=self.frames_border_color)
        flow_type_label = tk.Label(self.root, text='Тип потока\nпо времени:')
        flow_type_menu = tk.OptionMenu(self.root, self.flow_type, *settings.flow_types_list)
        flow_type_menu.configure(height=1, width=self.entry_width)
        self.deterministic_time_label = tk.Label(self.root, text='Время между автомобилями')
        self.deterministic_time_scale = tk.Scale(self.root, from_=0, to=40, orient=tk.HORIZONTAL,
                                                 variable=self.deterministic_time)
        self.distribution_law_label = tk.Label(self.root, text='Закон распределения:')
        self.distribution_law_menu = tk.OptionMenu(self.root, self.distribution_law, *settings.distributions_list)
        self.distribution_law_menu.configure(height=1, width=self.entry_width)
        self.normal_exp_label = tk.Label(self.root, text='Математическое\nожидание:')
        self.normal_exp_scale = tk.Scale(self.root, from_=10, to=30, orient=tk.HORIZONTAL,
                                         variable=self.normal_exp)
        self.normal_disp_label = tk.Label(self.root, text='Дисперсия:')
        self.normal_disp_scale = tk.Scale(self.root, from_=5, to=10, orient=tk.HORIZONTAL,
                                          variable=self.normal_disp)
        self.uniform_low_label = tk.Label(self.root, text='Нижняя граница:')
        self.uniform_low_scale = tk.Scale(self.root, from_=10, to=20, orient=tk.HORIZONTAL,
                                          variable=self.uniform_low)
        self.uniform_high_label = tk.Label(self.root, text='Верхняя граница:')
        self.uniform_high_scale = tk.Scale(self.root, from_=20, to=30, orient=tk.HORIZONTAL,
                                           variable=self.uniform_high)
        self.exponential_intensity_label = tk.Label(self.root, text='Интенсивность:')
        self.exponential_intensity_scale = tk.Scale(self.root, from_=0.01, to=1, orient=tk.HORIZONTAL,
                                                    variable=self.exponential_intensity, resolution=0.01)
        speed_type_label = tk.Label(self.root, text='Тип потока по\nскорости:')
        speed_type_menu = tk.OptionMenu(self.root, self.speed_type, *settings.speed_types_list)
        self.det_speed_label = tk.Label(self.root, text='Cкорость:')
        self.motorway_speed_scale = tk.Scale(self.root, from_=110, to=129, orient=tk.HORIZONTAL,
                                             variable=self.mot_speed)
        self.highway_speed_scale = tk.Scale(self.root, from_=60, to=79, orient=tk.HORIZONTAL,
                                            variable=self.high_speed)
        self.tunnel_speed_scale = tk.Scale(self.root, from_=40, to=59, orient=tk.HORIZONTAL,
                                           variable=self.tun_speed)
        # endregion
        # endregion

        # region Расположение элементов в окне

        title_label.grid(row=0, column=0, columnspan=9, sticky=tk.N + tk.S + tk.W + tk.E)
        road_settings_frame.grid(row=1, column=0, rowspan=6, columnspan=4, sticky=tk.N + tk.S + tk.W + tk.E, padx=5,
                                 pady=5)
        flow_settings_frame.grid(row=1, column=5, rowspan=6, sticky=tk.N + tk.S + tk.W + tk.E,
                                 columnspan=4, padx=5, pady=5)
        start_simulation_button.grid(row=7, column=0)
        system_info_button.grid(row=7, column=6)
        dev_info_button.grid(row=7, column=7)

        # region Элементы фрейма настройки дороги (Закончен)
        road_type_label.grid(row=1, column=0)
        road_type_menu.grid(row=1, column=1, columnspan=2, sticky=tk.W + tk.E)
        self.direction_num_label.grid(row=2, column=0)
        self.direction_num_scale.grid(row=2, column=1, columnspan=2, sticky=tk.W + tk.E)
        self.lanes_right_label.grid(row=4, column=0)
        self.lanes_right_scale.grid(row=4, column=1, columnspan=2, sticky=tk.W + tk.E)
        self.lanes_left_label.grid(row=3, column=0)
        self.lanes_left_scale.grid(row=3, column=1, columnspan=2, sticky=tk.W + tk.E)
        self.traffic_light_phase_len_label.grid(row=2, column=0)
        self.traffic_light_phase_len_scale.grid(row=2, column=1, columnspan=2, sticky=tk.W + tk.E)
        self.traffic_sign_button.grid(row=5, column=0)
        self.traffic_sign_checkbutton.grid(row=5, column=1)
        # endregion

        # region Элементы фрейма настройки потока
        flow_type_label.grid(row=1, column=5)
        flow_type_menu.grid(row=1, column=6, columnspan=2, sticky=tk.W + tk.E)
        self.deterministic_time_label.grid(row=2, column=5)
        self.deterministic_time_scale.grid(row=2, column=6, columnspan=2, sticky=tk.W + tk.E)
        self.distribution_law_label.grid(row=2, column=5)
        self.distribution_law_menu.grid(row=2, column=6, columnspan=2, sticky=tk.W + tk.E)
        self.normal_exp_label.grid(row=3, column=5)
        self.normal_exp_scale.grid(row=3, column=6, columnspan=2, sticky=tk.W + tk.E)
        self.normal_disp_label.grid(row=4, column=5)
        self.normal_disp_scale.grid(row=4, column=6, columnspan=2, sticky=tk.W + tk.E)
        self.uniform_low_label.grid(row=3, column=5)
        self.uniform_low_scale.grid(row=3, column=6, columnspan=2, sticky=tk.W + tk.E)
        self.uniform_high_label.grid(row=4, column=5)
        self.uniform_high_scale.grid(row=4, column=6, columnspan=2, sticky=tk.W + tk.E)
        self.exponential_intensity_label.grid(row=3, column=5)
        self.exponential_intensity_scale.grid(row=3, column=6, columnspan=2, sticky=tk.W + tk.E)
        speed_type_label.grid(row=5, column=5)
        speed_type_menu.grid(row=5, column=6, columnspan=2, sticky=tk.W + tk.E)
        self.det_speed_label.grid(row=6, column=5)
        self.motorway_speed_scale.grid(row=6, column=6, columnspan=2, sticky=tk.W + tk.E)
        self.highway_speed_scale.grid(row=6, column=6, columnspan=2, sticky=tk.W + tk.E)
        self.tunnel_speed_scale.grid(row=6, column=6, columnspan=2, sticky=tk.W + tk.E)
        # endregion
        # endregion

        # Установка переменным значений по умолчанию
        self.logger.log('Установка значений по умолчанию')
        for key in settings.non_sign_parameters:
            exec('self.' + key + '.set(settings.default_settings[key])')

        # region Скрытие элементов
        self.normal_exp_label.grid_remove()
        self.normal_exp_scale.grid_remove()
        self.normal_disp_label.grid_remove()
        self.normal_disp_scale.grid_remove()
        self.highway_speed_scale.grid_remove()
        self.tunnel_speed_scale.grid_remove()
        # endregion

        # Запуск окна
        self.root.mainloop()

    # region Трейсинг изменения переменных (отвечает за динамическое меню)
    def road_type_changed(self, var, indx, mode):
        settings.reset_sign_parameters()
        self.checkbox_var.set(False)
        try:
            print('remove sign stuff')
            self.traffic_sign_button.grid_remove()
            self.traffic_sign_checkbutton.grid_remove()
            value = self.road_type.get()
            self.logger.log(f'Значение поля {var} - \"{value}\"')
            self.motorway_speed_scale.grid_remove()
            self.highway_speed_scale.grid_remove()
            self.tunnel_speed_scale.grid_remove()
            if value == 'Автострада':
                settings.road_settings['lane_width'] = 50
                self.traffic_sign_button.grid_forget()
                self.traffic_sign_checkbutton.grid_forget()
                self.traffic_light_phase_len_label.grid_remove()
                self.traffic_light_phase_len_scale.grid_remove()
                self.direction_num_label.grid()
                self.direction_num_scale.grid()
                if self.speed_type.get() == 'Детерминированный':
                    self.motorway_speed_scale.grid()
                self.logger.log('Следующее обновление directions вызвано для обновления меню')
                self.directions_changed('directions', 0, 0)
            elif value == 'Шоссе':
                settings.road_settings['lane_width'] = 50
                self.traffic_light_phase_len_label.grid_remove()
                self.traffic_light_phase_len_scale.grid_remove()
                self.traffic_sign_button.grid()
                self.traffic_sign_checkbutton.grid()
                self.direction_num_label.grid()
                self.direction_num_scale.grid()
                if self.speed_type.get() == 'Детерминированный':
                    self.highway_speed_scale.grid()
                self.logger.log('Следующее обновление directions вызвано для обновления меню')
                self.directions_changed('directions', 0, 0)
            elif value == 'Тоннель':
                settings.road_settings['lane_width'] = 30
                self.direction_num_label.grid_remove()
                self.direction_num_scale.grid_remove()
                self.lanes_left_label.grid_remove()
                self.lanes_left_scale.grid_remove()
                self.lanes_right_label.grid_remove()
                self.lanes_right_scale.grid_remove()
                self.traffic_light_phase_len_label.grid()
                self.traffic_light_phase_len_scale.grid()
                if self.speed_type.get() == 'Детерминированный':
                    self.tunnel_speed_scale.grid()
        except:
            self.logger.log('Функция road_type_changed не выполнилась из-за ошибки:')
            self.logger.log(sys.exc_info()[1])

    def flow_type_changed(self, var, indx, mode):
        try:
            value = self.flow_type.get()
            self.logger.log(f'Значение поля {var} - \"{value}\"')
            if value == 'Детерминированный':
                self.distribution_law_label.grid_remove()
                self.distribution_law_menu.grid_remove()
                self.normal_exp_label.grid_remove()
                self.normal_exp_scale.grid_remove()
                self.normal_disp_label.grid_remove()
                self.normal_disp_scale.grid_remove()
                self.uniform_low_label.grid_remove()
                self.uniform_low_scale.grid_remove()
                self.uniform_high_label.grid_remove()
                self.uniform_high_scale.grid_remove()
                self.exponential_intensity_label.grid_remove()
                self.exponential_intensity_scale.grid_remove()
                self.deterministic_time_label.grid()
                self.deterministic_time_scale.grid()
            elif value == 'Случайный':
                self.deterministic_time_label.grid_remove()
                self.deterministic_time_scale.grid_remove()
                self.distribution_law_label.grid()
                self.distribution_law_menu.grid()
                self.logger.log('Следующее обновление distribution вызвано для обновления меню')
                self.distribution_changed('distribution', 0, 0)
        except:
            self.logger.log('Функция flow_type_changed не выполнилась из-за ошибки:')
            self.logger.log(sys.exc_info()[1])

    def directions_changed(self, var, indx, mode):
        settings.reset_sign_parameters()
        self.checkbox_var.set(False)
        try:
            value = self.directions.get()
            self.logger.log(f'Значение поля {var} - \"{value}\"')
            if value == 1:
                self.lanes_left_label.grid()
                self.lanes_left_scale.grid()
                self.lanes_left_label.configure(text='Количество полос:')
                self.lanes_right_label.grid_remove()
                self.lanes_right_scale.grid_remove()
            elif value == 2:
                self.lanes_left_label.configure(text='Количество полос\nв направлении влево:')
                self.lanes_left_label.grid()
                self.lanes_left_scale.grid()
                self.lanes_right_label.grid()
                self.lanes_right_scale.grid()
        except:
            self.logger.log('Функция directions_changed не выполнилась из-за ошибки:')
            self.logger.log(sys.exc_info()[1])

    def distribution_changed(self, var, indx, mode):
        try:
            value = self.distribution_law.get()
            self.logger.log(f'Значение поля {var} - \"{value}\"')
            if value == 'Нормальный':
                self.normal_exp_label.grid()
                self.normal_exp_scale.grid()
                self.normal_disp_label.grid()
                self.normal_disp_scale.grid()
                self.uniform_low_label.grid_remove()
                self.uniform_low_scale.grid_remove()
                self.uniform_high_label.grid_remove()
                self.uniform_high_scale.grid_remove()
                self.exponential_intensity_label.grid_remove()
                self.exponential_intensity_scale.grid_remove()
            elif value == 'Равномерный':
                self.normal_exp_label.grid_remove()
                self.normal_exp_scale.grid_remove()
                self.normal_disp_label.grid_remove()
                self.normal_disp_scale.grid_remove()
                self.uniform_low_label.grid()
                self.uniform_low_scale.grid()
                self.uniform_high_label.grid()
                self.uniform_high_scale.grid()
                self.exponential_intensity_label.grid_remove()
                self.exponential_intensity_scale.grid_remove()
            elif value == 'Экспоненциальный':
                self.normal_exp_label.grid_remove()
                self.normal_exp_scale.grid_remove()
                self.normal_disp_label.grid_remove()
                self.normal_disp_scale.grid_remove()
                self.uniform_low_label.grid_remove()
                self.uniform_low_scale.grid_remove()
                self.uniform_high_label.grid_remove()
                self.uniform_high_scale.grid_remove()
                self.exponential_intensity_label.grid()
                self.exponential_intensity_scale.grid()
        except:
            self.logger.log('Функция distribution_changed не выполнилась из-за ошибки:')
            self.logger.log(sys.exc_info()[0])

    def speed_type_changed(self, var, indx, mode):
        try:
            value = self.speed_type.get()
            self.logger.log(f'Значение поля {var} - \"{value}\"')
            if value == 'Детерминированный':
                road_type = self.road_type.get()
                self.det_speed_label.grid()
                if road_type == 'Автострада':
                    self.motorway_speed_scale.grid()
                elif road_type == 'Шоссе':
                    self.highway_speed_scale.grid()
                elif road_type == 'Тоннель':
                    self.tunnel_speed_scale.grid()
            elif value == 'Случайный':
                self.det_speed_label.grid_remove()
                self.motorway_speed_scale.grid_remove()
                self.highway_speed_scale.grid_remove()
                self.tunnel_speed_scale.grid_remove()
        except:
            self.logger.log('Функция distribution_changed не выполнилась из-за ошибки:')
            self.logger.log(sys.exc_info()[0])

    def lanes_changed(self, var, indx, mode):
        settings.reset_sign_parameters()
        self.checkbox_var.set(False)

    # endregion

    def set_traffic_light(self):
        self.logger.log('Переход к окну установки знака')
        self.root.withdraw()
        self.update_settings()
        TrafficSignSetupWindow(self.root, debug_mode=self.logger.is_on())

    def update_settings(self):
        self.logger.log('Идет сохранение настроек')
        if self.road_type.get() == 'Автострада':
            self.det_speed = self.mot_speed
        elif self.road_type.get() == 'Шоссе':
            self.det_speed = self.high_speed
        elif self.road_type.get() == 'Тоннель':
            self.det_speed = self.tun_speed
        for key in settings.non_sign_parameters:
            exec('settings.model_settings[key] = self.' + key + '.get()')
        for k, v in settings.model_settings.items():
            self.logger.log(f'{k} - {v}')

    def start_simulation(self):
        self.logger.log('Начинается симуляция')
        self.root.withdraw()
        self.update_settings()
        RunWindow(self.root, debug_mode=self.logger.is_on())
        pass


if __name__ == '__main__':
    settings_window = SettingsWindow(debug_mode=True)
