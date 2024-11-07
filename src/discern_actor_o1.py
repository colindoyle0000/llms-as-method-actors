"""Discerno1 class for discerning valuable answers from brainstorming notes for Actor-o1 approach."""
import os
import logging
import random

from src.baseclass import BaseClass
from src.utils_file import (
    get_root_dir
)
from src.utils_llm import (
    llm_call
)

from src.utils_tokens import (
    list_to_token_list,
    num_tokens
)

from src.utils_string import get_timestamp

# Set up logger
logger = logging.getLogger('connections')


class Discerno1(BaseClass):
    """Discerno1 class for discerning valuable answers from brainstorming notes."""

    def __init__(
        self,
        guess,
        brainstorm_responses,
    ):
        self.guess = guess
        self.puzzle = guess.puzzle
        self.solve = guess.solve
        # LLM settings for discerning
        self.llm_settings = self.puzzle.llm_settings
        # Brainstorm responses
        self.brainstorm_responses = brainstorm_responses
        # Select guess
        self.select_responses = []
        self.select_outputs = []
        # Submit guess
        self.submit_guess = True

    def set_llm_temperature(self):
        """Set the LLM temperature setting for discern.
        Note that this is not currently used in the code. It is here for any future experiments in changing the temperature for brainstorming process.
        """
        self.llm_settings.temperature = 0.6
        logger.info("Setting LLM temperature to %s for discerning.",
                    self.llm_settings.temperature)

    def select(self, notes_str: str):
        """Select the best discerned guess."""
        # Load the system prompt from a .txt file
        with open(os.path.join(
                get_root_dir(), 'data', 'prompts', 'actor_o1', 'select.txt'),
                'r', encoding='utf-8') as f:
            prompt_system = f.read()
        # Within the system prompt, replace the placeholder {notes} with the notes_str
        prompt_system = prompt_system.replace("{notes}", notes_str)
        # If bad guesses have been made, add them to the system prompt
        bad_guesses_str = self.guess.set_bad_guesses_str()
        prompt_system = prompt_system.replace('{bad_guesses}', bad_guesses_str)
        # Create a user prompt
        prompt_user = "Please select the best guess to submit."
        # Set up prompts for the LLM
        prompts = [
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": prompt_user},
        ]
        # Call the LLM
        llm_response = llm_call(
            model=self.llm_settings.model, prompts=prompts, settings=self.llm_settings)
        return llm_response

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
            model=self.llm_settings.model, prompts=prompts, settings=self.llm_settings)
        return llm_response

    def select_all(self):
        """Select the best discerned guess."""
        self.select_responses = []
        self.select_outputs = []
        # Run the select function to get a guess from the LLM
        logger.info("Selecting the best guess...")
        notes_str = ""
        for response in self.brainstorm_responses:
            notes_str += response.output
            notes_str += "/n *** /n"
        llm_response = self.select(notes_str)
        self.select_responses.append(llm_response)
        self.select_outputs.append(llm_response.output)
        # Turn the guess into a list of words and fix formatting
        guess = llm_response.output
        # Remove "Output:" or "Response:" from guess if it appears in the string
        guess = guess.replace("Output:", "").strip()
        guess = guess.replace("Response:", "").strip()
        guess_lst = self.puzzle.split_puzzle_text(guess, 4, "***")
        
        # Sort the guess_lst in alphabetical order
        guess_lst = sorted(guess_lst)  
        
        if len(guess_lst) != 4:
            logger.warning(
                "Guess does not contain four words. Trying to get LLM to fix...")
            llm_response = self.select_fix(guess)
            # Turn the guess into a list of words and fix formatting
            guess = llm_response.output
            # Remove "Output:" from guess if it appears in the string
            guess = guess.replace("Output:", "").strip()
            guess_lst = self.puzzle.split_puzzle_text(guess, 4, "***")
            if len(guess_lst) != 4:
                logger.warning(
                    "Failed to fix guess. Guess still does not contain four words.")
            else:
                logger.info("Fixed guess!")
        
        self.guess.guess_lst = guess_lst
        logger.info("Selected guess: %s", " ".join(guess_lst))

    def validate_guess_format(self):
        """Validate the guess formatting."""
        # If the guess list has more or less than four items, log a warning
        if len(self.guess.guess_lst) != 4:
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
        # - The guess is not already in logically_bad_guesses_lst
        
        guess_set = set(self.guess.guess_lst)
        if not guess_set.issubset(set(self.solve.words_remain_lst)):
            logger.info(
                "Invalid guess. Guess contains words not in words_remain_lst.")
            return False
        for bad_guess in self.solve.bad_guesses_lst:
            if guess_set == set(bad_guess):
                logger.info(
                    "Invalid guess: Guess is already in bad_guesses_lst.")
                return False
        for logically_bad_guess in self.solve.logically_bad_guesses_lst:
            if guess_set == set(logically_bad_guess):
                logger.info(
                    "Invalid guess: Guess is already in logically_bad_guesses_lst.")
                return False
        logger.info("Valid guess content.")
        return True


    def select_and_validate_all(self):
        """Select the best guess and validate it for errors."""

        # Select guess
        self.select_all()

        # Validate the guess formatting, and if it is not valid, try again
        attempts = 1
        while self.validate_guess_format() is False or self.validate_guess_content() is False:
            if attempts > 2:
                logger.warning(
                    "Failed to select a correctly formatted guess after retrying.")
                return False
            logger.warning("Trying to select guess again...")
            self.select_all()
            attempts += 1
        return True

    def make_ready_to_submit(self):
        """Make the guess ready to submit by summarizing rationale."""
        logger.info("Making guess ready to submit.")
        self.guess.guess_rationale = ""
        notes_str = ""
        for response in self.brainstorm_responses:
            notes_str += response.output
            notes_str += "\n *** \n"
        self.guess.guess_rationale = notes_str
        self.guess.guess_is_ready_to_submit = True
