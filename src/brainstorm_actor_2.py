"""BrainstormActor2 class for brainstorming possible solutions to the puzzle under Actor-2 approach."""

import os
import logging
import random

from src.baseclass import BaseClass
from src.utils_file import get_root_dir
from src.utils_llm import llm_call
from src.utils_string import get_timestamp

# Set up logger
logger = logging.getLogger('connections')


class BrainstormActor2(BaseClass):
    """Class to manage brainstorming for puzzle solutions using the Actor-2 approach.
    
    This class allows for loading brainstorming templates, setting up prompts for the language
    model (LLM), and generating brainstorming responses based on given puzzle context.
    """

    def __init__(self, guess):
        """
        Initialize the BrainstormActor2 instance with a guess and related puzzle data.

        Args:
            guess: An instance representing the current puzzle guess, including details 
                   about the puzzle context and solutions.
        """
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
        """
        Set the LLM temperature setting for brainstorming, allowing future adjustments 
        to the randomness/creativity of responses.
        
        Args:
            temperature (float): Temperature for the LLM, controlling response randomness.
        """
        self.llm_settings.temperature = temperature
        logger.info("Setting LLM temperature to %s for brainstorming.",
                    self.llm_settings.temperature)

    def load_templates(self, num_templates=5):
        """
        Load and select a specified number of brainstorming templates from the template folder.

        Args:
            num_templates (int): Number of templates to load for brainstorming. Defaults to 5.
        
        Raises:
            FileNotFoundError: If template files are not found in the specified folder.
        """
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
        """
        Generate a brainstorming response by asking the LLM for a possible solution.

        Args:
            template (str): Optional. The template to use for this brainstorming session.
                            If not provided, a random template will be selected.

        Returns:
            dict: The response from the LLM call, including generated output and metadata.
        """
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
        """
        Generate a series of brainstorming responses by iterating through loaded templates.

        Returns:
            list: List of all LLM responses generated across multiple brainstorming attempts.
        """
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
