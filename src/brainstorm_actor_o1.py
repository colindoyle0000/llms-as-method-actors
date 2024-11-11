"""
Brainstormo1 class for brainstorming possible solutions to the puzzle under Actor-o1 approach.
"""
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
    """Class for generating brainstorming solutions using the Actor-o1 approach.
    
    This class provides methods to generate solutions by interacting with an LLM,
    using specific prompts tailored to the Actor-o1 framework.
    """

    def __init__(
        self,
        guess
    ):
        """
        Initialize Brainstormo1 with a guess and related puzzle data.

        Args:
            guess: An instance representing the current puzzle guess, including 
                   information about the puzzle and its potential solutions.
        """
        self.guess = guess
        self.puzzle = guess.puzzle
        self.solve = guess.solve

        # Brainstorming responses and outputs
        self.brainstorm_responses = []
        self.brainstorm_outputs = []
        # LLM settings for brainstorming
        self.llm_settings = self.puzzle.llm_settings

    def set_llm_temperature(self, temperature=0.0):
        """
        Set the temperature for the LLM to adjust the randmoness/creativity of responses.

        Args:
            temperature (float): Temperature setting for the LLM, controlling response randomness.
        """
        self.llm_settings.temperature = temperature
        logger.info("Setting LLM temperature to %s for brainstorming.",
                    self.llm_settings.temperature)

    def brainstorm(self):
        """
        Generate a single brainstorming response by asking the LLM for a possible solution.

        Returns:
            dict: The LLM response containing generated content and metadata.
        """
        # Select a random system prompt file for brainstorming
        random_num = random.randint(0, 2)
        brainstorm_str = f"brainstorm_{random_num}.txt"
        with open(os.path.join(
                get_root_dir(), 'data', 'prompts', 'actor_o1', brainstorm_str),
                'r', encoding='utf-8') as f:
            prompt_system = f.read()
        # Add any previous incorrect guesses to the system prompt
        bad_guesses_str = self.guess.set_bad_guesses_str()
        if len(bad_guesses_str) > 0:
            # Add text to end of bad_guesses_str
            bad_guesses_str += "\n \n You should reject any guess that has the same four words as a guess that we already know is incorrect. \n"            
        prompt_system = prompt_system.replace('{bad_guesses}', bad_guesses_str)
        # Convert system prompt to a user prompt (specific to Actor-o1) and add remaining words
        prompt_user = prompt_system
        words_remain_shuffled = self.solve.temp_words_remain_lst.copy()
        random.shuffle(words_remain_shuffled)
        words_remain_str = " ".join(words_remain_shuffled)
        prompt_user += f"\n \n List of words in puzzle: {words_remain_str}"
        
        # Set up the prompts for the LLM
        prompts = [
            {"role": "user", "content": prompt_user},
        ]
        # Call the LLM and return the response
        llm_response = llm_call(
            model='o1-preview', prompts=prompts, settings=self.llm_settings)
        return llm_response

    def brainstorm_all(self):
        """
        Generate multiple brainstorming responses using the current template.

        Returns:
            list: List of all LLM responses generated in the brainstorming session.
        """
        self.brainstorm_responses = []
        self.brainstorm_outputs = []
        response = self.brainstorm()
        self.brainstorm_responses.append(response)
        self.brainstorm_outputs.append(response.output)
        return self.brainstorm_responses
