import json
import os
import random
import tkinter as tk
from tkinter import messagebox

SCORE_FILE = 'score.json'
GRID_SIZE = 4

DEFAULT_COLORS = {
    0: '#cdc1b4',
    2: '#eee4da',
    4: '#ede0c8',
    8: '#f2b179',
    16: '#f59563',
    32: '#f67c5f',
    64: '#f65e3b',
    128: '#edcf72',
    256: '#edcc61',
    512: '#edc850',
    1024: '#edc53f',
    2048: '#edc22e',
}

DARK_COLORS = {
    0: '#776e65',
    2: '#eee4da',
    4: '#ede0c8',
    8: '#f2b179',
    16: '#f59563',
    32: '#f67c5f',
    64: '#f65e3b',
    128: '#edcf72',
    256: '#edcc61',
    512: '#edc850',
    1024: '#edc53f',
    2048: '#edc22e',
}

class Game2048:
    def __init__(self, master):
        self.master = master
        master.title('2048 Game')
        self.theme_dark = False
        self.colors = DEFAULT_COLORS
        self.load_highscore()
        self.setup_ui()
        self.reset_game()
        self.master.bind('<Key>', self.handle_key)

    def setup_ui(self):
        top_frame = tk.Frame(self.master)
        top_frame.pack(pady=10)

        self.score_var = tk.StringVar()
        self.high_var = tk.StringVar()

        tk.Label(top_frame, textvariable=self.score_var, width=10).pack(side=tk.LEFT, padx=5)
        tk.Label(top_frame, textvariable=self.high_var, width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text='Reset', command=self.reset_game).pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text='Theme', command=self.toggle_theme).pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text='Help', command=self.show_help).pack(side=tk.LEFT, padx=5)

        self.tiles = []
        board = tk.Frame(self.master, bg='#bbada0')
        board.pack(padx=10, pady=10)
        for r in range(GRID_SIZE):
            row = []
            for c in range(GRID_SIZE):
                lbl = tk.Label(board, text='', width=4, height=2, font=('Helvetica', 32, 'bold'))
                lbl.grid(row=r, column=c, padx=5, pady=5)
                row.append(lbl)
            self.tiles.append(row)

    def show_help(self):
        messagebox.showinfo('How to Play',
            'Use arrow keys to move tiles.\n'
            'When two tiles with the same number touch, they merge into one!\n'
            'Reach 2048 to win.')

    def load_highscore(self):
        if os.path.exists(SCORE_FILE):
            with open(SCORE_FILE, 'r') as f:
                data = json.load(f)
                self.highscore = data.get('highscore', 0)
        else:
            self.highscore = 0

    def save_highscore(self):
        with open(SCORE_FILE, 'w') as f:
            json.dump({'highscore': self.highscore}, f)

    def reset_game(self):
        self.board = [[0]*GRID_SIZE for _ in range(GRID_SIZE)]
        self.score = 0
        self.add_random_tile()
        self.add_random_tile()
        self.update_ui()

    def add_random_tile(self):
        empty = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if self.board[r][c] == 0]
        if empty:
            r, c = random.choice(empty)
            self.board[r][c] = 4 if random.random() > 0.9 else 2

    def compress(self, row):
        new_row = [i for i in row if i]
        new_row += [0]*(GRID_SIZE-len(new_row))
        return new_row

    def merge(self, row):
        for i in range(GRID_SIZE-1):
            if row[i] and row[i] == row[i+1]:
                row[i] *= 2
                self.score += row[i]
                row[i+1] = 0
        return row

    def move_left(self):
        changed = False
        for r in range(GRID_SIZE):
            original = list(self.board[r])
            row = self.compress(self.board[r])
            row = self.merge(row)
            row = self.compress(row)
            self.board[r] = row
            if row != original:
                changed = True
        if changed:
            self.add_random_tile()
        return changed

    def move_right(self):
        self.board = [list(reversed(r)) for r in self.board]
        changed = self.move_left()
        self.board = [list(reversed(r)) for r in self.board]
        return changed

    def transpose(self):
        self.board = [list(row) for row in zip(*self.board)]

    def move_up(self):
        self.transpose()
        changed = self.move_left()
        self.transpose()
        return changed

    def move_down(self):
        self.transpose()
        changed = self.move_right()
        self.transpose()
        return changed

    def handle_key(self, event):
        key = event.keysym
        moved = False
        if key == 'Up':
            moved = self.move_up()
        elif key == 'Down':
            moved = self.move_down()
        elif key == 'Left':
            moved = self.move_left()
        elif key == 'Right':
            moved = self.move_right()
        if moved:
            self.update_ui()
            if self.check_game_over():
                self.end_game()
        self.update_score_labels()

    def update_ui(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                value = self.board[r][c]
                tile = self.tiles[r][c]
                tile.config(text='' if value == 0 else str(value),
                            bg=self.colors.get(value, '#3c3a32'),
                            fg='#776e65' if value <= 4 else 'white')
        self.update_score_labels()

    def update_score_labels(self):
        self.highscore = max(self.highscore, self.score)
        self.score_var.set(f'Score: {self.score}')
        self.high_var.set(f'Best: {self.highscore}')

    def check_game_over(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.board[r][c] == 0:
                    return False
                if c < GRID_SIZE-1 and self.board[r][c] == self.board[r][c+1]:
                    return False
                if r < GRID_SIZE-1 and self.board[r][c] == self.board[r+1][c]:
                    return False
        return True

    def end_game(self):
        self.save_highscore()
        messagebox.showinfo('Game Over', 'No more moves!')

    def toggle_theme(self):
        self.theme_dark = not self.theme_dark
        self.colors = DARK_COLORS if self.theme_dark else DEFAULT_COLORS
        self.update_ui()

    def on_close(self):
        self.save_highscore()
        self.master.destroy()


def main():
    root = tk.Tk()
    game = Game2048(root)
    root.protocol('WM_DELETE_WINDOW', game.on_close)
    root.mainloop()

if __name__ == '__main__':
    main()
