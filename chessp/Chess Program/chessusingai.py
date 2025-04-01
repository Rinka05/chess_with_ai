import tkinter as tk
from functools import partial
from pathlib import Path
from PIL import Image, ImageTk
import chess
import chess.engine
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")


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

        self.squares = {}
        self.selected_piece = None
        self.last_move = None
        self.turn = "white"
        self.board = chess.Board()
        self.engine = chess.engine.SimpleEngine.popen_uci(r"C:\\Users\\12345\\Downloads\\stockfish\\stockfish-windows-x86-64-avx2.exe")
        
        self.piece_images = self.load_piece_images()
        self.create_board()
        self.update_board()
    
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
    
    def select_piece(self, pos):
        if self.turn == "black":
            return  
        
        move_from = chess.parse_square(pos)
        if self.selected_piece is None:
            if self.board.piece_at(move_from) and self.board.piece_at(move_from).color == chess.WHITE:
                self.selected_piece = pos
                self.highlight_possible_moves(pos)
        else:
            move_to = chess.parse_square(pos)
            move = chess.Move(chess.parse_square(self.selected_piece), move_to)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.last_move = (self.selected_piece, pos)
                self.selected_piece = None
                self.update_board()
                self.check_game_status()
                if not self.board.is_game_over():
                    self.turn = "black"
                    self.turn_label.config(text="Black's Turn")
                    self.root.after(500, self.ai_move)
            else:
                self.selected_piece = None  
                self.update_board()
    
    def ai_move(self):
        engine_choice = self.engine_option.get()
        if engine_choice == "Stockfish":
            result = self.engine.play(self.board, chess.engine.Limit(time=1.0))
            move = result.move
        else:
            prompt = f"Given the following chess position in FEN notation: {self.board.fen()}, suggest the best move in UCI format."
            if engine_choice == "ChatGPT":
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}]
                )
                ai_move = response["choices"][0]["message"]["content"].strip()
            else:  # Gemini
                ai_move = "e2e4"  # Placeholder, replace with Gemini API call
            
            try:
                move = chess.Move.from_uci(ai_move)
                if move not in self.board.legal_moves:
                    raise ValueError("Invalid AI move")
            except ValueError:
                return
        
        self.board.push(move)
        self.last_move = (move.uci()[:2], move.uci()[2:])
        self.update_board()
        self.check_game_status()
        if not self.board.is_game_over():
            self.turn = "white"
            self.turn_label.config(text="White's Turn")
    
    def highlight_possible_moves(self, pos):
        self.update_board()
        square = chess.parse_square(pos)
        for move in self.board.legal_moves:
            if move.from_square == square:
                move_to = chess.square_name(move.to_square)
                self.squares[move_to].config(bg="lightblue")

    def update_board(self):
        for pos, btn in self.squares.items():
            piece = self.board.piece_at(chess.parse_square(pos))
            if piece:
                piece_color = "white" if piece.color == chess.WHITE else "black"
                piece_type = piece.symbol().lower()
                btn.config(image=self.piece_images[f"{piece_color}_{piece_type}"])
                btn.image = self.piece_images[f"{piece_color}_{piece_type}"]
            else:
                btn.config(image=self.piece_images["blank"])
                btn.image = self.piece_images["blank"]
    
    def check_game_status(self):
        if self.board.is_checkmate():
            self.status_label.config(text="Checkmate! Game Over.")
        elif self.board.is_stalemate():
            self.status_label.config(text="Stalemate! Game Over.")
    
    def __del__(self):
        self.engine.quit()

if __name__ == "__main__":
    root = tk.Tk()
    ChessBoard(root)
    root.mainloop()
