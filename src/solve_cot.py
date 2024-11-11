"""SolveCot class is a class the  solves the Connections puzzle using a Chain-of-Thoughts approaches.
"""

import logging
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
from src.guess_cot import GuessCot

# Set up logger
logger = logging.getLogger('method-actors')

class SolveCot(BaseSolver):
    """SolveCot class is a class the  solves the Connections puzzle using a Chain-of-Thoughts approach.
    """
    
    def __init__(self,
                 puzzle,
                cot_scripted=False
                 ):
        super().__init__()
        self.puzzle = puzzle
        self.words_remain_lst = puzzle.words_lst
        self.cot_scripted = cot_scripted
    
    def set_path_cot(self):
        """Set the path for saving data to file."""
        if self.cot_scripted is False:
            self.set_path(name="solve_cot")
        else:
            self.set_path(name="solve_cot_scripted")
    
    def solve_puzzle_cot(self):
        """Solve the puzzle using the CoT method.
        """
        start_time = time.time()
        if self.cot_scripted is False:
            logger.info("Solving puzzle using CoT approach. \n Words in puzzle: \n %s \n Solution: \n %s",
                        self.puzzle.words_lst, self.puzzle.solution_lst)
        else:
            logger.info("Solving puzzle using CoT (Scripted) approach. \n Words in puzzle: \n %s \n Solution: \n %s",
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
            
            # If the guesses ready to submit list has any guesses in it, submit the guess.
            if len(self.guesses_ready_to_submit) > 0:
                for guess in self.guesses_ready_to_submit:
                    guess.do_submit()
                    self.guesses_submitted.append(guess)
                    # Remove from the list of guesses ready to submit
                    self.guesses_ready_to_submit.remove(guess)
                    if guess.guess_is_correct is True:
                        self.good_guesses.append(guess)
                        self.good_guesses_lst.append(guess.guess_lst)
                        # Extend the words_excluded_lst to include each word in the guess_lst
                        self.words_solved_lst.extend(guess.guess_lst)
                        # Make words_remain_lst be words_lst minus words_solved_lst
                        self.words_remain_lst = list(
                            set(self.puzzle.words_lst) - set(self.words_solved_lst))
                        # Iterate over a copy of the list using slicing [:]
                        for guess_ready in self.guesses_ready_to_submit[:]:
                            if all(word in self.words_remain_lst for word in guess_ready.guess_lst):
                                logger.info("Guess ready to submit still valid: %s",
                                            guess_ready.guess_lst)
                            else:
                                logger.info("Guess ready to submit no longer valid: %s",
                                            guess_ready.guess_lst)
                                self.guesses_ready_to_submit.remove(guess_ready)
                    else:
                        self.bad_guesses.append(guess)
                        self.bad_guesses_lst.append(guess.guess_lst)
                        logger.debug("Number of bad guesses: %s",
                                    len(self.bad_guesses_lst))
          

            # If there are only four words left to solve, submit the guess that solves them.
            if len(self.good_guesses) == 3:
                logger.info("Only one possible solution left. Submitting.")
                self.current_guess = GuessCot(self)
                self.current_guess.guess_lst = self.words_remain_lst
                self.current_guess.do_submit()
                if self.current_guess.guess_was_submitted is True:
                    self.guesses_submitted.append(self.current_guess)
                    if self.current_guess.guess_is_correct is True:
                        self.good_guesses.append(self.current_guess)
                        self.good_guesses_lst.append(
                            self.current_guess.guess_lst)
                        # Extend the words_excluded_lst to include each word in the guess_lst
                        self.words_solved_lst.extend(
                            self.current_guess.guess_lst)
                        # Make words_remain_lst be words_lst minus words_solved_lst
                        self.words_remain_lst = list(
                            set(self.puzzle.words_lst) - set(self.words_solved_lst))
                    else:
                        self.bad_guesses.append(self.current_guess)
                        self.bad_guesses_lst.append(
                            self.current_guess.guess_lst)
                        logger.debug("Number of bad guesses: %s",
                                     len(self.bad_guesses_lst))
            self.check_end_game_conditions()


            # If the puzzle is not done, create a new guess
            if self.end_game is False:
                # Create a new guess
                self.current_guess = GuessCot(self)
                guesses_ready_to_submit_str = ""
                for guess in self.guesses_ready_to_submit:
                    guess_str = "Guess: \n"
                    guess_str += " ".join(guess.guess_lst)
                    guess_str += "\n Rationale: \n"
                    guess_str += guess.guess_rationale
                    guesses_ready_to_submit_str += f"{guess_str}\n"
                logger.info("Starting New Guess! \n Current guess number: %s \n %s words remaining: \n %s  \n %s good guesses so far: \n %s \n %s bad guesses so far: \n %s \n %s guesses ready to submit: \n %s",
                            self.current_guess.num_of_guess, len(self.words_remain_lst), self.words_remain_lst, len(self.good_guesses_lst), self.good_guesses_lst, len(self.bad_guesses_lst), self.bad_guesses_lst, len(self.guesses_ready_to_submit), guesses_ready_to_submit_str)
                self.current_guess.process_guess()
                self.guesses_processed.append(self.current_guess)
                # If the current guess failed because of an error, start over from the beginning.
                if self.current_guess.guess_is_valid is False:
                    logger.info(
                        "Guess is not a valid guess to submit because of a formatting or content error. Starting over.")
                # If the current guess is ready to submit, add it to the list of guesses ready to submit.
                if self.current_guess.guess_is_ready_to_submit is True:
                    self.guesses_ready_to_submit.append(self.current_guess)
                    logger.info("Guess is ready to submit. Adding to list.")

        self.solve_time = time.time() - start_time
        minutes, seconds = divmod(self.solve_time, 60)
        minutes = int(minutes)
        seconds = int(seconds)
        logger.info("Puzzle finished in %s minutes and %s seconds.",
                    minutes, seconds)
        self.save_results_dict()
        if self.puzzle.solution_lst is not None:
            self.save_summary()
        else:
            self.save_summary_no_solution()
        if self.cot_scripted is False:
            self.save_attributes(filepath_pkl=self.path_pkl,
                                 name=f"puzzle_{self.puzzle.number}_cot")
        else:
            self.save_attributes(filepath_pkl=self.path_pkl,
                                 name=f"puzzle_{self.puzzle.number}_cot_scripted")
