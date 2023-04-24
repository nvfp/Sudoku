import time
import tkinter as tk

from carbon.gui.button import Button
from carbon.gui.label import Label
from carbon.time import get_dur

from main.constants import SOFTWARE_NAME, SOFTWARE_VER, THEME_BACKGROUND
from main.board import Board
from main.register_buttons import register_buttons
from main.register_labels import register_labels


root = tk.Tk()
root.attributes('-fullscreen', True)
root.title(f'{SOFTWARE_NAME}_v{SOFTWARE_VER}')

page = tk.Canvas(root, bg=THEME_BACKGROUND, highlightthickness=0, borderwidth=0)
page.pack(fill=tk.BOTH, expand=True)

Button.page = page


class Runtime:
    stopwatch = time.time()
    paused = False

    board_focused_cell_idx = 0


board = Board(root, page, Runtime)


register_buttons(root, Runtime, board)
register_labels(root)


## <event listeners>
def left_mouse_press(e):
    Button.press_listener()    
root.bind('<ButtonPress-1>', left_mouse_press)

def left_mouse_release(e):
    Button.release_listener()
root.bind('<ButtonRelease-1>', left_mouse_release)

root.bind('<Escape>', lambda e: root.destroy())
## </event listeners>


## <background>
def background_slow():
    if not Runtime.paused:
        Label.set_text_by_id('timer', f'Time: {get_dur(time.time() - Runtime.stopwatch)}')
    root.after(1000, background_slow)

def background_fast():
    Button.hover_listener()
    root.after(50, background_fast)
## </background>


def main():

    ## <all necessary pre-startup things>
    board.reset()
    ## </all necessary pre-startup things>

    background_slow()
    background_fast()
    root.mainloop()