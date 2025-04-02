import tkinter as tk
from functools import partial
from pathlib import Path
from PIL import Image, ImageTk
import chess
import chess.engine
import google.generativeai as genai
import re

genai.configure(api_key="")  # Initial placeholder, will be updated from UI

def set_gemini_key(gemini_key):
    global genai
    genai.configure(api_key=gemini_key)

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

        self.engine_option = tk.StringVar(value="Gemini")
        self.engine_menu = tk.OptionMenu(self.info_frame, self.engine_option, "Gemini")
        self.engine_menu.pack(pady=10)

        self.api_key_label = tk.Label(self.info_frame, text="Enter Gemini API Key:", font=("Arial", 12), fg="white", bg="gray20")
        self.api_key_label.pack(pady=5)

        self.gemini_key_entry = tk.Entry(self.info_frame, width=30)
        self.gemini_key_entry.pack(pady=2)

        self.set_key_button = tk.Button(self.info_frame, text="Set API Key", command=self.set_keys)
        self.set_key_button.pack(pady=5)

        self.squares = {}
        self.selected_piece = None
        self.turn = "white"
        self.board = chess.Board()
        self.piece_images = self.load_piece_images()
        self.create_board()
        self.update_board()

    def set_keys(self):
        set_gemini_key(self.gemini_key_entry.get())
        self.gemini_key_entry.delete(0, tk.END) #Clears the entry field

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
                btn.config(image=self.piece_images.get(piece_key, self.piece_images["blank"]))
            else:
                btn.config(image=self.piece_images["blank"])

        if self.board.is_game_over():
            result = self.board.result()
            if result == "1-0":
                self.status_label.config(text="White wins!")
            elif result == "0-1":
                self.status_label.config(text="Black wins!")
            else:
                self.status_label.config(text="Game Drawn!")

    def select_piece(self, pos):
        if self.selected_piece is None:
            piece = self.board.piece_at(chess.parse_square(pos))
            if piece and ((self.turn == "white" and piece.color == chess.WHITE) or (self.turn == "black" and piece.color == chess.BLACK)):
                self.selected_piece = pos
        else:
            if self.selected_piece == pos:
                self.selected_piece = None
                return
            move = chess.Move.from_uci(self.selected_piece + pos)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.turn = "black" if self.turn == "white" else "white"
                self.turn_label.config(text=("Black's Turn" if self.turn == "black" else "White's Turn"))
                self.selected_piece = None
                self.update_board()
                self.root.after(500, self.ai_move)
            else:
                self.selected_piece = None

    def ai_move(self):
        if not self.board.is_game_over():
            if self.engine_option.get() == "Gemini":
                move = self.get_gemini_move(self.board.fen())
                if move:
                    self.board.push(move)
                    self.update_board()
                    self.turn = "white"
                    self.turn_label.config(text="White's Turn")


    def get_gemini_move(self, fen):
        try:
            model = genai.GenerativeModel("models/gemini-1.5-pro-latest")  # Use the correct model name
            prompt = f"Given the chess position in FEN notation: {fen}, provide the best legal move for {'black' if self.turn == 'black' else 'white'} in UCI format only. Do not provide any additional text or explanation."
            # print(f"Sending prompt: {prompt}")
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            # print(f"Gemini response: {response_text}")

            # Extract the UCI move using a regular expression
            uci_match = re.search(r"[a-h][1-8][a-h][1-8][qrbn]?", response_text)
            if uci_match:
                move_uci = uci_match.group(0)
                move = chess.Move.from_uci(move_uci)
                if move in self.board.legal_moves:
                    return move
                else:
                    return None
            else:
                return None
        except Exception as e:
            print(f"Error getting Gemini move: {e}")
            return None


if __name__ == "__main__":
    root = tk.Tk()
    ChessBoard(root)
    root.mainloop()
