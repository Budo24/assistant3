"""
Links:
https://yagisanatode.com/2018/02/24/how-to-center-the-main-window-on-the-screen-in-tkinter-with-python-3/
"""
import math
import queue
import wave
from curses import window
from string import hexdigits
from time import sleep
from tkinter import *

import matplotlib as mpl
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from tomlkit import boolean
import numpy as np

from assistant3 import record


class GUI():
    def __init__(self):
        # initial Graphic settings
        self.window = Tk()
        self.window.title("Welcome to Assistant3")
        # Center Window by getting the requested values of the height and width and make it daynically adjustable to label length
        windowWidth = self.window.winfo_reqwidth()
        windowHeight = self.window.winfo_reqheight()
        # Gets both half the screen width/height and window width/height
        positionRight = int(self.window.winfo_screenwidth()/2 - windowWidth/2)
        positionDown = int(self.window.winfo_screenheight()/2 - windowHeight/2)
        # Positions the window in the center of the page
        self.window.geometry("+{}+{}".format(positionRight, positionDown))
        
        # Label for Text Output
        self.lbl = Label(self.window, font= "Damascus", anchor= CENTER)

        # Canvas for Speech animations
        canvas_width = 200
        canvas_height = 200
        self.myCanvas = Canvas(self.window, width=canvas_width, height=canvas_height)
        self.myCanvas.place(relx=0.5, rely=0.5, anchor=CENTER)
        self.myCanvas.pack()
        # self.myCanvas.grid(row=0, column=0)

        # loading Speech sample for animation in list
        self.speech = True
        self.answer = False
        self.frame = 0
        self.wav_sample = wave.open('./file_example_WAV_1MG.wav', 'r')
        self.frames = 700
        self.waves = []
        for i in range(1, self.frames):
            self.waves.append(int(self.wav_sample.readframes(i)[0]) * 0.23)



    def update_speech(self, text="understood Text..."):
        # text needs to be passed
        if self.speech == True:
            self.myCanvas.delete('all')
            self.text = text
            self.lbl.config(text = self.text, font =("Damascus", 16, "italic"))
            self.show_label()

        else:
            self.lbl.config(self.window, text="Speak...")
            self.lbl.config(text = self.text)
            self.show_label()

        self.window.after(2000, self.update_speech)


    def update_answer(self, text="answered Text..."):
        if self.answer == True:
            self.text = text
            self.lbl.config(text = self.text)
            self.show_label()

        else:
            self.update_speech
        self.window.after(2000, self.update_answer)

    def show_label(self):
        self.lbl.pack()
        # self.lbl.grid()

    def speech_bubble(self, x, y, r, **kwargs):
        'create a circle'
        self.myCanvas.delete('all')
        self.id = self.myCanvas.create_oval(x-r,y-r,x+r,y+r,**kwargs)
        return id

    # Update values
    def update_bubble(self):
        # Update Speech Bubble, speech is bool if usr is speeking, needs to be passed 
        if self.speech == True:
            if self.frame < self.frames - 10:
                self.frame = self.frame + 1
            else:
                self.frame = 1

            self.radius = self.waves[self.frame] if self.waves[self.frame] > 15 else 15
            r = self.radius
            self.speech_bubble(100, 100, r, fill="red", outline="black", width=5)
        else:
            self.speech_bubble(100, 100, 15, fill="black", outline="black", width=3)

        self.window.after(100,self.update_bubble)

    def run(self):
        self.window.after(100, self.update_bubble)
        self.update_speech()
        self.update_answer()
        self.window.mainloop()

gui = GUI()

gui.run()
