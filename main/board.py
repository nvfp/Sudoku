import random
import tkinter as tk
import time

from carbon.gui.button import Button
from carbon.gui.label import Label

from main.constants import THEME_FONT_COLOR


CELL_COLOR_UNFOCUS = '#000'
CELL_COLOR_FOCUS = '#111'
CELL_COLOR_FOCUS_CTR = '#333'
CELL_BORDER_COLOR = '#777'
BOX_BORDER_COLOR = '#dddddd'
FONT_COLOR_FOCUS = '#ffffff'
FONT_COLOR_UNFOCUS = '#bbbbbb'
FONT_COLOR_GIVEN = '#555'

NUM_PAD_GAP = 45
NUM_PAD_BG_COLOR = '#000'
NUM_PAD_ALLOWED_COLOR = '#fff'
NUM_PAD_UNALLOWED_COLOR = '#555'

## Sudoku puzzle with fewer than 17 givens is mathematically impossible to solve
N_GIVENS_EASY = [40, 45]
N_GIVENS_MEDIUM = [35, 39]
N_GIVENS_HARD = [30, 34]


class Board:

    values = None
    given_indices = []  # to hold the given cell indices. given cells are immutable.
    level = N_GIVENS_EASY

    @staticmethod
    def change_level(idx):
        if idx == 0:
            Board.level = N_GIVENS_EASY
        elif idx == 1:
            Board.level = N_GIVENS_MEDIUM
        elif idx == 2:
            Board.level = N_GIVENS_HARD

    def __init__(self, root, page: tk.Canvas, Runtime) -> None:
        
        self.page = page
        self.Runtime = Runtime

        cell_len = root.winfo_screenheight()*0.9 // 9

        X = (root.winfo_screenwidth() - cell_len*9) / 2
        Y = (root.winfo_screenheight() - cell_len*9) / 2
        
        for y in range(9):
            for x in range(9):
                page.create_rectangle(
                    X + cell_len*x, Y + cell_len*y,
                    X + cell_len*(x + 1), Y + cell_len*(y + 1),
                    fill=CELL_COLOR_UNFOCUS, outline=CELL_BORDER_COLOR, tags=(f'cell_{x}_{y}', f'cell_{y*9 + x}')
                )
                page.create_text(
                    X + cell_len*x + cell_len/2, Y + cell_len*y + cell_len/2,
                    text='', font='Arial 22', fill=FONT_COLOR_UNFOCUS, tags=(f'num_{x}_{y}', f'num_{y*9 + x}', 'num', 'pause')
                )
        
        ## box border
        for x in range(4):
            page.create_line(X + cell_len*3*x, Y, X + cell_len*3*x, Y + cell_len*9, fill=BOX_BORDER_COLOR, width=1)
        for y in range(4):
            page.create_line(X, Y + cell_len*3*y, X + cell_len*9, Y + cell_len*3*y, fill=BOX_BORDER_COLOR, width=1)

        ## number pad
        for y in range(9):
            page.create_rectangle(
                X + cell_len*9 + NUM_PAD_GAP, Y + cell_len*y,
                X + cell_len*9 + NUM_PAD_GAP + cell_len, Y + cell_len*(y + 1),
                fill=NUM_PAD_BG_COLOR, outline=CELL_BORDER_COLOR
            )
            page.create_text(
                X + cell_len*9 + NUM_PAD_GAP + cell_len/2, Y + cell_len*y + cell_len/2,
                text=str(y+1), font='Arial 22', fill=NUM_PAD_ALLOWED_COLOR, tags=(f'num_pad_{y+1}', 'num_pad', 'pause')
            )


        # self.reset()  # can't reset here because the label "counter" hasn't been initialized yet


        ## LISTENERS

        def navigate_up(e):
            if Runtime.paused: return
            new_idx = Runtime.board_focused_cell_idx - 9
            if new_idx < 0:
                new_idx += 81
            self.refocus_cell(new_idx)
            self.update_num_pad()

        def navigate_right(e):
            if Runtime.paused: return
            new_idx = Runtime.board_focused_cell_idx + 1
            if new_idx % 9 == 0:
                new_idx -= 9
            self.refocus_cell(new_idx)
            self.update_num_pad()

        def navigate_down(e):
            if Runtime.paused: return
            new_idx = Runtime.board_focused_cell_idx + 9
            if new_idx >= 81:
                new_idx -= 81
            self.refocus_cell(new_idx)
            self.update_num_pad()

        def navigate_left(e):
            if Runtime.paused: return
            new_idx = Runtime.board_focused_cell_idx - 1
            if new_idx % 9 == 8:
                new_idx += 9
            self.refocus_cell(new_idx)
            self.update_num_pad()

        def navigate_home(e):
            if Runtime.paused: return
            new_idx = Runtime.board_focused_cell_idx // 9 * 9  # jump to the first column
            self.refocus_cell(new_idx)
            self.update_num_pad()

        def navigate_end(e):
            if Runtime.paused: return
            new_idx = (Runtime.board_focused_cell_idx // 9 + 1) * 9 - 1  # jump to the last column
            self.refocus_cell(new_idx)
            self.update_num_pad()

        def navigate_page_up(e):
            if Runtime.paused: return
            new_idx = Runtime.board_focused_cell_idx % 9  # jump to the first row
            self.refocus_cell(new_idx)
            self.update_num_pad()

        def navigate_page_down(e):
            if Runtime.paused: return
            new_idx = 80 - (8 - (Runtime.board_focused_cell_idx % 9))  # jump to the last row
            if new_idx >= 81:
                new_idx = 80
            self.refocus_cell(new_idx)
            self.update_num_pad()

        root.bind('<Up>', navigate_up)
        root.bind('<Right>', navigate_right)
        root.bind('<Down>', navigate_down)
        root.bind('<Left>', navigate_left)
        root.bind('<Home>', navigate_home)
        root.bind('<End>', navigate_end)
        root.bind('<Prior>', navigate_page_up)
        root.bind('<Next>', navigate_page_down)

        def wrapper(e):
            if Runtime.paused: return
            self.set_cell_value(int(e.char))
        for i in range(9):
            root.bind(str(i+1), wrapper)
        
        def wrapper(e):
            if Runtime.paused: return
            self.set_cell_value(None)
        root.bind('<BackSpace>', wrapper)


    def refocus_cell(self, idx):

        ## restore the normal color of the previously focused cells
        _y = self.Runtime.board_focused_cell_idx // 9
        _x = self.Runtime.board_focused_cell_idx % 9
        cross = [(_x, i) for i in range(9)] + [(i, _y) for i in range(9)]
        for X, Y in cross:
            _idx = X+Y*9
            self.page.itemconfigure(f'cell_{_idx}', fill=CELL_COLOR_UNFOCUS)
            if _idx not in Board.given_indices:  # givens remain unchanged
                self.page.itemconfigure(f'num_{_idx}', fill=FONT_COLOR_UNFOCUS)

        ## new focused cell
        self.Runtime.board_focused_cell_idx = idx
        y = idx // 9
        x = idx % 9
        cross = [(x, i) for i in range(9)] + [(i, y) for i in range(9)]
        for X, Y in cross:
            _idx = X+Y*9
            self.page.itemconfigure(f'cell_{_idx}', fill=CELL_COLOR_FOCUS)
            if _idx not in Board.given_indices:  # givens don't have to be highlighted
                self.page.itemconfigure(f'num_{_idx}', fill=FONT_COLOR_FOCUS)
        self.page.itemconfigure(f'cell_{x}_{y}', fill=CELL_COLOR_FOCUS_CTR)


    def pause(self):
        self.page.itemconfig('pause', state='hidden')

    def resume(self):
        self.page.itemconfig('pause', state='normal')

    def check_value(self, cell_idx, value):

        row = cell_idx // 9
        col = cell_idx % 9
        
        ## check if value is valid in the row
        for i in range(9):
            if Board.values[row*9+i] == value:
                return False
        
        ## check if value is valid in the column
        for i in range(9):
            if Board.values[i*9+col] == value:
                return False
        
        ## check if value is valid in the box
        box_row = (row // 3) * 3
        box_col = (col // 3) * 3
        for i in range(3):
            for j in range(3):
                if Board.values[(box_row+i)*9+(box_col+j)] == value:
                    return False

        ## the value is valid
        return True

    def update_num_pad(self):

        if self.Runtime.board_focused_cell_idx in Board.given_indices:
            ## given cells are immutable
            self.page.itemconfig('num_pad', fill=NUM_PAD_UNALLOWED_COLOR)
        else:

            for i in range(9):
                if self.check_value(self.Runtime.board_focused_cell_idx, i+1) or (Board.values[self.Runtime.board_focused_cell_idx] == (i+1)):
                    self.page.itemconfig(f'num_pad_{i+1}', fill=NUM_PAD_ALLOWED_COLOR)
                else:
                    self.page.itemconfig(f'num_pad_{i+1}', fill=NUM_PAD_UNALLOWED_COLOR)

    def reset(self):

        self.Runtime.stopwatch = time.time()
        self.Runtime.paused = False
        Button.set_lock_by_id('pause', False)
        
        ## reset
        Board.values = [None] * 81
        Board.given_indices = []
        self.page.itemconfig('num', text='')

        ## fill cells with valid Sudoku numbers
        n_givens = random.randint(*Board.level)
        num_givens = 0
        indices = list(range(81))
        random.shuffle(indices)

        for idx in indices:
            if num_givens >= n_givens:
                break
            if Board.values[idx] is None:
                for val in random.sample(range(1, 10), 9):
                    if self.check_value(idx, val):
                        Board.values[idx] = val
                        Board.given_indices.append(idx)
                        self.page.itemconfig(f'num_{idx}', text=str(val), fill=FONT_COLOR_GIVEN)
                        num_givens += 1
                        break

        ## testing purposes
        # Board.values = [
        #     5, 3, 4, 6, 7, 8, 9, 1, 2,    
        #     6, 7, 2, 1, 9, 5, 3, 4, 8,    
        #     1, 9, 8, 3, 4, 2, 5, 6, 7,    
        #     8, 5, 9, 7, 6, 1, 4, 2, 3,    
        #     4, 2, 6, 8, 5, 3, 7, 9, 1,    
        #     7, 1, 3, 9, 2, 4, 8, 5, 6,    
        #     9, 6, 1, 5, 3, 7, 2, 8, 4,    
        #     2, 8, 7, 4, 1, 9, 6, 3, 5,    
        #     3, 4, 5, 2, 8, 6, 1, 7, None
        # ]
        # Board.given_indices = []

        Label.set_text_by_id('counter', f'Progress: {n_givens} out of 81')
        self.refocus_cell(40)  # 40 is from 9*9//2
        self.update_num_pad()

    def set_cell_value(self, value):
        
        if self.Runtime.board_focused_cell_idx in Board.given_indices:
            ## given cells are immutable
            return
        
        if value is None:
            ## removing the cell value
            Board.values[self.Runtime.board_focused_cell_idx] = None
            self.page.itemconfig(f'num_{self.Runtime.board_focused_cell_idx}', text='')
            Label.set_text_by_id('counter', f'Progress: {sum(isinstance(x, int) for x in Board.values)} out of 81')
            return

        if not self.check_value(self.Runtime.board_focused_cell_idx, value):
            return

        Board.values[self.Runtime.board_focused_cell_idx] = value
        self.page.itemconfig(f'num_{self.Runtime.board_focused_cell_idx}', text=str(value))
        Label.set_text_by_id('counter', f'Progress: {sum(isinstance(x, int) for x in Board.values)} out of 81')

        if self.is_finish():
            self.Runtime.paused = True  # freeze the game listeners

            ## direct user to press RESET button to restart the game
            Button.set_lock_by_id('hint', True)
            Button.set_lock_by_id('solve', True)
            Button.set_lock_by_id('pause', True)
            self.page.itemconfig(f'cell_{self.Runtime.board_focused_cell_idx}', fill=CELL_COLOR_UNFOCUS)
            self.page.itemconfig('num', fill=FONT_COLOR_FOCUS)
            self.page.itemconfig('num_pad', fill=NUM_PAD_UNALLOWED_COLOR)

    def is_finish(self):
        """true if the game finish, false if not."""
        
        ## check rows
        for i in range(9):
            row = set(Board.values[i*9:(i+1)*9])
            if len(row) != 9:
                return False
        
        ## check columns
        for i in range(9):
            col = set(Board.values[i::9])
            if len(col) != 9:
                return False

        ## check sub-grids
        for i in range(0, 9, 3):
            for j in range(0, 9, 3):
                subgrid = set(Board.values[i*9+j:i*9+j+3] + Board.values[(i+1)*9+j:(i+1)*9+j+3] + Board.values[(i+2)*9+j:(i+2)*9+j+3])
                if len(subgrid) != 9:
                    return False
        
        return True
