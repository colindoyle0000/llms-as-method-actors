"""Puzzleo1 class is a composite class that manages the classes that solve the puzzle using GPT-o1 model.
"""
import logging
import os
import emoji
from src.utils_llm import (
    LLMSettings,
)

from src.baseclass import BaseClass
from src.solve_one_shot_o1 import SolveOneShoto1
from src.solve_vanilla_o1 import SolveVanillao1
from src.solve_actor_o1 import SolveActoro1

# Set up logger
logger = logging.getLogger('connections')


class Puzzleo1(BaseClass):
    """Puzzleo1 class is a composite class that manages the classes that solve the puzzle using GPT-o1 model.
    """

    def __init__(self,
                 words_str: str,
                 number: int = 0000,
                 solution_lst: list = None,
                 llm_settings: LLMSettings = LLMSettings(),
                 model: str = None,
                 path = None
                 ):
        super().__init__()  # Call the constructor of BaseClass
        # LLM settings for this instance (dataclass in utils_llm.py)
        self.llm_settings = llm_settings
        if model is not None:
            self.llm_settings.model = model
        # Puzzle data
        # Raw string of the puzzle
        self.words_str = words_str
        # Number of the puzzle
        self.number = number
        # Puzzle string converted to a list of strings, each string representing a tile in the puzzle
        self.words_lst = []
        # Puzzle solution
        self.solution_lst = solution_lst
        # Dictionary of words to emojis
        self.emoji_dict = None
        self.num_bad_guesses = 4
        # Dictionary of solve attempts
        self.solve_attempts = {}

        # Filepath for saving data from this puzzle
        self.path = path
        self.path_pkl = ""
        
        # Class instances
        self.oneshoto1 = None
        self.vanillao1 = None
        self.actoro1 = None

        
        self.results_dict = {}

    def set_path(self):
        """Set the path for saving data to file."""
        # Create the directory if it does not exist.
        os.makedirs(self.path, exist_ok=True)
        # Set the path for saving data to pkl file.
        self.path_pkl = os.path.join(self.path, "pkl")
        # Create the directory if it does not exist.
        os.makedirs(self.path_pkl, exist_ok=True)

    def clean_up_puzzle_text(self, words_lst: list):
        """Clean up a list of words for use in the puzzle."""
        # Remove any new line characters from each string in the list
        words_lst = [x.replace("\n", "") for x in words_lst]
        # Remove any punctuation from each string in the list
        words_lst = [x.translate(str.maketrans(
            "", "", ".,!?:")) for x in words_lst]
        # Remove leading and trailing whitespace from each string in the list
        words_lst = [x.strip() for x in words_lst]
        # Make all of the letters in all of the strings uppercase
        words_lst = [x.upper() for x in words_lst]
        # Remove any strings that are too short to be valid words
        words_lst = [x for x in words_lst if len(x) >= 1]
        return words_lst

    def split_puzzle_text(self, words_str: str, num_items: int = 4, separator: str = None):
        """Takes a raw string of words, turns it into a list, and cleans it up for use in the puzzle."""
        # Split the raw string into a list of strings based on separator
        words_lst = None
        if separator:
            words_lst = words_str.split(separator)
            words_lst = self.clean_up_puzzle_text(words_lst)
            if len(words_lst) != num_items:
                logger.warning("Based on provided separator, number of items in list is not %s. Number of items is %s. Trying other separators.",
                               num_items, len(words_lst))
                words_lst = None
        if words_lst is None:
            # Otherwise split the string into a list of strings based on newline, then comma, then space
            words_lst = words_str.split("\n")
            words_lst = self.clean_up_puzzle_text(words_lst)
            if len(words_lst) != num_items:
                words_lst = words_str.split(",")
            words_lst = self.clean_up_puzzle_text(words_lst)
            if len(words_lst) != num_items:
                words_lst = words_str.split(" ")
            words_lst = self.clean_up_puzzle_text(words_lst)
            if len(words_lst) != num_items:
                logger.warning("Number of items in list is not %s. Number of items is %s.",
                               num_items, len(words_lst))
        return words_lst

    def load_puzzle(self):
        """Load the puzzle from the raw string."""
        self.words_lst = self.split_puzzle_text(self.words_str, num_items=16)
        logger.info("Loaded puzzle with %s words.\n%s",
                    len(self.words_lst), self.words_lst)
        # Set the remaining words to be solved to the full list of words
        self.words_remain_lst = self.words_lst
        # Check to make sure length of list is 16.
        if len(self.words_lst) != 16:
            logger.error(
                "Puzzle must have exactly 16 words. Length is %s.", len(self.words_lst))
            raise ValueError("Puzzle must have exactly 16 words.")

    def set_solution(self, solution_lst=None):
        """Set the solution to the puzzle."""
        if solution_lst is not None:
            self.solution_lst = solution_lst
        if self.solution_lst is not None:
            if len(self.solution_lst) != 4:
                raise ValueError("Incorrect number of parts to the solution. It should be 4 but is %s",
                                 len(self.solution_lst))
            # If the solution is not already a list of lists, split it into a list of lists
            if not all(isinstance(i, list) for i in self.solution_lst):
                for i, solution in enumerate(self.solution_lst):
                    self.solution_lst[i] = self.split_puzzle_text(
                        solution, num_items=4)
                logger.info("Set solution to list of %s.\n List is:\n %s",
                            len(self.solution_lst), self.solution_lst)
            # For each word in each item in the solution list, make sure it is in the words list
            for solution in self.solution_lst:
                for word in solution:
                    if word not in self.words_lst:
                        raise ValueError(
                            "Word in solution not found in words list: %s", word)
            logger.info("Each word in the solution is in the words list.")
        else:
            logger.warning("No solution provided.")

    def set_emoji_dict(self):
        """Set the emoji dictionary for the puzzle."""
        self.emoji_dict = {}
        if self.solution_lst is not None:
            if len(self.solution_lst) != 4:
                raise ValueError("Incorrect number of parts to the solution. It should be 4 but is %s",
                                 len(self.solution_lst))
            for word in self.solution_lst[0]:
                self.emoji_dict[word] = (emoji.emojize(":yellow_square:"))
            for word in self.solution_lst[1]:
                self.emoji_dict[word] = (emoji.emojize(":green_square:"))
            for word in self.solution_lst[2]:
                self.emoji_dict[word] = (emoji.emojize(":blue_square:"))
            for word in self.solution_lst[3]:
                self.emoji_dict[word] = (emoji.emojize(":purple_square:"))
            logger.info("Emoji dictionary set for the puzzle.")
        else:
            logger.warning("No solution provided. Emoji dictionary not set.")

    def setup_puzzle(self):
        """Set up the puzzle default filepath, default llm settings, load puzzle, and set solution."""
        self.set_path()
        self.load_puzzle()
        self.set_solution()
        self.set_emoji_dict()
        if self.llm_settings.model == 'gpt-4':
            self.set_llm_settings(
                max_tokens=6000, chunk_size=6000, chunk_overlap=500)
            logger.info("LLM settings set for gpt-4 token capacity.")
        elif self.llm_settings.model == 'claude-3-opus-20240229':
            self.set_llm_settings(
                max_tokens=3500, chunk_size=3500, chunk_overlap=300)
            logger.info(
                "LLM settings set for claude-3-opus-20240229 token capacity.")
    
    def solve_oneshoto1(self):
        """Solve the puzzle using the oneshoto1 approach."""
        logger.info("Solving puzzle using One-Shot o1 approach")
        self.oneshoto1 = SolveOneShoto1(self)
        self.oneshoto1.set_path_oneshoto1()
        self.oneshoto1.solve_puzzle_oneshoto1()
        self.save_attributes(filepath_pkl=self.path_pkl,
                        name=f"puzzle_{self.number}")
    
    def solve_vanillao1(self):
        """Solve the puzzle using vanillao1 approach."""
        logger.info("Solving puzzle using Vanilla o1 approach")
        self.vanillao1 = SolveVanillao1(self)
        self.vanillao1.set_path_vanillao1()
        self.vanillao1.solve_puzzle_vanillao1()
        self.results_dict['vanillao1'] = self.vanillao1.results_dict
        self.save_attributes(filepath_pkl=self.path_pkl,
                        name=f"puzzle_{self.number}")
    
    def solve_actoro1(self):
        """Solve the puzzle using Actor-o1 approach."""
        logger.info("Solving puzzle using Actor-o1 approach")
        self.actoro1 = SolveActoro1(self)
        self.actoro1.set_path_actoro1()
        self.actoro1.solve_puzzle_actoro1()
        self.results_dict['actoro1'] = self.actoro1.results_dict
        self.save_attributes(filepath_pkl=self.path_pkl,
                        name=f"puzzle_{self.number}")
    
    def solve_all(self):
        """Solve the puzzle using all approaches."""
        self.solve_oneshoto1()
        self.solve_vanillao1()
        self.solve_actoro1()    
    
    def solve_unfinished(self):
        """Solve the puzzle for any approach that is not finished already."""
        if self.oneshoto1 is None or self.oneshoto1.end_game is False:
            logger.info("# %s No One-Shot o1 solve exists. Solving puzzle using One-Shot o1 approach", self.number)
            self.solve_oneshoto1()
        else:
            logger.info("# %s One-Shot o1 solve is already finished. No need to redo.", self.number)
        if self.vanillao1 is None:
            logger.info("# %s No Vanilla o1 solve exists. Solving puzzle using Vanilla o1 approach", self.number)
            self.solve_vanillao1()
        elif self.vanillao1.end_game is False:
            logger.info("# %s Vanilla o1 solve is not finished. Solving puzzle using Vanilla o1 approach", self.number)
            self.vanillao1.set_path_vanillao1()
            self.vanillao1.llm_settings = self.llm_settings
            self.vanillao1.puzzle.words_lst = self.words_lst
            self.vanillao1.solve_puzzle_vanillao1()
            self.results_dict['vanillao1'] = self.vanillao1.results_dict
            self.save_attributes(filepath_pkl=self.path_pkl,
                        name=f"puzzle_{self.number}")
        else:
            logger.info("# %s Vanilla o1 solve is already finished. No need to redo.", self.number)
        if self.actoro1 is None:
            logger.info("# %s No Actor-o1 solve exists. Solving puzzle using Actor-o1 approach", self.number)
            self.solve_actoro1()
        elif self.actoro1.end_game is False:
            logger.info("# %s Actor-o1 solve is not finished. Solving puzzle using Actor-o1 approach", self.number)
            self.actoro1.set_path_actoro1()
            self.actoro1.llm_settings = self.llm_settings
            self.actoro1.puzzle.words_lst = self.words_lst
            self.actoro1.solve_puzzle_actoro1()
            self.results_dict['actoro1'] = self.actoro1.results_dict
            self.save_attributes(filepath_pkl=self.path_pkl,
                        name=f"puzzle_{self.number}")
            
            
    def save_results(self):
        """Save the results of the puzzle to a dictionary."""
        self.results_dict = {}
        if self.vanillao1 is not None:
            self.results_dict['vanillao1'] = self.vanillao1.results_dict
            logger.info("Vanilla-o1 results saved to dictionary.")
        if self.actoro1 is not None:
            self.results_dict['actoro1'] = self.actoro1.results_dict
            logger.info("Actor-o1 results saved to dictionary.")
