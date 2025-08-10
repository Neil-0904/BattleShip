import tkinter as tk
from tkinter import messagebox
import random

GRID_SIZE = 6
SHIP_SIZES = [3, 2]

def create_grid():
    return [['.' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

def place_ships(grid):
    for size in SHIP_SIZES:
        placed = False
        while not placed:
            orient = random.choice(['H', 'V'])
            if orient == 'H':
                row = random.randint(0, GRID_SIZE-1)
                col = random.randint(0, GRID_SIZE-size)
                if all(grid[row][col+i] == '.' for i in range(size)):
                    for i in range(size):
                        grid[row][col+i] = 'S'
                    placed = True
            else:
                row = random.randint(0, GRID_SIZE-size)
                col = random.randint(0, GRID_SIZE-1)
                if all(grid[row+i][col] == '.' for i in range(size)):
                    for i in range(size):
                        grid[row+i][col] = 'S'
                    placed = True

def check_win(board):
    return all(cell != 'S' for row in board for cell in row)

def ai_random_heuristic(guesses):
    options = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if guesses[r][c] == '.']
    return random.choice(options)

def ai_hunt_heuristic(guesses):
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if guesses[r][c] == 'X':
                for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE and guesses[nr][nc] == '.':
                        return nr, nc
    return ai_random_heuristic(guesses)

def ai_dual_heuristic(guesses, last_hit):
    if last_hit:
        return ai_hunt_heuristic(guesses)
    else:
        return ai_random_heuristic(guesses)

class BattleshipGUI:
    def __init__(self, master):
        self.master = master
        master.title("Battleship")

        self.player_board = create_grid()
        self.ai_board = create_grid()
        place_ships(self.player_board)
        place_ships(self.ai_board)

        self.player_guesses = create_grid()
        self.ai_guesses = create_grid()
        self.ai_last_hit = False

        self.player_buttons = []
        self.ai_buttons = []

        self.status_label = tk.Label(master, text="Your turn! Click the AI's grid to fire.")
        self.status_label.grid(row=0, column=0, columnspan=GRID_SIZE*2)

        tk.Label(master, text="Your Board").grid(row=1, column=0, columnspan=GRID_SIZE)
        tk.Label(master, text="AI Board").grid(row=1, column=GRID_SIZE, columnspan=GRID_SIZE)

        for r in range(GRID_SIZE):
            row_buttons = []
            for c in range(GRID_SIZE):
                btn = tk.Button(master, width=2, height=1, state=tk.NORMAL, font=('Arial', 12),
                                command=lambda r=r, c=c: self.player_fire(r, c))
                btn.grid(row=r+2, column=c)
                row_buttons.append(btn)
            self.player_buttons.append(row_buttons)

        for r in range(GRID_SIZE):
            row_buttons = []
            for c in range(GRID_SIZE):
                btn = tk.Button(master, width=2, height=1, state=tk.NORMAL, font=('Arial', 12),
                                command=lambda r=r, c=c: self.fire_at_ai(r, c))
                btn.grid(row=r+2, column=GRID_SIZE+c)
                row_buttons.append(btn)
            self.ai_buttons.append(row_buttons)

        self.update_player_board()

    def update_player_board(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                val = self.player_board[r][c]
                btn = self.player_buttons[r][c]
                if val == 'S':
                    btn.config(text='S', bg='light blue', state=tk.DISABLED)
                elif val == 'X':
                    btn.config(text='X', bg='red', state=tk.DISABLED)
                elif val == 'O':
                    btn.config(text='O', bg='white', state=tk.DISABLED)
                else:
                    btn.config(text='', bg='SystemButtonFace', state=tk.DISABLED)

    def update_ai_board(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                val = self.player_guesses[r][c]
                btn = self.ai_buttons[r][c]
                if val == 'X':
                    btn.config(text='X', bg='red', state=tk.DISABLED)
                elif val == 'O':
                    btn.config(text='O', bg='white', state=tk.DISABLED)
                else:
                    btn.config(text='', bg='SystemButtonFace', state=tk.NORMAL)

    def fire_at_ai(self, r, c):
        if self.player_guesses[r][c] != '.':
            return
        if self.ai_board[r][c] == 'S':
            self.player_guesses[r][c] = 'X'
            self.ai_board[r][c] = 'X'
            self.status_label.config(text="Hit! Go again.")
        else:
            self.player_guesses[r][c] = 'O'
            self.ai_board[r][c] = 'O'
            self.status_label.config(text="Miss! AI's turn.")
            self.update_ai_board()
            self.master.after(1000, self.ai_turn)
            return
        self.update_ai_board()
        if check_win(self.ai_board):
            messagebox.showinfo("Battleship", "You win!")
            self.master.destroy()

    def ai_turn(self):
        r, c = ai_dual_heuristic(self.ai_guesses, self.ai_last_hit)
        if self.player_board[r][c] == 'S':
            self.ai_guesses[r][c] = 'X'
            self.player_board[r][c] = 'X'
            self.ai_last_hit = True
            self.status_label.config(text=f"AI hits at ({r},{c})! AI goes again.")
            self.update_player_board()
            if check_win(self.player_board):
                messagebox.showinfo("Battleship", "AI wins!")
                self.master.destroy()
            else:
                self.master.after(1000, self.ai_turn)
        else:
            self.ai_guesses[r][c] = 'O'
            self.player_board[r][c] = 'O'
            self.ai_last_hit = False
            self.status_label.config(text=f"AI misses at ({r},{c})! Your turn.")
            self.update_player_board()
            self.update_ai_board()

    def player_fire(self, r, c):
        # Not used, but can be enabled for player-vs-player later
        pass

if __name__ == "__main__":
    root = tk.Tk()
    gui = BattleshipGUI(root)
    root.mainloop()