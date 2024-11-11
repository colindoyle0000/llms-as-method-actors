"""Puzzle class is a composite class that manages the classes that solve the puzzle for Experiment #1 with GPT-4o for Vanilla, CoT, CoT (Scripted), and Actor approaches.
"""
import logging
import os
import emoji
from src.utils_llm import (
    LLMSettings,
)

from src.baseclass import BaseClass
from src.solve_vanilla import SolveVanilla
from src.solve_cot import SolveCot
from src.solve_actor import SolveActor

# Set up logger
logger = logging.getLogger('method-actors')


class Puzzle(BaseClass):
    """Puzzle class is a composite class that manages the classes that solve the puzzle for Experiment #1 with GPT-4o for Vanilla, CoT, CoT (Scripted), and Actor approaches.
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
        self.vanilla = None
        self.cot = None
        self.cot_scripted = None
        self.actor = None
        
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

    def solve_vanilla(self):
        """Solve the puzzle using vanilla approach."""
        logger.info("Solving puzzle using Vanilla approach")
        self.vanilla = SolveVanilla(self)
        self.vanilla.set_path_vanilla()
        self.vanilla.solve_puzzle_vanilla()
        self.results_dict['vanilla'] = self.vanilla.results_dict
        self.save_attributes(filepath_pkl=self.path_pkl,
                             name=f"puzzle_{self.number}")
    
    def solve_cot(self):
        """Solve the puzzle using cot approach."""
        logger.info("Solving puzzle using Cot approach")
        self.cot = SolveCot(self, cot_scripted=False)
        self.cot.set_path_cot()
        self.cot.solve_puzzle_cot()
        self.results_dict['cot'] = self.cot.results_dict
        self.save_attributes(filepath_pkl=self.path_pkl,
                        name=f"puzzle_{self.number}")

    def solve_cot_scripted(self):
        """Solve the puzzle using cot scripted approach."""
        logger.info("Solving puzzle using Cot Scripted approach")
        self.cot_scripted = SolveCot(self, cot_scripted=True)
        self.cot_scripted.set_path_cot()
        self.cot_scripted.solve_puzzle_cot()
        self.results_dict['cot_scripted'] = self.cot_scripted.results_dict
        self.save_attributes(filepath_pkl=self.path_pkl,
                        name=f"puzzle_{self.number}")
               
    def solve_actor(self):
        """Solve the puzzle using the Actor approach."""
        logger.info("Solving puzzle using Actor approach")
        self.actor = SolveActor(self)
        self.actor.set_path_actor()
        self.actor.solve_puzzle_actor()
        self.results_dict['actor'] = self.actor.results_dict
        self.save_attributes(filepath_pkl=self.path_pkl,
                        name=f"puzzle_{self.number}")
    
    
    def solve_all(self):
        """Solve the puzzle using all approaches."""
        self.solve_vanilla()
        self.solve_cot()
        self.solve_cot_scripted()
        self.solve_actor()

    
    def solve_unfinished(self):
        """Solve the puzzle for any approach that is not finished already."""
        
        if self.vanilla is None:
            logger.info("# %s No Vanilla solve exists. Solving puzzle using Vanilla approach", self.number)
            self.solve_vanilla()
        elif self.vanilla.end_game is False:
            logger.info("# %s Vanilla solve is not finished. Solving puzzle using Vanilla approach", self.number)
            self.vanilla.set_path_vanilla()
            self.vanilla.solve_puzzle_vanilla()
            self.results_dict['vanilla'] = self.vanilla.results_dict
            self.save_attributes(filepath_pkl=self.path_pkl,
                             name=f"puzzle_{self.number}")
        else:
            logger.info("# %s Vanilla solve is already finished. No need to redo.", self.number)
        
        if self.cot is None:
            logger.info("# %s No Cot solve exists. Solving puzzle using Cot approach", self.number)
            self.solve_cot()
        elif self.cot.end_game is False:
            logger.info("# %s Cot solve is not finished. Solving puzzle using Cot approach", self.number)
            self.cot.set_path_cot()
            self.cot.solve_puzzle_cot()
            self.results_dict['cot'] = self.cot.results_dict
            self.save_attributes(filepath_pkl=self.path_pkl,
                        name=f"puzzle_{self.number}")
        else:
            logger.info("# %s Cot solve is already finished. No need to redo.", self.number)
        
        if self.cot_scripted is None:
            logger.info("# %s No Cot Scripted solve exists. Solving puzzle using Cot Scripted approach", self.number)
            self.solve_cot_scripted()
        elif self.cot_scripted.end_game is False:
            logger.info("# %s Cot Scripted solve is not finished. Solving puzzle using Cot Scripted approach", self.number)
            self.cot_scripted.set_path_cot()
            self.cot_scripted.solve_puzzle_cot()
            self.results_dict['cot_scripted'] = self.cot_scripted.results_dict
            self.save_attributes(filepath_pkl=self.path_pkl,
                        name=f"puzzle_{self.number}")
        
        if self.actor is None:
            logger.info("# %s No Actor solve exists. Solving puzzle using Actor approach", self.number)
            self.solve_actor()
        elif self.actor.end_game is False:
            logger.info("# %s Actor solve is not finished. Solving puzzle using Actor approach", self.number)
            self.actor.set_path_actor()
            self.actor.solve_puzzle_actor()
            self.results_dict['actor'] = self.actor.results_dict
            self.save_attributes(filepath_pkl=self.path_pkl,
                        name=f"puzzle_{self.number}")
            
    def save_results(self):
        """Save the results of the puzzle to a dictionary."""
        self.results_dict = {}
        if self.vanilla is not None:
            self.results_dict['vanilla'] = self.vanilla.results_dict
        if self.cot is not None:
            self.results_dict['cot'] = self.cot.results_dict
        if self.cot_scripted is not None:
            self.results_dict['cot_scripted'] = self.cot_scripted.results_dict
        if self.actor is not None:
            self.results_dict['actor'] = self.actor.results_dict
        logger.info("Results saved to dictionary.")
