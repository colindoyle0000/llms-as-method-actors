"""Class for submitting an guess for part of the answer to the puzzle."""


import logging

from src.baseclass import BaseClass


# Set up logger
logger = logging.getLogger('method-actors')


class Submit(BaseClass):
    """Submit class for submitting an guess for part of the answer to the puzzle."""

    def __init__(
            self,
            guess
    ):

        self.guess = guess
        self.puzzle = guess.puzzle
        self.solve = guess.solve

    def submit_guess(self):
        """Submit a guess for part of the answer to the puzzle."""
        logger.info("Submitting guess%s: %s",
                    self.guess.num_of_guess, self.guess.guess_lst)
        # If the solution list exists, check if the guess is correct
        if self.puzzle.solution_lst is not None:
            guess_set = set(self.guess.guess_lst)
            if any(guess_set.issubset(set(solution)) for solution in self.puzzle.solution_lst):
                logger.info("Correct guess! Woohoo!")
                return True
            else:
                logger.info("Incorrect guess! Dang!")
                return False
        else:
            logger.info("No solution to check guess against.")
            return True

    def check_if_one_away(self):
        """Check if the guess is one away from the solution."""
        logger.info("Checking if guess is one away from solution.")
        # If the solution list exists, check if the guess is one away
        if self.puzzle.solution_lst is not None:
            for solution in self.puzzle.solution_lst:
                # Check if the guess is one away from the solution
                if len(set(self.guess.guess_lst).symmetric_difference(set(solution))) == 2:
                    logger.info("Guess is one away from the solution.")
                    return True
        logger.info("Guess is not one away from the solution.")
        return False
