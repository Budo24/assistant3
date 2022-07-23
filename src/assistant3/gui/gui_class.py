"""Gui."""

import importlib.resources as resourcesapi
import socket
import wave
from tkinter import CENTER, Canvas, Label, Tk

import assistant3.data


class GUI():
    """Empty."""

    HOST = '127.0.0.1'  # The server's hostname or IP address
    PORT = 65511

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
        self.text = 'Understood text ...'
        self.radius = 0.0
        # Label for Text Output
        self.lbl = Label(self.window, font='Damascus', anchor=CENTER)

        # Canvas for Speech animations
        canvas_width = 200
        canvas_height = 200
        self.m_canvas = Canvas(self.window, width=canvas_width, height=canvas_height)
        self.m_canvas.place(relx=0.5, rely=0.5, anchor=CENTER)
        self.m_canvas.pack()
        # self.m_canvas.grid(row=0, column=0)

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

    def update_speech(self) -> None:
        """Update speech callback."""
        # text needs to be passed
        self.m_canvas.delete('all')
        wav_file_path = resourcesapi.path(assistant3.data, 'inter_results.txt')
        try:
            with open(str(wav_file_path), 'r', encoding='utf-8') as r_f:

                self.text = r_f.readlines()[-1]
        except FileNotFoundError:
            pass
        except IndexError:
            pass
        self.lbl.config(text=self.text, font=('Damascus', 16, 'italic'))
        self.show_label()

    def show_label(self) -> None:
        """Empty."""
        self.lbl.pack()
        # self.lbl.grid()

    def speech_bubble(self, _x: int, _y: int, _r: int, **kwargs: int) -> None:
        """Empty."""
        self.m_canvas.delete('all')
        self.m_canvas.create_oval(_x0=_x - _r, _y0=_y - _r, _x1=_x + _r, _x2=_y + _r, **kwargs)

    # Update values
    def update_animate(self) -> None:
        """Update animation callback."""
        rec = self.socket.recv(4)
        print(rec)
        if rec == b'0000':
            self.update_speech()
            self.animate = False
        elif rec == b'0001':
            self.animate = True
        else:
            self.animate = True
        self.window.after(50, self.update_animate)

    def update_bubble(self) -> None:
        """Update circle callback."""
        # Update Speech Bubble, speech is bool if usr is speeking, needs to be passed

        if self.animate:
            if self.frame < self.frames - 10:
                self.frame = self.frame + 1
            else:
                self.frame = 1

            self.radius = self.waves[self.frame] if self.waves[self.frame] > 15 else 15
            _r = self.radius
            self.speech_bubble(100, 100, int(_r), fill='red', outline='black', width=5)
        else:
            self.speech_bubble(100, 100, 30, fill='black', outline='black', width=3)

        self.window.after(100, self.update_bubble)

    def run(self) -> None:
        """Start main loop."""
        self.window.after(100, self.update_bubble)
        self.window.after(50, self.update_animate)
        self.update_speech()

        self.window.mainloop()


def main() -> None:
    """Gui main function."""
    gui = GUI()
    gui.run()


if __name__ == '__main__':
    main()
