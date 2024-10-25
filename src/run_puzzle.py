import logging

import setup_logging
from src.puzzle_4o import Puzzle
from baseclass import BaseClass
from get_puzzle_info import extract_puzzle_data_from_url

setup_logging.setup_logger()
logger = logging.getLogger('connections')
logger.info('This is an info message')


def main():

    # Get the puzzle information from the web
    # Get the puzzle number from the user
    number = int(input('Enter the puzzle number: '))
    url = f"https://connections.swellgarfo.com/nyt/{number}"
    puzzle_str, number, solution_lst = extract_puzzle_data_from_url(url)
    style = 'quick'

    # Define the list of models
    models = [
        'gpt-4o',
        'gpt-4o-mini',
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
    model_index = int(
        input('Enter the number corresponding to the model: ')) - 1
    model = models[model_index]

    # Setup logging
    setup_logging.setup_logger()
    logger = logging.getLogger('connections')
    logger.info('This is an info message')

    # Initialize puzzle
    puzzle = Puzzle(words_str=puzzle_str, number=number,
                    solution_lst=solution_lst, style=style, model=model)
    puzzle.setup_puzzle()
    # Try to solve the puzzle, save if an error occurs
    try:
        puzzle.solve_puzzle_thorough()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        print("An error occurred while solving the puzzle. Saving...")
        puzzle.save_attributes(filepath_pkl=puzzle.path_pkl,
                               name=f"puzzle_{puzzle.number}")


if __name__ == '__main__':
    main()
