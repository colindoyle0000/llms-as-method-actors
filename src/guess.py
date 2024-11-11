"""Base class for storing information about a guess that is processed."""

import os
import logging

from src.baseclass import BaseClass
from src.utils_file import (
    get_root_dir
)
from src.utils_llm import (
    llm_call
)

from src.submit import Submit

# Set up logger
logger = logging.getLogger('method-actors')


class BaseGuess(BaseClass):
    """Base class for storing information about a guess that is processed."""

    def __init__(
        self
    ):
        super().__init__()  # Call the constructor of BaseClass

        self.puzzle = None
        self.solve = None
        self.num_of_guess = None

        self.guess_lst = []
        self.good_options_for_guess = True
        self.guess_is_valid = True
        self.guess_is_ready_to_submit = False
        self.guess_rationale = ""
        self.guess_was_submitted = False
        self.guess_is_correct = False
        self.guess_was_one_away = False

        # Class instance of submit
        self.submit = None

    def do_submit(self):
        """Submit the guess for part of the answer to the puzzle."""
        self.submit = Submit(self)
        self.guess_was_submitted = True
        if self.submit.submit_guess() is True:
            self.guess_is_correct = True
        else:
            self.guess_is_correct = False
            if self.puzzle.solution_lst is not None:
                if self.submit.check_if_one_away() is True:
                    self.guess_was_one_away = True
                else:
                    self.guess_was_one_away = False

    def set_bad_guesses_str(self):
        """Set the string for the bad guesses."""
        bad_guesses = " "

        # Check if there are any bad guesses
        if len(self.solve.bad_guesses_lst) > 0:
            # Check to make sure at least one bad guess is still viable (all words are in the word remain list)
            count_viable = 0
            for guess in self.solve.bad_guesses_lst:
                if all(word in self.solve.words_remain_lst for word in guess):
                    count_viable += 1
            if count_viable > 0:
                bad_guesses += "The following guesses were incorrect: \n"
                for guess in self.solve.bad_guesses_lst:
                    if all(word in self.solve.words_remain_lst for word in guess):
                        guess_str = " ".join(guess)
                        # Add guess_str to bad_guesses
                        bad_guesses += f"{guess_str}\n"
        return bad_guesses

    
    def select_fix(self, guess_str: str):
        """If the guess does not contain four words, ask the LLM to fix it."""
        # Load the system prompt from a .txt file
        with open(os.path.join(
                get_root_dir(), 'data', 'prompts', 'select_fix.txt'),
                'r', encoding='utf-8') as f:
            prompt_system = f.read()
        # Create a user prompt
        prompt_user = f"Please fix the guess: {guess_str}"
        # Set up prompts for the LLM
        prompts = [
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": prompt_user},
        ]
        # Call the LLM
        llm_response = llm_call(
            model=self.puzzle.llm_settings.model, prompts=prompts, settings=self.puzzle.llm_settings)
        return llm_response
    

    def validate_guess_format(self):
        """Validate the guess formatting."""
        # If the guess list has more or less than four items, log a warning
        if len(self.guess_lst) != 4:
            logger.warning("Invalid guess. Guess does not contain four words.")
            return False
        else:
            logger.info("Valid guess format. Guess contains four words.")
            return True
        
    def validate_guess_content(self):
        """Check to make sure the guess content can be submmitted."""
        # Conditions for valid guess content:
        # - The guess only contains words from the words_remain_lst
        # - The guess is not already in bad_guesses_lst
        guess_set = set(self.guess_lst)
        if not guess_set.issubset(set(self.solve.words_remain_lst)):
            logger.info(
                "Invalid guess. Guess contains words not in words_remain_lst.")
            return False
        for bad_guess in self.solve.bad_guesses_lst:
            if guess_set == set(bad_guess):
                logger.info(
                    "Invalid guess: Guess is already in bad_guesses_lst.")
                return False
        logger.info("Valid guess content.")
        return True
    
    def validate_all(self):
        """Run each of the steps to validate the guess."""
        self.guess_is_valid = True
        if self.validate_guess_format() is False:
            self.guess_is_valid = False
        if self.validate_guess_content() is False:
            self.guess_is_valid = False