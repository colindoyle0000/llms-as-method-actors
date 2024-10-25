"""Guess class for Vanilla GPT-o1 approach for storing information about a guess that is processed."""

import os
import logging
import random

from guess import BaseGuess
from utils_file import (
    get_root_dir
)
from utils_llm import (
    llm_call
)

from utils_string import get_timestamp

from submit import Submit

# Set up logger
logger = logging.getLogger('connections')

class GuessVanillao1(BaseGuess):
    """Guess class for Vanilla GPT-o1 approach for storing information about a guess that is processed."""
    
    def __init__(
        self,
        solve
    ):
        super().__init__()
        self.solve = solve
        self.puzzle = self.solve.puzzle
        self.num_of_guess = len(self.solve.guesses_processed)+1
        
        self.make_guess_responses = []
        self.make_guess_outputs = []
        self.select_responses = []
        self.select_outputs = []
    
    def process_guess(self):
        """Process the guess from start to finish for the Vanilla approach."""
        self.make_guess()
        self.select_and_validate_all()
        if self.guess_is_valid is True:
            self.guess_is_ready_to_submit = True
        else:
            self.guess_is_ready_to_submit = False

    def make_guess(self):
        """Ask LLM to make a guess."""
        self.make_guess_responses = []
        self.make_guess_outputs = []
        # Load the system prompt from a .txt file
        with open(os.path.join(
                get_root_dir(), 'data', 'prompts', 'vanilla_o1' , 'make_guess.txt'),
                'r', encoding='utf-8') as f:
            prompt_system = f.read()
        # If bad guesses have been made, add them to the system prompt
        bad_guesses_str = self.set_bad_guesses_str()
        prompt_system = prompt_system.replace('{bad_guesses}', bad_guesses_str)
        # Because o1 does not allow you to use a system prompt, turn system prompt into user prompt
        prompt_user = prompt_system
        # Create rest of user prompt
        # Create a list that shuffles the words that remain to be solved
        words_remain_shuffled = self.solve.words_remain_lst.copy()
        random.shuffle(words_remain_shuffled)
        # Create a string of the words that remain to be solved
        words_remain_str = " ".join(words_remain_shuffled)
        prompt_user += f"\n \n List of words in puzzle: {words_remain_str}"
        # Set up the prompts for the LLM
        prompts = [
            {"role": "user", "content": prompt_user},
        ]
        # Call the LLM
        llm_response = llm_call(
            model='o1-preview', prompts=prompts, settings=self.puzzle.llm_settings)
        self.make_guess_responses.append(llm_response)
        self.make_guess_outputs.append(llm_response.output)
        self.guess_rationale = llm_response.output
        logger.debug("Made guess: /n /n %s", llm_response.output)

    def select_guess(self):
        """Call LLM to select the guess."""
        # Load the system prompt from a .txt file
        with open(os.path.join(
                get_root_dir(), 'data', 'prompts', 'vanilla_o1', 'select.txt'),
                'r', encoding='utf-8') as f:
            prompt_system = f.read()
        # Within the system prompt, replace the placeholder {notes} with the notes_str
        prompt_system = prompt_system.replace("{notes}", self.guess_rationale)
        # Create a user prompt
        # Create a list that shuffles the words that remain to be solved
        words_remain_shuffled = self.solve.words_remain_lst.copy()
        random.shuffle(words_remain_shuffled)
        # Create a string of the words that remain to be solved
        words_remain_str = " ".join(words_remain_shuffled)
        prompt_user = f"Please select the guess to submit for this puzzle: {words_remain_str}"
        # Set up prompts for the LLM
        prompts = [
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": prompt_user},
        ]
        # Call the LLM
        llm_response = llm_call(
            model=self.puzzle.llm_settings.model, prompts=prompts, settings=self.puzzle.llm_settings)
        logger.debug("Select guess: /n /n %s", llm_response.output)
        return llm_response
    
    def select_all(self):
        """Run each of the steps to select the guess."""
        self.select_responses = []
        self.select_outputs = []
        llm_response = self.select_guess()
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
        # Check if the guess_lst has four words
        if len(guess_lst) != 4:
            logger.warning(
                "Guess does not contain four words. Trying to get LLM to fix...")
            llm_response = self.select_fix(guess)
            # Turn the guess into a list of words and fix formatting
            guess = llm_response.output
            # Remove "Output:" from guess if it appears in the string
            guess = guess.replace("Output:", "").strip()
            guess = guess.replace("Response:", "").strip()
            guess_lst = self.puzzle.split_puzzle_text(guess, 4, "***")
            if len(guess_lst) != 4:
                logger.warning(
                    "Failed to fix guess. Guess still does not contain four words.")
            else:
                logger.info("Fixed guess!")
        self.guess_lst = guess_lst
        logger.info("Selected guess: %s", " ".join(guess_lst))
        
    def select_and_validate_all(self):
        """Select the guess and validate it for errors."""
        self.select_all()
        self.validate_all()    