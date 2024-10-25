import logging

import setup_logging
from src.experiment_4o import Experiment

setup_logging.setup_logger()
logger = logging.getLogger('connections')
logger.info('This is an info message')

def main():

    # List of puzzle numbers
    puzzle_numbers = [420,435]
    
    # Initialize the experiment
    experiment = Experiment(puzzle_numbers=puzzle_numbers)
    experiment.set_path()
    experiment.set_puzzles()
    experiment.setup_puzzles()
    experiment.solve_unfinished_puzzles()
    experiment.save_results_dict()
    experiment.save_attributes(filepath_pkl=experiment.path_pkl,
                             name=f"experiment_test")
    
if __name__ == '__main__':
    main()
