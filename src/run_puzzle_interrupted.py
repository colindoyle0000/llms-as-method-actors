import logging

import setup_logging
from src.puzzle_4o import Puzzle

setup_logging.setup_logger()
logger = logging.getLogger('connections')
logger.info('This is an info message')


def main():

    filename = "/Users/colindoyle/Documents/_research_icloud_sync/how_to_think/python/connections/outputs/415/gpt-4o/2024_07_30/pkl/puzzle_415.pkl"
    # Setup logging
    setup_logging.setup_logger()
    logger = logging.getLogger('connections')
    logger.info('This is an info message')

    # Load puzzle
    puzzle = Puzzle(words_str="", number=0,
                    solution_lst=[], style='quick', model='model')
    puzzle.load_attributes(filename=filename)

    # if solution list length is not 4, set solution list
    if len(puzzle.solution_lst) != 4:
        logger.info(
            "No solution list found in puzzle object. Setting solution list.")
        solution_lst = ["""
        NEAT
        NIFTY
        SUPER
        SWELL""", """
        ELABORATE
        EXPAND
        EXPLAIN
        SPECIFY""", """
        FACILITY
        FLAIR
        GIFT
        KNACK""", """
        BLOCK
        COMPLEX
        COMPOUND
        DEVELOPMENT"""]

        puzzle.set_solution(solution_lst)

    # For each guess in the puzzle, set guess.puzzle to the puzzle object
    logger.info("Setting puzzle object for each guess.")
    for guess in puzzle.guesses_processed:
        guess.puzzle = puzzle
    logger.info("Puzzle object set for each guess.")
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
