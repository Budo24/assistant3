"""
Links:
https://yagisanatode.com/2018/02/24/how-to-center-the-main-window-on-the-screen-in-tkinter-with-python-3/
"""

import importlib.resources as resourcesapi
from tkinter import CENTER, Canvas, Label, Tk
import wave
import socket

import assistant3.data


class GUI():
    """Empty."""
    HOST = "127.0.0.1"  # The server's hostname or IP address
    PORT = 65434

    def __init__(self) -> None:
        """Empty."""
        # initial Graphic settings
        self.window = Tk()
        self.window.title('Welcome to Assistant3')
        # Center Window by getting the requested
        # values of the height and width and make it daynically adjustable to label length
        window_width = self.window.winfo_reqwidth()
        window_height = self.window.winfo_reqheight()
        # Gets both half the screen width/height and window width/height
        position_right = int(self.window.winfo_screenwidth() / 2 - window_width / 2)
        position_down = int(self.window.winfo_screenheight() / 2 - window_height / 2)
        # Positions the window in the center of the page
        self.window.geometry(
            '+' +
            str(position_right) +
            '+' +
            str(position_down),
        )

        # Label for Text Output
        self.lbl = Label(self.window, font='Damascus', anchor=CENTER)

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
        # self.wav_sample = wave.open('./file_example_WAV_1MG.wav', 'r')
        wav_file_path = resourcesapi.path(assistant3.data, 'file_example_WAV_1MG.wav')
        self.wav_sample = wave.open(str(wav_file_path), 'r')
        self.frames = 700
        self.waves = []
        for i in range(1, self.frames):
            self.waves.append(int(self.wav_sample.readframes(i)[0]) * 0.23)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((GUI.HOST, GUI.PORT))

        self.animate = True

        

    def update_speech(self, text: str = 'understood Text...') -> None:
        # text needs to be passed
        self.myCanvas.delete('all')
        self.text = text
        self.lbl.config(text=self.text, font=('Damascus', 16, 'italic'))
        self.show_label()

        self.window.after(200, self.update_speech)

    def show_label(self):
        """Empty."""
        self.lbl.pack()
        # self.lbl.grid()

    def speech_bubble(self, x: int, y: int, r: int, **kwargs: int) -> int:
        """Empty."""
        'create a circle'
        self.myCanvas.delete('all')
        self.id = self.myCanvas.create_oval(x - r, y - r, x + r, y + r, **kwargs)
        return id

    # Update values
    def update_animate(self):
        rec = self.socket.recv(4)
        print(rec)
        if rec == b'0000':
            self.animate = False
        elif rec == b'0001':
            self.animate = True
        else:
            self.animate = True
        self.window.after(50, self.update_animate)
        

    
    def update_bubble(self) -> None:
        """Empty."""
        # Update Speech Bubble, speech is bool if usr is speeking, needs to be passed
        
        if self.animate:
            if self.frame < self.frames - 10:
                self.frame = self.frame + 1
            else:
                self.frame = 1

            self.radius = self.waves[self.frame] if self.waves[self.frame] > 15 else 15
            r = self.radius
            self.speech_bubble(100, 100, r, fill='red', outline='black', width=5)
        else:
            self.speech_bubble(100, 100, 30, fill='black', outline='black', width=3)

        self.window.after(100, self.update_bubble)

    def run(self) -> None:
        """Empty."""
        self.window.after(100, self.update_bubble)
        self.window.after(50, self.update_animate)
        #self.update_speech()

        self.window.mainloop()

def main():
    gui = GUI()

    gui.run()

if __name__ == '__main__':
    main()
