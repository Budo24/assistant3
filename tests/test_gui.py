"""Tests for the GUI."""
import pytest
from assistant3.gui.cGui import GUI

def test_text() -> None:
    gui = GUI().__init__()
    gui.lbl.config(text='Hello World')
    assert gui.lbl.getc("text") == "Hello World"


def test_speech_update():
    """Test if Text updates if new one is inserted"""
    speech = GUI().update_speech()
    speech(text = "This is a new Text")
    assert GUI().__init__().lbl.getc("text") == "This is a new Text""This is a new Text"

def test_animate():
    """Test if animate is true while somenoe speaks"""
    update = GUI().update_animate()
    update(rec=b'0000')
    assert GUI().__init__.animate = False

    update(rec = b'0001')
    assert GUI().__init__.animate = True


def test_speech_bubble_update():
    """Test if Speechbubble is animating while speech is true"""
    GUI().__init__.animate = True
    a =  GUI().update_bubble(frames=500)
    b = GUI().update_bubble(frames=300)
    assert a is not b

def main():
    test_text()

if __name__ == '__main__':
    main()
