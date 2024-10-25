"""Experimento1 class oversees the process for Experiment #2 with GPT-o1 for Oneshot-o1, Vanilla-o1, and Actor-o1 approaches."""
import logging
import os
import re
import copy
import time
import random
import json
import numpy as np
import pandas as pd
import openpyxl
import matplotlib.pyplot as plt
import emoji

from utils_llm import (
    LLMSettings,
    llm_call
)

from baseclass import BaseClass
from utils_string import (
    get_date,
    get_timestamp
)
from utils_file import (
    get_root_dir
)
from get_puzzle_info import extract_puzzle_data_from_url

from puzzle_o1 import Puzzleo1

# Set up logger
logger = logging.getLogger('connections')

class Experimento1(BaseClass):
    """Experimento1 class oversees the process for Experiment #2 with GPT-o1 for Oneshot-o1, Vanilla-o1, and Actor-o1 approaches."""

    def __init__(self,
                 puzzle_numbers: list,
                 llm_settings: LLMSettings = LLMSettings(),
                 model: str = None
    ):
        self.puzzle_numbers = puzzle_numbers
        self.puzzles = {}
        self.llm_settings = llm_settings
        if model is not None:
            self.llm_settings.model = model
        # Dictionary of the results of the experiment
        self.results_dict = None
        # Numpy array of the results of the experiment
        self.results_array = None
        # Pandas DataFrame of the results of the experiment
        self.results_df = None
        # Filepath to save data from this experiment
        self.path = ""
        self.path_pkl = ""
        self.path_export = ""
    
    def set_path(self, name: str = None, date: str = None):
        """Set the path for saving data to file."""
        # If name and date are not passed, use the default directory.
        if name is None and date is None:
            date = get_date()
            self.path = os.path.join(
                get_root_dir(), "outputs", date
            )
        # If a directory is passed, use that directory.
        else:
            # If date is not passed, use the current date.
            if date is None:
                date = get_date()
            # If name is not passed, use an underscore.
            if name is None:
                name = "_"
            self.path = os.path.join(get_root_dir(), "outputs", date, name)
        # Create the directory if it does not exist.
        os.makedirs(self.path, exist_ok=True)
        # Set the path for saving data to pkl file.
        self.path_pkl = os.path.join(self.path, "experiment_o1_pkl")
        # Create the directory if it does not exist.
        os.makedirs(self.path_pkl, exist_ok=True)
        # Set the path for saving data exports.
        self.path_export = os.path.join(self.path, "experiment_o1_export")
        # Create the directory if it does not exist.
        os.makedirs(self.path_export, exist_ok=True)
    
    def set_llm_settings(
        self,
        embeddings: str = None,
        model: str = None,
        max_tokens: int = None,
        model_long: str = None,
        max_tokens_long: int = None,
        model_cheap: str = None,
        max_tokens_cheap: int = None,
        chunk_size: int = None,
        chunk_overlap: int = None,
        chunk_size_long: int = None,
        max_attempts: int = None,
        temperature: int = None,
        response_format: str = None
    ):
        """Set the LLM settings.
        With this function, only the settings that you want to change need to be passed.
        """
        self.llm_settings.embeddings = embeddings if embeddings else self.llm_settings.embeddings
        self.llm_settings.model = model if model else self.llm_settings.model
        self.llm_settings.max_tokens = max_tokens if max_tokens else self.llm_settings.max_tokens
        self.llm_settings.model_long = model_long if model_long else self.llm_settings.model_long
        self.llm_settings.max_tokens_long = max_tokens_long if max_tokens_long else self.llm_settings.max_tokens_long
        self.llm_settings.model_cheap = model_cheap if model_cheap else self.llm_settings.model_cheap
        self.llm_settings.max_tokens_cheap = max_tokens_cheap if max_tokens_cheap else self.llm_settings.max_tokens_cheap
        self.llm_settings.chunk_size = chunk_size if chunk_size else self.llm_settings.chunk_size
        self.llm_settings.chunk_overlap = chunk_overlap if chunk_overlap else self.llm_settings.chunk_overlap
        self.llm_settings.chunk_size_long = chunk_size_long if chunk_size_long else self.llm_settings.chunk_size_long
        self.llm_settings.max_attempts = max_attempts if max_attempts else self.llm_settings.max_attempts
        self.llm_settings.temperature = temperature if temperature else self.llm_settings.temperature
        self.llm_settings.response_format = response_format if response_format else self.llm_settings.response_format

    def set_puzzles(self):
        """Set the puzzles for the experiment."""
        self.puzzles = {}  # Initialize an empty dictionary
        for number in self.puzzle_numbers:  # Iterate over each puzzle number
            logger.info("Getting puzzle information for puzzle %s", number)
            url = f"https://connections.swellgarfo.com/nyt/{number}"  # Construct the URL for the puzzle
            puzzle_str, number, solution_lst = extract_puzzle_data_from_url(url)  # Extract puzzle data from the URL
            path = os.path.join(self.path, str(number))  # Create a directory for the puzzle
            # Create a new Puzzle object
            puzzle = Puzzleo1(
                words_str=puzzle_str, 
                number=number,
                solution_lst=solution_lst, 
                llm_settings=self.llm_settings, 
                model=self.llm_settings.model,
                path=path
            )
            # Add the puzzle to the dictionary of puzzles
            self.puzzles[number] = puzzle  
            logger.info("Puzzle %s added to the experiment.", number)
            self.puzzles[number].setup_puzzle()
    
    def set_new_puzzles(self, puzzle_numbers: list):
        """Set new puzzles for the experiment."""
        # Add the new puzzle numbers to the existing list of puzzle numbers
        self.puzzle_numbers.extend(puzzle_numbers)
        # Set the new puzzles
        for number in self.puzzle_numbers:
            if number not in self.puzzles:
                logger.info("Getting puzzle information for puzzle %s", number)
                url = f"https://connections.swellgarfo.com/nyt/{number}"
                puzzle_str, number, solution_lst = extract_puzzle_data_from_url(url)
                path = os.path.join(self.path, str(number))
                puzzle = Puzzleo1(
                    words_str=puzzle_str, 
                    number=number,
                    solution_lst=solution_lst, 
                    llm_settings=self.llm_settings, 
                    model=self.llm_settings.model,
                    path=path
                )
                self.puzzles[number] = puzzle
                logger.info("Puzzle %s added to the experiment.", number)
                self.puzzles[number].setup_puzzle()
    
    def solve_puzzle(self, number: int):
        """Solve a single puzzle."""
        self.puzzles[number].solve_all()
        
    def solve_puzzle_all(self):
        """Solve all puzzles in the experiment."""
        for number, puzzle in self.puzzles.items():
            logger.info("Solving puzzle %s", number)
            puzzle.solve_all()
            timestamp = get_timestamp()
            self.save_attributes(filepath_pkl=self.path_pkl,
                        name=f"experiment_o1_{timestamp}")
            
    def solve_unfinished_puzzles(self):
        """Solve all unfinished puzzles in the experiment."""
        for number, puzzle in self.puzzles.items():
            unfinished = False
            logger.info("Solving puzzle %s", number)
            if self.puzzles[number].actoro1 is None:
                unfinished = True
            elif self.puzzles[number].vanillao1 is None:
                unfinished = True
            elif self.puzzles[number].actoro1.end_game is False:
                unfinished = True
            elif self.puzzles[number].vanillao1.end_game is False:
                unfinished = True
            elif self.puzzles[number].oneshoto1 is None:
                unfinished = True
            elif self.puzzles[number].oneshoto1.end_game is False:
                unfinished = True
            if unfinished:
                puzzle.solve_unfinished()
                timestamp = get_timestamp()
                self.save_attributes(filepath_pkl=self.path_pkl,
                            name=f"experiment_o1_{timestamp}")
            else:
                logger.info("Puzzle %s already solved.", number)

    def save_results_dict(self):
        """Save the results of the experiment to a dictionary."""
        self.results_dict = {}
        for number, puzzle in self.puzzles.items():
            if puzzle.results_dict:
                self.results_dict[number] = puzzle.results_dict
            else:
                logger.warning("Puzzle %s has no results.", number)
                self.results_dict[number] = {}
    
    def save_results_dict_to_json(self):
        """Save the results of the experiment to a JSON file."""
        timestamp = get_timestamp()
        filepath = os.path.join(self.path_export, f"results_{timestamp}.json")
        with open(filepath, "w") as f:
            json.dump(self.results_dict, f, indent=4)
    
    def save_results_df(self):
        """Save the results of the experiment to a pandas DataFrame."""
        data = []
        for number, puzzle in self.puzzles.items():
            row = {'puzzle_number': number}
            
            for result_type in ['vanillao1', 'actoro1']:
                result = puzzle.results_dict.get(result_type, {})
        
                # Add the values to the row, with keys indicating the result type
                row[f'{result_type}_success'] = result.get('success', None)
                row[f'{result_type}_good_guesses'] = result.get('good_guesses', None)
                row[f'{result_type}_bad_guesses'] = result.get('bad_guesses', None)
                row[f'{result_type}_guesses_submitted'] = result.get('guesses_submitted', None)
    
            data.append(row)

        # Convert the list of dictionaries to a DataFrame
        self.results_df = pd.DataFrame(data)
        timestamp = get_timestamp()
        self.results_df.to_excel(os.path.join(self.path_export, f"experiment_o1_results{timestamp}.xlsx"), index=False)
        self.save_attributes(filepath_pkl=self.path_pkl,
                        name=f"experiment_o1")
    
    def run_experiment(self, numbers: list):
        """Run the experiment."""
        self.set_path()
        self.set_puzzles()
        self.setup_puzzles()
        self.solve_puzzle_all()
        self.save_results_dict()
        self.save_results_dict_to_json()
        self.save_results_df()
    
    def finish_experiment(self):
        """Finish the experiment."""
        self.solve_unfinished_puzzles()
        self.save_results_dict()
        self.save_results_dict_to_json()
        self.save_results_df()
