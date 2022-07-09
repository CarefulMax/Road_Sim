from tkinter import messagebox
from pathlib import Path
from interface_functions import rcpath
import tkinter as tk
from devs_info_interface import DevsWindow
import webbrowser


def show_dev_info(settings_window: tk.Tk):
    settings_window.withdraw()
    DevsWindow(settings_window)


def show_system_info():
    path = Path(rcpath('system_info.html'))
    if not path.is_file():
        messagebox.showerror(title='Ошибка', message='Файл справки не найден')
    else:
        browser = webbrowser.get('chrome')
        browser.open_new_tab('file://' + rcpath('system_info.html'))
