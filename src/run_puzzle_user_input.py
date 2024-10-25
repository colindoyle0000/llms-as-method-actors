import os
import sys
import logging
import argparse
from src import setup_logging
from src.puzzle_4o import Puzzle
from src.guess import Guess
from src.brainstorm import Brainstorm
from src.discern import Discern
from src.submit import Submit
from src.utils_llm import LLMSettings

def main():
    # Prompt user for input
    puzzle_str = input('Enter the puzzle words separated by newlines: ')
    number = int(input('Enter the puzzle number: '))
    num_groups = 4
    
    solution_lst = []
    for i in range(num_groups):
        group = input(f'Enter the solution strings for group {i+1} separated by newlines: ')
        solution_lst.append(f'"""{group}"""')
    
    style = input('Enter the puzzle style (default: quick): ') or 'quick'

    # Define the list of models
    models = [
        'gpt-4o',
        'gpt-4',
        'claude-3-5-sonnet-20240620',
        'claude-3-opus-20240229',
        'gemini-1.5-pro'
    ]
    
    # Display the list of models to the user
    print("Select the model to use:")
    for idx, model in enumerate(models, start=1):
        print(f"{idx}. {model}")
    
    # Prompt the user to select a model
    model_index = int(input('Enter the number corresponding to the model: ')) - 1
    model = models[model_index]

    # Setup logging
    setup_logging.setup_logger()
    logger = logging.getLogger('connections')
    logger.info('This is an info message')

    # Initialize puzzle
    puzzle = Puzzle(words_str=puzzle_str, number=number,
                    solution_lst=solution_lst, style=style, model=model)
    puzzle.setup_puzzle()
    puzzle.solve_puzzle_thorough()

if __name__ == '__main__':
    main()