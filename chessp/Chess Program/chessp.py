import tkinter as tk
from functools import partial
from pathlib import Path
from PIL import Image, ImageTk
import chess
import chess.engine
import openai
import os

openai_api_key = ""
gemini_api_key = ""

def set_api_keys(openai_key, gemini_key):
    global openai_api_key, gemini_api_key
    openai_api_key = openai_key
    gemini_api_key = gemini_key
    openai.api_key = openai_api_key

class ChessBoard:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Game")
        self.root.configure(bg="gray20")

        self.main_frame = tk.Frame(root, bg="gray20")
        self.main_frame.pack()

        self.board_frame = tk.Frame(self.main_frame, bg="gray20", padx=10, pady=10)
        self.board_frame.grid(row=0, column=0)

        self.info_frame = tk.Frame(self.main_frame, bg="gray20")
        self.info_frame.grid(row=0, column=1, padx=20)

        self.turn_label = tk.Label(self.info_frame, text="White's Turn", font=("Arial", 16), fg="white", bg="gray20")
        self.turn_label.pack(pady=10)

        self.status_label = tk.Label(self.info_frame, text="", font=("Arial", 14, "bold"), fg="yellow", bg="gray20", wraplength=200, justify="center")
        self.status_label.pack(pady=10)

        self.engine_option = tk.StringVar(value="Stockfish")
        self.engine_menu = tk.OptionMenu(self.info_frame, self.engine_option, "Stockfish", "ChatGPT", "Gemini")
        self.engine_menu.pack(pady=10)

        self.api_key_label = tk.Label(self.info_frame, text="Enter API Keys:", font=("Arial", 12), fg="white", bg="gray20")
        self.api_key_label.pack(pady=5)
        
        self.openai_key_entry = tk.Entry(self.info_frame, width=30)
        self.openai_key_entry.pack(pady=2)
        self.gemini_key_entry = tk.Entry(self.info_frame, width=30)
        self.gemini_key_entry.pack(pady=2)
        
        self.set_key_button = tk.Button(self.info_frame, text="Set API Keys", command=self.set_keys)
        self.set_key_button.pack(pady=5)

        self.squares = {}
        self.selected_piece = None
        self.last_move = None
        self.turn = "white"
        self.board = chess.Board()
        self.engine = chess.engine.SimpleEngine.popen_uci(r"C:\\Users\\12345\\Downloads\\stockfish\\stockfish-windows-x86-64-avx2.exe")
        
        self.piece_images = self.load_piece_images()
        self.create_board()
        self.update_board()
    
    def set_keys(self):
        set_api_keys(self.openai_key_entry.get(), self.gemini_key_entry.get())
    
    def load_piece_images(self):
        images = {}
        base_path = Path(__file__).parent / "assets"
        for color in ["white", "black"]:
            for piece in ["p", "r", "n", "b", "q", "k"]:
                file_path = base_path / f"{color}_{piece}.png"
                if file_path.exists():
                    img = Image.open(file_path).resize((80, 80))
                    images[f"{color}_{piece}"] = ImageTk.PhotoImage(img)
        images["blank"] = ImageTk.PhotoImage(Image.new("RGBA", (80, 80), (255, 255, 255, 0)))
        return images

    def create_board(self):
        for row in range(8):
            for col in range(8):
                square_color = "#8B4513" if (row + col) % 2 == 0 else "#F0D9B5"
                pos = f"{chr(97 + col)}{8 - row}"
                
                btn = tk.Button(
                    self.board_frame,
                    bg=square_color,
                    activebackground="goldenrod",
                    relief=tk.RAISED,
                    borderwidth=2,
                    image=self.piece_images["blank"],
                    width=80,
                    height=80,
                    compound="center",
                    command=partial(self.select_piece, pos)
                )
                btn.grid(row=row, column=col, padx=1, pady=1)
                self.squares[pos] = btn
    
    def update_board(self):
        for pos, btn in self.squares.items():
            piece = self.board.piece_at(chess.parse_square(pos))
            if piece:
                color = "white" if piece.color == chess.WHITE else "black"
                piece_key = f"{color}_{piece.symbol().lower()}"
                btn.config(image=self.piece_images.get(piece_key, self.piece_images["blank"]), bg=("#8B4513" if (ord(pos[0]) + int(pos[1])) % 2 == 0 else "#F0D9B5"))
            else:
                btn.config(image=self.piece_images["blank"], bg=("#8B4513" if (ord(pos[0]) + int(pos[1])) % 2 == 0 else "#F0D9B5"))
    
    def select_piece(self, pos):
        if self.selected_piece is None:
            piece = self.board.piece_at(chess.parse_square(pos))
            if piece and ((self.turn == "white" and piece.color == chess.WHITE) or (self.turn == "black" and piece.color == chess.BLACK)):
                self.selected_piece = pos
                self.highlight_moves()
        else:
            if self.selected_piece == pos:
                self.selected_piece = None
                self.update_board()
                return
            move = chess.Move.from_uci(self.selected_piece + pos)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.last_move = (self.selected_piece, pos)
                self.selected_piece = None
                self.update_board()
                self.turn = "black" if self.turn == "white" else "white"
                self.turn_label.config(text=("Black's Turn" if self.turn == "black" else "White's Turn"))
                self.root.after(500, self.ai_move)
            else:
                self.selected_piece = None
                self.update_board()
    
    def ai_move(self):
        if not self.board.is_game_over():
            result = self.engine.play(self.board, chess.engine.Limit(time=1.0))
            move = result.move
            if move:
                self.board.push(move)
                self.update_board()
                self.turn = "white"
                self.turn_label.config(text="White's Turn")
    
    def __del__(self):
        self.engine.quit()

if __name__ == "__main__":
    root = tk.Tk()
    ChessBoard(root)
    root.mainloop()
