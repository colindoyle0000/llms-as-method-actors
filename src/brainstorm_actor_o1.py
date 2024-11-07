"""Brainstormo1 class for brainstorming possible solutions to the puzzle under Actor-o1 approach."""

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

from src.utils_string import get_timestamp

# Set up logger
logger = logging.getLogger('connections')


class Brainstormo1(BaseClass):
    """Brainstormo1 class for brainstorming possible solutions to the puzzle under Actor-o1 approach."""

    def __init__(
        self,
        guess
    ):
        self.guess = guess
        self.puzzle = guess.puzzle
        self.solve = guess.solve

        # Brainstorming responses and outputs
        self.brainstorm_responses = []
        self.brainstorm_outputs = []
        # LLM settings for brainstorming
        self.llm_settings = self.puzzle.llm_settings

    def set_llm_temperature(self, temperature=0.0):
        """Set the LLM temperature setting for brainstorming.
        Note that this is not currently used in the code. It is here for any future experiments in changing the temperature for brainstorming process.
        """
        self.llm_settings.temperature = temperature
        logger.info("Setting LLM temperature to %s for brainstorming.",
                    self.llm_settings.temperature)

    def brainstorm(self):
        """Ask LLM to brainstorm a possible solution to the puzzle."""
        # Load the system prompt from a .txt file
        # Pick a random brainstorm prompt
        # Pick a random number 0, 1, or 2
        random_num = random.randint(0, 2)
        brainstorm_str = f"brainstorm_{random_num}.txt"
        with open(os.path.join(
                get_root_dir(), 'data', 'prompts', 'actor_o1', brainstorm_str),
                'r', encoding='utf-8') as f:
            prompt_system = f.read()
        # If bad guesses have been made, add them to the system prompt
        bad_guesses_str = self.guess.set_bad_guesses_str()
        if len(bad_guesses_str) > 0:
            # Add text to end of bad_guesses_str
            bad_guesses_str += "\n \n You should reject any guess that has the same four words as a guess that we already know is incorrect. \n"            
        prompt_system = prompt_system.replace('{bad_guesses}', bad_guesses_str)
        # Because o1 does not allow you to use a system prompt, turn system prompt into user prompt
        prompt_user = prompt_system
        # Add text to user prompt
        # Create a list that shuffles the words that remain to be solved
        words_remain_shuffled = self.solve.temp_words_remain_lst.copy()
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
            model='o1-preview', prompts=prompts, settings=self.llm_settings)
        return llm_response

    def brainstorm_all(self):
        """Brainstorm a bunch of possible solutions to the puzzle."""
        self.brainstorm_responses = []
        self.brainstorm_outputs = []
        response = self.brainstorm()
        self.brainstorm_responses.append(response)
        self.brainstorm_outputs.append(response.output)
        return self.brainstorm_responses
