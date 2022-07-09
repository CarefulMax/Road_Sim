import tkinter as tk
import tkinter.font as tkFont


class DevsWindow:
    # Параметры стилизации
    window_size = '650x350'
    header_color = '#f1f1f1'
    frames_bg_color = 'white'
    frames_border_color = '#f1f1f1'
    dev_info = 'Самарский университет\n' \
               'Кафедра программных систем\n\n' \
               'Курсовой проект по дисциплине Программная инженерия\n\n' \
               'Тема проекта: "Система моделирования движения\n' \
               'транспорта на автодороге"\n\n' \
               'Разработчики:\n' \
               'Студент группы 6414-020302D Кирюшкин Максим Андреевич\n' \
               'Студент группы 6414-020302D Ахмадиев Ильдар Рафаэлевич\n\n' \
               'Самара 2022'

    def __init__(self, settings_window: tk.Tk):
        self.settings_window = settings_window

        # region Создание окна и задание его параметров
        self.root = tk.Toplevel()
        self.root.title('Разработчики')
        self.root.geometry(self.window_size)
        self.root.configure(bg='white')
        self.root.resizable(False, False)
        # endregion

        # region Установка геометрии окна
        for counter in range(6):
            self.root.columnconfigure(counter, weight=1)
        for counter in range(10):
            self.root.rowconfigure(counter, weight=1)
        # endregion

        # region Создание элементов экранной формы
        info_font = tkFont.Font(family='Arial', size=20)
        info_label = tk.Label(self.root, text=self.dev_info, font=info_font)
        # endregion

        # region Расположение элементов в окне
        info_label.grid(row=1, column=0, columnspan=6, rowspan=5)
        # endregion

        self.root.protocol('WM_DELETE_WINDOW', self.on_closing)

        self.root.mainloop()

    def on_closing(self):
        self.settings_window.deiconify()
        self.root.destroy()
        del self
