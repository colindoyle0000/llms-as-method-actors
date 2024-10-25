"""BrainstormActor2 class for brainstorming possible solutions to the puzzle under Actor-2 approach."""

import os
import logging
import random

from baseclass import BaseClass
from utils_file import (
    get_root_dir
)
from utils_llm import (
    llm_call
)

from utils_string import get_timestamp

# Set up logger
logger = logging.getLogger('connections')


class BrainstormActor2(BaseClass):
    """BrainstormActor2 class for brainstorming possible solutions to the puzzle under Actor-2 approach.."""

    def __init__(
        self,
        guess
    ):
        self.guess = guess
        self.puzzle = guess.puzzle
        self.solve = guess.solve

        # Templates for the different kinds of solutions
        self.templates = []
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

    def load_templates(self, num_templates=5):
        """Load brainstorming templates."""
        self.templates = []
        templates_temp = []
        folder = os.path.join(get_root_dir(), 'data', 'templates')

        # List all files in the folder
        files = [file for file in os.listdir(folder) if file.endswith('.txt')]

        # Sort files based on the numeric value at the start of each filename
        files.sort(key=lambda x: int(x.split('_')[0]))

        # Read and append the contents of each file to self.templates
        for file in files:
            with open(os.path.join(folder, file), 'r', encoding='utf-8') as f:
                templates_temp.append(f.read())
        
        # Ensure self.solve.templates_index is initialized
        if not hasattr(self.solve, 'templates_index'):
            self.solve.templates_index = 0
        
        # Append templates to self.templates until it has num_templates elements
        while len(self.templates) < num_templates:
            if self.solve.templates_index >= len(templates_temp):
                self.solve.templates_index = 0
            self.templates.append(templates_temp[self.solve.templates_index])
            self.solve.templates_index += 1
        
        logger.info(
            "Selected the first %s templates.", num_templates)

    def brainstorm(self, template=None):
        """Ask LLM to brainstorm a possible solution to the puzzle."""
        # If no template is provided, choose a random template
        if template is None:
            template = random.choice(self.templates)
        # Load the system prompt from a .txt file
        with open(os.path.join(
                get_root_dir(), 'data', 'prompts', 'actor_2', 'brainstorm.txt'),
                'r', encoding='utf-8') as f:
            prompt_system = f.read()
        # Within the system prompt, replace the placeholder {template} with the actual template
        prompt_system = prompt_system.replace('{template}', template)
        # If bad guesses have been made, add them to the system prompt
        bad_guesses_str = self.guess.set_bad_guesses_str()
        prompt_system = prompt_system.replace('{bad_guesses}', bad_guesses_str)
        # Create user prompt
        # Create a list that shuffles the words that remain to be solved
        words_remain_shuffled = self.solve.temp_words_remain_lst.copy()
        random.shuffle(words_remain_shuffled)
        # Create a string of the words that remain to be solved
        words_remain_str = " ".join(words_remain_shuffled)
        prompt_user = f"Let's brainstorm a possible solution to this puzzle: {words_remain_str}"
        # Set up the prompts for the LLM
        prompts = [
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": prompt_user},
        ]
        # Call the LLM
        llm_response = llm_call(
            model=self.llm_settings.model, prompts=prompts, settings=self.llm_settings)
        return llm_response

    def brainstorm_all(self):
        """Brainstorm a bunch of possible solutions to the puzzle."""
        self.brainstorm_responses = []
        self.brainstorm_outputs = []
        count = 1
        for template in self.templates:
            logger.debug("Brainstorming attempt %s of %s.",
                            count, len(self.templates))
            response = self.brainstorm(template=template)
            self.brainstorm_responses.append(response)
            self.brainstorm_outputs.append(response.output)
            count += 1
        return self.brainstorm_responses
