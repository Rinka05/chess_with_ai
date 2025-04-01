# Chess AI Game

## Overview
This is a Chess game built using Python and Tkinter with AI-powered move suggestions. The AI can use either Stockfish, OpenAI's GPT, or Google's Gemini to generate moves. The game supports both human and AI players, and it announces the winner at the end.

![image](https://github.com/user-attachments/assets/eeccb31e-1733-4e37-84df-3209c5b8fb3c)


## Features
- Play against another human or AI (Stockfish, GPT, Gemini)
- Interactive GUI built with Tkinter
- API key input for GPT and Gemini integration
- Displays winner and loser at the end of the game
- Uses Stockfish for strong chess AI play
- Highlights selected piece and updates board dynamically

## Installation
### Prerequisites
Ensure you have the following installed:
- Python 3.8+
- Tkinter (comes pre-installed with Python)
- chess (python-chess library)
- PIL (Pillow library for images)

### Setup
1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/chess_with-ai.git
   cd chess_with-ai
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Download and place Stockfish in the project folder (Update the path in the code if necessary).
4. Run the game:
   ```sh
   python final.py
   ```

## Usage
1. Enter your OpenAI/Gemini API key if you want AI moves from GPT or Gemini.
2. Select the AI engine from the dropdown (Stockfish, GPT, or Gemini).
3. Click on pieces to move them according to standard chess rules.
4. The game will announce the winner when checkmate occurs.

## File Structure
```
chess-ai-game/
│-- assets/                # Piece images
│-- ai_engine.py           # Handles GPT/Gemini API calls
│-- final.py               # Main game file with GUI logic
│-- README.md              # Project documentation
```

## License
This project is open-source and free to use under the MIT License.

## Contributors
- Your Name Rinka05

## Contact
For any issues, reach out via GitHub Issues or email 12345rinka@gmail.com.

