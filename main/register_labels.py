from carbon.gui.label import Label

from main.constants import THEME_BACKGROUND, THEME_FONT_COLOR


def register_labels(
    root
):

    Label(
        id='timer',
        x=20, y=root.winfo_screenheight()*0.9,
        text='up time: 0 sec', font='Arial 12',
        fg=THEME_FONT_COLOR, bg=THEME_BACKGROUND
    )

    Label(
        id='counter',
        x=20, y=90,
        text='Progress: N/A out of 81', font='Arial 16',
        fg=THEME_FONT_COLOR, bg=THEME_BACKGROUND
    )