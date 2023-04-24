import time

from carbon.gui.button import Button


def register_buttons(
    root,
    Runtime,
    board
):

    BTN_X = 40
    BTN_Y = 20
    BTN_X_GAP = 60
    BTN_LEN = 50
    def wrapper(idx, id):
        board.change_level(idx)
        Button.set_lock_by_tag('level', False)
        Button.set_lock_by_id(id, True)
    Button(
        id='easy',
        x=BTN_X,
        y=BTN_Y,
        label='Easy',
        fn=lambda: wrapper(0, 'easy'),
        len=BTN_LEN,
        locked=True,
        tags='level'
    )
    Button(
        id='medium',
        x=BTN_X + BTN_X_GAP,
        y=BTN_Y,
        label='Medium',
        fn=lambda: wrapper(1, 'medium'),
        len=BTN_LEN,
        tags='level'
    )
    Button(
        id='hard',
        x=BTN_X + BTN_X_GAP*2,
        y=BTN_Y,
        label='Hard',
        fn=lambda: wrapper(2, 'hard'),
        len=BTN_LEN,
        tags='level'
    )

    BTN_X = 40
    BTN_Y = 50
    BTN_X_GAP = 60
    BTN_LEN = 50
    Button(
        id='reset',
        x=BTN_X,
        y=BTN_Y,
        label='Reset',
        fn=board.reset,
        len=BTN_LEN
    )
    # Button(
    #     id='hint',
    #     x=BTN_X + BTN_X_GAP,
    #     y=BTN_Y,
    #     label='Hint',
    #     fn=None,
    #     len=BTN_LEN,
    #     locked=True
    # )
    # Button(
    #     id='solve',
    #     x=BTN_X + BTN_X_GAP*2,
    #     y=BTN_Y,
    #     label='Solve',
    #     fn=None,
    #     len=BTN_LEN,
    #     locked=True
    # )

    class X:
        t = 0
    def fn():
        Runtime.paused = not Runtime.paused
        if Runtime.paused:
            X.t = time.time()
            Button.set_label_by_id('pause', 'Continue')
            board.pause()
        else:
            Runtime.stopwatch += time.time() - X.t
            Button.set_label_by_id('pause', 'Pause')
            board.resume()
    Button(
        id='pause',
        x=60,
        y=root.winfo_screenheight()*0.9 + 45,
        label='Pause',
        fn=fn,
        len=70
    )