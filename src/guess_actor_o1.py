"""Guess class for Actor-o1 approach for storing information about a guess that is processed."""

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

from src.brainstorm_actor_o1 import Brainstormo1
from src.discern_actor_o1 import Discerno1
from submit import Submit

# Set up logger
logger = logging.getLogger('connections')


class GuessActoro1(BaseGuess):
    """Guess class for Actor-o1 approach for storing information about a guess that is processed."""

    def __init__(
        self,
        solve
    ):
        super().__init__()
        self.solve = solve
        self.puzzle = self.solve.puzzle
        self.num_of_guess = len(self.solve.guesses_processed)+1
        self.guess_type = 1
        self.guess_lst_freq = 0
        # Count of how many times guess has been evaluated for submission as a final guess
        self.guess_eval_count = 0

        # Class instances
        self.brainstorm = None
        self.discern = None
    
    
    def process_guess(self):
        """Process the guess from start to finish for the Actor-o1 approach
        """
        brainstorm_responses = self.do_brainstorm()
        self.do_discern(brainstorm_responses)
        if self.guess_is_valid is True:
            self.discern.make_ready_to_submit()

    def do_brainstorm(self):
        """Brainstorm possible solutions to the puzzle."""
        self.brainstorm = Brainstormo1(self)
        brainstorm_responses = self.brainstorm.brainstorm_all()
        self.brainstorm.save_outputs(filepath_md=self.solve.path_md,
                                     name=f"guess_{self.num_of_guess}_brainstorm",
                                     responses=brainstorm_responses
                                     )
        return brainstorm_responses

    def do_discern(self, brainstorm_responses):
        """Select the guess from the brainstorming responses."""
        self.discern = Discerno1(self, brainstorm_responses)
        if self.discern.select_and_validate_all() is True:
            self.guess_is_valid = True
        else:
            self.guess_is_valid = False
        self.discern.save_outputs(filepath_md=self.solve.path_md,
                                  name=f"guess_{self.num_of_guess}_discern_select",
                                  responses=self.discern.select_responses
                                  )
