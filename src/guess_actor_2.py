"""Guess class for Actor-2 approach for storing information about a guess that is processed."""


import logging

from src.guess import BaseGuess

from src.brainstorm_actor_2 import BrainstormActor2
from src.discern_actor_2 import DiscernActor2

# Set up logger
logger = logging.getLogger('connections')


class GuessActor2(BaseGuess):
    """Guess class for Actor-2 approach for storing information about a guess that is processed."""

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
        """Process the guess from start to finish for the Actor-2 approach
        """
        brainstorm_responses = self.do_brainstorm()
        self.do_discern(brainstorm_responses)
        self.do_decide()
        if self.good_options_for_guess is True:
            self.do_select()
            if self.guess_is_valid is True:
                self.discern.make_ready_to_submit()

    def do_brainstorm(self):
        """Brainstorm possible solutions to the puzzle."""
        self.brainstorm = BrainstormActor2(self)
        num_templates = 5
        self.brainstorm.load_templates(num_templates=num_templates)
        brainstorm_responses = self.brainstorm.brainstorm_all()
        self.brainstorm.save_outputs(filepath_md=self.solve.path_md,
                                     name=f"guess_{self.num_of_guess}_brainstorm",
                                     responses=brainstorm_responses
                                     )
        return brainstorm_responses

    def do_discern(self, brainstorm_responses):
        """Discern the best guesses from the brainstorming responses."""
        self.discern = DiscernActor2(self, brainstorm_responses)
        self.discern.extract_all()
        self.discern.save_outputs(filepath_md=self.solve.path_md,
                                  name=f"guess_{self.num_of_guess}_discern_extract",
                                  responses=self.discern.extract_responses
                                  )
        self.discern.discern_guess_all()
        self.discern.save_outputs(filepath_md=self.solve.path_md,
                                  name=f"guess_{self.num_of_guess}_discern_discern",
                                  responses=self.discern.discern_responses
                                  )

    def do_decide(self):
        """Decide if there are good options for the guess."""
        self.discern.decide_all()
        self.discern.save_outputs(filepath_md=self.solve.path_md,
                                  name=f"guess_{self.num_of_guess}_discern_decide_cot",
                                  responses=self.discern.decide_cot_responses
                                  )
        self.discern.save_outputs(filepath_md=self.solve.path_md,
                                  name=f"guess_{self.num_of_guess}_discern_decide_yn",
                                  responses=self.discern.decide_yn_responses
                                  )

    def do_select(self):
        """Select the guess from the discerning process."""
        if self.discern.select_and_validate_all() is True:
            self.guess_is_valid = True
        else:
            self.guess_is_valid = False
        self.discern.save_outputs(filepath_md=self.solve.path_md,
                                  name=f"guess_{self.num_of_guess}_discern_select",
                                  responses=self.discern.select_responses
                                  )
