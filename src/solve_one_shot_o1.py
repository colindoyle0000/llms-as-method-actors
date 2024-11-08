"""SolveOneShoto1 class is a class the  solves the Connections puzzle using a one-shot approach with GPT-o1.
"""

import logging
import os
import time

from src.utils_llm import (
    LLMSettings,
    llm_call
)
from src.baseclass import BaseClass
from src.solve import BaseSolver
from src.utils_string import (
    get_date,
    get_timestamp
)
from src.utils_file import (
    get_root_dir
)
from src.guess_oneshot_o1 import GuessOneShoto1


# Set up logger
logger = logging.getLogger('connections')

class SolveOneShoto1(BaseSolver):
    """SolveOneShoto1 class is a class the  solves the Connections puzzle using a one-shot approach with GPT-o1.
    """
    
    def __init__(self,
                 puzzle
                 ):
        super().__init__()
        self.puzzle = puzzle
        self.words_remain_lst = puzzle.words_lst
    
    def set_path_oneshoto1(self):
        """Set the path for saving data to file."""
        self.set_path(name="solve_oneshot_o1")
    
    def solve_puzzle_oneshoto1(self):
        """Solve the puzzle using the oneshoto1 method.
        """
        start_time = time.time()
        logger.info("Solving puzzle using One-Shot o1 approach. \n Words in puzzle: \n %s \n Solution: \n %s",
                    self.puzzle.words_lst, self.puzzle.solution_lst)

        if len(self.guesses_processed) == 0:

            self.current_guess = None
            self.guesses_processed = []
            self.guesses_ready_to_submit = []
            self.guesses_submitted = []
            self.good_guesses = []
            self.good_guesses_lst = []
            self.bad_guesses = []
            self.bad_guesses_lst = []
            self.end_game = False
            self.success = False
        while self.end_game is False:
            self.save_attributes(filepath_pkl=self.path_pkl,
                                 name=f"puzzle_{self.puzzle.number}")
            
            # Create a new guess
            self.current_guess = GuessOneShoto1(self)
            guesses_ready_to_submit_str = ""
            logger.info("Starting New Guess! \n Current guess number: %s \n %s words remaining: \n %s  \n %s good guesses so far: \n %s \n %s bad guesses so far: \n %s \n %s guesses ready to submit: \n %s",
                        self.current_guess.num_of_guess, len(self.words_remain_lst), self.words_remain_lst, len(self.good_guesses_lst), self.good_guesses_lst, len(self.bad_guesses_lst), self.bad_guesses_lst, len(self.guesses_ready_to_submit), guesses_ready_to_submit_str)
            self.current_guess.process_guess()
            self.guesses_processed.append(self.current_guess)
            self.guesses_submitted.append(self.current_guess)
            self.good_guesses.append(self.current_guess)
            self.good_guesses_lst.append(self.current_guess.guess_lst)
            
            self.end_game = True

        self.solve_time = time.time() - start_time
        minutes, seconds = divmod(self.solve_time, 60)
        minutes = int(minutes)
        seconds = int(seconds)
        logger.info("Puzzle finished in %s minutes and %s seconds.",
                    minutes, seconds)
        self.save_results_dict()
        self.save_summary_oneshoto1()
        self.save_attributes(filepath_pkl=self.path_pkl,
                             name=f"puzzle_{self.puzzle.number}_one_shot_o1")

    def save_summary_oneshoto1(self):
        timestamp = get_timestamp()
        filename = f"summary_puzzle{self.puzzle.number}_o1-preview_{timestamp}.md"
        with open(
            os.path.join(self.path_md, filename),
            'w', encoding='utf-8'
        ) as f:
            f.write(f"# Summary of Puzzle {self.puzzle.number}\n\n")
            f.write(f"Date: {get_date()}\n")
            f.write(f"Model: o1-preview\n")
            minutes, seconds = divmod(self.solve_time, 60)
            f.write(
                f"Took {int(minutes)} minutes and {int(seconds)} seconds \n\n")

            f.write("## Guess\n\n")
            for guess in self.guesses_submitted:
                f.write(f"### Guess {guess.num_of_guess}\n\n")
                guess_str = " ".join(guess.guess_lst)
                f.write(f"{guess_str}\n\n")
            f.write("## Solution\n\n")
            for solution in self.puzzle.solution_lst:
                # Turn the solution into a string
                solution_str = " ".join(solution)
                f.write(f"{solution_str}\n\n")
        filepath = os.path.join(self.path_md, filename)
        logger.info("Saved summary to %s", filepath)
