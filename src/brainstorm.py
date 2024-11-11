"""
Brainstorm class for generating possible solutions to the puzzle using the Actor approach.
"""

import os
import logging
import random

from src.baseclass import BaseClass
from src.utils_file import get_root_dir
from src.utils_llm import llm_call
from src.utils_string import get_timestamp

# Set up logger
logger = logging.getLogger('connections')


class Brainstorm(BaseClass):
    """Class for brainstorming puzzle solutions using the Actor approach.

    This class includes methods to load templates, generate prompts, and interact with an LLM
    to brainstorm possible solutions to a given puzzle.
    """

    def __init__(self, guess):
        """
        Initialize the Brainstorm instance with a guess and related puzzle data.

        Args:
            guess: An instance representing the current guess for the puzzle, containing information 
                   about the puzzle, solutions, and tracking incorrect guesses.
        """
        self.guess = guess
        self.puzzle = guess.puzzle
        self.solve = guess.solve
        self.templates = []  # Stores templates for brainstorming solutions
        self.brainstorm_responses = []  # Stores LLM responses from brainstorming sessions
        self.brainstorm_outputs = []  # Stores generated outputs from LLM responses
        self.llm_settings = self.puzzle.llm_settings  # LLM settings associated with the puzzle

    def set_llm_temperature(self, temperature=0.0):
        """
        Set the LLM temperature to control response creativity.

        Args:
            temperature (float): LLM temperature setting, influencing response randomness.
        """
        self.llm_settings.temperature = temperature
        logger.info("Setting LLM temperature to %s for brainstorming.", self.llm_settings.temperature)

    def load_templates(self, num_templates=5):
        """
        Load a specified number of brainstorming templates from files.

        Args:
            num_templates (int): Number of templates to load for brainstorming. Defaults to 5.
        
        Raises:
            FileNotFoundError: If template files are not found in the specified folder.
        """
        self.templates = []
        templates_temp = []
        folder = os.path.join(get_root_dir(), 'data', 'templates')

        # Retrieve all template files in the directory
        files = [file for file in os.listdir(folder) if file.endswith('.txt')]
        files.sort(key=lambda x: int(x.split('_')[0]))  # Sort based on numeric prefixes

        # Load and store contents of each template file
        for file in files:
            with open(os.path.join(folder, file), 'r', encoding='utf-8') as f:
                templates_temp.append(f.read())
        
        # Ensure `solve.templates_index` is initialized
        if not hasattr(self.solve, 'templates_index'):
            self.solve.templates_index = 0
        
        # Fill `self.templates` up to `num_templates` elements
        while len(self.templates) < num_templates:
            if self.solve.templates_index >= len(templates_temp):
                self.solve.templates_index = 0
            self.templates.append(templates_temp[self.solve.templates_index])
            self.solve.templates_index += 1
        
        logger.info("Selected the first %s templates.", num_templates)

    def brainstorm(self, template=None):
        """
        Generate a brainstorming response using a specified or random template.

        Args:
            template (str): Optional. Template for generating a response. If None, selects a random template.

        Returns:
            dict: LLM response containing generated content and metadata.
        """
        # If no template is provided, randomly select one from `self.templates`
        if template is None:
            template = random.choice(self.templates)
        
        # Load system prompt for brainstorming and replace placeholders
        with open(os.path.join(get_root_dir(), 'data', 'prompts', 'actor', 'brainstorm.txt'), 'r', encoding='utf-8') as f:
            prompt_system = f.read()
        prompt_system = prompt_system.replace('{template}', template)

        # Add previous incorrect guesses to the prompt, if any
        bad_guesses_str = self.guess.set_bad_guesses_str()
        prompt_system = prompt_system.replace('{bad_guesses}', bad_guesses_str)

        # Generate user prompt with shuffled remaining words
        words_remain_shuffled = self.solve.words_remain_lst.copy()
        random.shuffle(words_remain_shuffled)
        words_remain_str = " ".join(words_remain_shuffled)
        prompt_user = f"Let's brainstorm a possible solution to this puzzle: {words_remain_str}"

        # Set up the prompts for the LLM
        prompts = [
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": prompt_user},
        ]

        # Call the LLM and return its response
        llm_response = llm_call(model=self.llm_settings.model, prompts=prompts, settings=self.llm_settings)
        return llm_response

    def brainstorm_all(self):
        """
        Generate multiple brainstorming responses by iterating through loaded templates.

        Returns:
            list: List of all LLM responses generated across multiple brainstorming attempts.
        """
        self.brainstorm_responses = []
        self.brainstorm_outputs = []
        count = 1
        for template in self.templates:
            logger.debug("Brainstorming attempt %s of %s.", count, len(self.templates))
            response = self.brainstorm(template=template)
            self.brainstorm_responses.append(response)
            self.brainstorm_outputs.append(response.output)
            count += 1
        return self.brainstorm_responses
