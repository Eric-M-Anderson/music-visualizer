# Eric Anderson (100704730)

from tkinter import *
from tkinter.ttk import Progressbar
import time


class Progress:
    def __init__(self):
        self.window = Tk()
        self.window.title('Map Loading')
        self.window.geometry('200x40')
        self.bar = Progressbar(self.window, orient=HORIZONTAL, length=100, mode='determinate')
        self.bar.place(x=40, y=10)
        self.txt = Label(self.window, text='0%')
        self.txt.place(x=150, y=10)

    def bar_update(self, value, total_value):
        self.bar['value'] = round(value/total_value*100, 2)
        time.sleep(0.005)
        self.txt['text'] = self.bar['value'], '%'
        self.window.update()
