"""Guess class for One-Shot GPT-o1 approach for storing information about a guess that is processed."""

import os
import logging
import random

from src.guess import BaseGuess
from src.utils_file import (
    get_root_dir
)
from src.utils_llm import (
    llm_call
)

# Set up logger
logger = logging.getLogger('connections')

class GuessOneShoto1(BaseGuess):
    """Guess class for One-Shot GPT-o1 approach for storing information about a guess that is processed."""
    
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
        """Process the guess from start to finish for the one-shot GPTo1 approach."""
        self.make_guess()


    def make_guess(self):
        """Ask LLM to make a guess."""
        self.make_guess_responses = []
        self.make_guess_outputs = []
        # Load the system prompt from a .txt file
        with open(os.path.join(
                get_root_dir(), 'data', 'prompts', 'oneshot_o1' , 'make_guess.txt'),
                'r', encoding='utf-8') as f:
            prompt_system = f.read()
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
        self.guess_lst.append(llm_response.output)
        logger.debug("Made guess: /n /n %s", llm_response.output)