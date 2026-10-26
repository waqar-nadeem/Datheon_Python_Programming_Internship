#!/usr/bin/env python3
"""
Terminal-based Hangman Game
Python Programming Internship - Task 1

Features:
- Random word selection from a word list
- ASCII art gallows that updates with each incorrect guess
- Tracks previously guessed letters
- No penalty for duplicate guesses
- Maximum 6 incorrect guesses
"""

import random
import os
import sys

# ---------------------------------------------------------------------------
# ASCII Art Stages (0 = no mistakes → 6 = full hangman / game over)
# ---------------------------------------------------------------------------
HANGMAN_STAGES = [
    # 0 mistakes
    r"""
      +---+
      |   |
          |
          |
          |
          |
    =========
    """,
    # 1 mistake - head
    r"""
      +---+
      |   |
      O   |
          |
          |
          |
    =========
    """,
    # 2 mistakes - body
    r"""
      +---+
      |   |
      O   |
      |   |
          |
          |
    =========
    """,
    # 3 mistakes - one arm
    r"""
      +---+
      |   |
      O   |
     /|   |
          |
          |
    =========
    """,
    # 4 mistakes - both arms
    r"""
      +---+
      |   |
      O   |
     /|\  |
          |
          |
    =========
    """,
    # 5 mistakes - one leg
    r"""
      +---+
      |   |
      O   |
     /|\  |
     /    |
          |
    =========
    """,
    # 6 mistakes - both legs (game over)
    r"""
      +---+
      |   |
      O   |
     /|\  |
     / \  |
          |
    =========
    """,
]


def clear_screen():
    """Clear the terminal screen for a cleaner display."""
    os.system("cls" if os.name == "nt" else "clear")


def load_words(filename="words.txt"):
    """
    Load words from a text file (one word per line).
    Filters for Hangman-friendly words (4–10 letters, alphabetic only).
    Falls back to a built-in list if the file is missing.
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            words = [line.strip().lower() for line in f if line.strip()]
        # Keep only pure alphabetic words of good Hangman length
        words = [w for w in words if w.isalpha() and 4 <= len(w) <= 10]
        if words:
            return words
    except FileNotFoundError:
        pass

    # Fallback word list
    return [
        "python", "hangman", "programming", "computer", "keyboard",
        "algorithm", "function", "variable", "developer", "software",
        "elephant", "giraffe", "penguin", "dolphin", "kangaroo",
        "adventure", "mystery", "treasure", "journey", "explorer",
        "mountain", "ocean", "forest", "desert", "volcano",
        "guitar", "piano", "violin", "trumpet", "drummer",
        "pizza", "burger", "sushi", "pancake", "chocolate",
        "galaxy", "planet", "comet", "asteroid", "nebula",
    ]


def display_game_state(secret_word, guessed_letters, mistakes, stages):
    """Print the current game state: ASCII art, masked word, guessed letters."""
    clear_screen()
    print("=" * 50)
    print("           H A N G M A N")
    print("=" * 50)
    print(stages[mistakes])
    print()

    # Build masked word: show letter if guessed, else '_'
    masked = " ".join(
        letter.upper() if letter in guessed_letters else "_"
        for letter in secret_word
    )
    print(f"  Word:  {masked}")
    print()
    print(f"  Mistakes: {mistakes}/6")
    print(f"  Guessed letters: {', '.join(sorted(guessed_letters)).upper() or '(none)'}")
    print("=" * 50)


def get_valid_guess(guessed_letters):
    """Prompt the user for a single letter that has not been guessed yet."""
    while True:
        guess = input("\nEnter a letter: ").strip().lower()

        if len(guess) != 1:
            print("  → Please enter exactly one letter.")
            continue
        if not guess.isalpha():
            print("  → Please enter a letter (A-Z).")
            continue
        if guess in guessed_letters:
            print(f"  → You already guessed '{guess.upper()}'. Try a different letter.")
            continue

        return guess


def play_hangman(word_list):
    """Main game loop for one round of Hangman."""
    secret_word = random.choice(word_list)
    guessed_letters = set()
    mistakes = 0
    max_mistakes = 6

    while mistakes < max_mistakes:
        display_game_state(secret_word, guessed_letters, mistakes, HANGMAN_STAGES)

        # Check win condition before asking for another guess
        if all(letter in guessed_letters for letter in secret_word):
            print("\n🎉 Congratulations! You guessed the word!")
            print(f"   The word was: {secret_word.upper()}")
            return True

        guess = get_valid_guess(guessed_letters)
        guessed_letters.add(guess)

        if guess in secret_word:
            print(f"\n  ✓ Good job! '{guess.upper()}' is in the word.")
        else:
            mistakes += 1
            print(f"\n  ✗ Sorry, '{guess.upper()}' is not in the word.")

        # Small pause so the player can read the feedback
        input("  Press Enter to continue...")

    # Out of attempts
    display_game_state(secret_word, guessed_letters, mistakes, HANGMAN_STAGES)
    print("\n💀 Game Over! You ran out of attempts.")
    print(f"   The word was: {secret_word.upper()}")
    return False


def main():
    """Entry point: load words and run the game with replay option."""
    word_list = load_words()
    if not word_list:
        print("Error: No words available to play.")
        sys.exit(1)

    print("Welcome to Hangman!")
    print(f"Loaded {len(word_list)} words.\n")

    while True:
        play_hangman(word_list)

        again = input("\nWould you like to play again? (y/n): ").strip().lower()
        if again not in ("y", "yes"):
            print("\nThanks for playing! Goodbye.")
            break


if __name__ == "__main__":
    main()
