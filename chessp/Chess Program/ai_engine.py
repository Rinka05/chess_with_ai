import openai
import os 

def set_openai_key(api_key):
    openai.api_key = os.getenv("OPENAI_API_KEY")

def get_gpt_move(fen):
    """
    Get the best move suggestion from GPT-4 based on the FEN representation of the board.
    """
    prompt = f"Given the following chess position in FEN notation: {fen}, suggest the best move in UCI format."
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a chess engine."},
                  {"role": "user", "content": prompt}]
    )
    
    move = response["choices"][0]["message"]["content"].strip()
    return move
