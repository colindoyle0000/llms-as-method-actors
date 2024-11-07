"""Base class for solve classes in the project.
"""

import logging
import os
import re
import emoji


from src.baseclass import BaseClass
from src.utils_string import (
    get_date,
    get_timestamp
)
from src.utils_file import (
    get_root_dir
)

# Set up logger
logger = logging.getLogger('connections')

class BaseSolver(BaseClass):
    """Base class for solve classes in the project.
    """

    def __init__(self
    ):
        super().__init__()  # Call the constructor of BaseClass
        self.puzzle = None
        # Words that remain to be solved
        self.words_remain_lst = []
        # Words that are solved
        self.words_solved_lst = []
        # Current guess instance
        self.current_guess = None
        # Guesses that have been processed by the solve instance
        self.guesses_processed = []
        # Guesses that are ready to be submitted
        self.guesses_ready_to_submit = []
        # Guesses that have been submitted by the solve instance
        self.guesses_submitted = []
        # Good guesses (full guess object)
        self.good_guesses = []
        # Good guesses (just the words, not the full guess object)
        self.good_guesses_lst = []
        # Bad guesses (full guess object)
        self.bad_guesses = []
        # Bad guesses (just the words, not the full guess object)
        self.bad_guesses_lst = []
        # End game
        self.end_game = False
        # Success
        self.success = False
        # Time to solve the puzzle
        self.solve_time = 0
        # Results dictionary
        self.results_dict = None

        # Filepath for saving data from this solve attempt
        self.path = ""
        self.path_md = ""
        self.path_pkl = ""

    def set_path(self, name: str = None):
        """Set the path for saving data to file."""
        self.path = os.path.join(self.puzzle.path, name)
        # Create the directory if it does not exist.
        os.makedirs(self.path, exist_ok=True)
        # Set the path for saving data to pkl file.
        self.path_pkl = os.path.join(self.path, "pkl")
        # Create the directory if it does not exist.
        os.makedirs(self.path_pkl, exist_ok=True)
        # Set the path for saving data to markdown file.
        self.path_md = os.path.join(self.path, "md")
        # Create the directory if it does not exist.
        os.makedirs(self.path_md, exist_ok=True)

    def check_end_game_conditions(self):
        """See if end game conditions are met."""
        # If the number of bad guesses is greater than the maximum number of bad guesses allowed,
        # end the game
        if len(self.bad_guesses_lst) >= self.puzzle.num_bad_guesses:
            logger.info("Ending game. Too many bad guesses.")
            self.end_game = True
            self.success = False
        # If the number of good guesses is equal to 4
        if len(self.good_guesses_lst) >= 4:
            logger.info(
                "Ending game. All parts of the solution have been guessed.")
            self.end_game = True
            self.success = True  

    def save_results_dict(self):
        """Save the results of the solve to a dictionary."""
        self.results_dict = {
            "success": self.success,
            "good_guesses": len(self.good_guesses_lst),
            "bad_guesses": len(self.bad_guesses_lst),
            "guesses_submitted": len(self.guesses_submitted),
            "solve_time": self.solve_time,
        }

    def save_summary(self):
        """Save a summary of the results as a markdown file."""
        timestamp = get_timestamp()
        filename = f"summary_puzzle{self.puzzle.number}_{self.puzzle.llm_settings.model}_{timestamp}.md"
        filepath = os.path.join(self.path_md, filename)
        with open(
            filepath,
            'w', encoding='utf-8'
        ) as f:
            f.write(f"# Summary of Puzzle {self.puzzle.number}\n\n")
            f.write(f"Date: {get_date()}\n")
            f.write(f"Model: {self.puzzle.llm_settings.model}\n")
            minutes, seconds = divmod(self.solve_time, 60)

            if self.puzzle.emoji_dict is not None:
                f.write("\n")
                for guess in self.guesses_submitted:
                    for word in guess.guess_lst:
                        square_emoji = self.puzzle.emoji_dict.get(
                            word, (emoji.emojize(':red_question_mark:')))
                        f.write(f"{square_emoji}")
                    f.write("\n")
            if self.success is True:
                f.write("## Success!\n\n")
                f.write(
                    f"Solved in {int(minutes)} minutes and {int(seconds)} seconds \n\n")
            else:
                f.write("## Failure!\n\n")
                f.write(
                    f"Wasted {int(minutes)} minutes and {int(seconds)} seconds on this dumb puzzle.\n\n")
            num_good_guesses = len(self.good_guesses_lst)
            num_bad_guesses = len(self.bad_guesses_lst)
            f.write(f"Correct guesses: {num_good_guesses}\n")
            f.write(f"Incorrect guesses: {num_bad_guesses}\n\n")
            f.write("## Submitted Guesses\n\n")
            for guess in self.guesses_submitted:
                f.write(f"### Guess {guess.num_of_guess}\n\n")
                if guess.guess_is_correct:
                    f.write("Correct: ")
                else:
                    f.write("Incorrect: ")
                guess_str = " ".join(guess.guess_lst)
                f.write(f"{guess_str}\n\n")
            f.write("## Solution\n\n")
            for solution in self.puzzle.solution_lst:
                # Turn the solution into a string
                solution_str = " ".join(solution)
                f.write(f"{solution_str}\n\n")
            f.write("## Submitted Guesses Play-By-Play\n\n")
            for guess in self.guesses_submitted:
                f.write(f"### Guess {guess.num_of_guess}\n\n")
                if guess.guess_is_correct:
                    f.write("Correct: ")
                else:
                    f.write("Incorrect: ")
                guess_str = " ".join(guess.guess_lst)
                f.write(f"{guess_str}\n\n")
                f.write("Reasoning:\n")
                reasoning = ""
                if len(guess.guess_rationale) > 0:
                    reasoning = f"{guess.guess_rationale}\n\n"
                    # Modify reasoning string so that all "# " are "## "
                    reasoning = re.sub(
                        r"^#", "##", reasoning, flags=re.MULTILINE)
                    f.write(f"{reasoning}")
                elif guess == self.guesses_submitted[-1] and self.success:
                    f.write(
                        "(Automatically chosen by application because it was the only option left.).\n\n")
            if len(self.guesses_processed) > len(self.guesses_submitted):
                f.write("## All Guesses Play-By-Play\n\n")
                for guess in self.guesses_processed:
                    guess_str = " ".join(guess.guess_lst)
                    f.write(f"### Guess {guess.num_of_guess}\n\n")
                    if guess.guess_was_submitted:
                        if guess.guess_is_correct:
                            f.write("Submitted and Correct: ")
                        else:
                            f.write("Submitted and Incorrect: ")
                        guess_str = " ".join(guess.guess_lst)
                        f.write(f"Guess: {guess_str}\n\n")
                        f.write("Reasoning:\n")
                        reasoning = ""
                        if len(guess.guess_rationale) > 0:
                            reasoning = f"{guess.guess_rationale}\n\n"
                            # Modify reasoning string so that all "# " are "## "
                            reasoning = re.sub(
                                r"^#", "##", reasoning, flags=re.MULTILINE)
                            f.write(f"{reasoning}")
                        elif guess == self.guesses_submitted[-1] and self.success:
                            f.write(
                                "(Automatically chosen by application because it was the only option left.).\n\n")
                    elif len(guess.guess_rationale) > 0:
                        f.write(f"Guess: {guess_str}\n\n")
                        f.write("Reasoning:\n")
                        reasoning = f"{guess.guess_rationale}\n\n"
                        # Modify reasoning string so that all "# " are "## "
                        reasoning = re.sub(
                            r"^#", "##", reasoning, flags=re.MULTILINE)
                        f.write(f"{reasoning}")
                    elif guess.guess_is_valid is False:
                        f.write(
                            "Rejected because guess has formatting or content error: ")
                        guess_str = " ".join(guess.guess_lst)
                        f.write(f"Guess: {guess_str}\n\n")
                    elif guess.good_options_for_guess is False:
                        f.write("Rejected because no good options for guess: ")
                        reasoning = ""
                        for response in guess.discern.decide_cot_responses:
                            reasoning += f"{response.output}\n\n"
                        # Modify reasoning string so that all "# " are "## "
                        reasoning = re.sub(
                            r"^#", "##", reasoning, flags=re.MULTILINE)
                        f.write(f"{reasoning}")
            logger.info("Saved summary to %s", filepath)

    def save_summary_no_solution(self):
        """Save a summary of the results as a markdown file."""
        timestamp = get_timestamp()
        filename = f"summary_puzzle{self.puzzle.number}_{self.puzzle.llm_settings.model}_{timestamp}.md"
        with open(
            os.path.join(self.path_md, filename),
            'w', encoding='utf-8'
        ) as f:
            f.write(f"# Summary of Puzzle {self.puzzle.number}\n\n")
            f.write(f"Date: {get_date()}\n")
            f.write(f"Model: {self.puzzle.llm_settings.model}\n")
            minutes, seconds = divmod(self.solve_time, 60)
            f.write(
                f"Took {int(minutes)} minutes and {int(seconds)} seconds \n\n")

            f.write("## Submitted Guesses\n\n")
            for guess in self.guesses_submitted:
                f.write(f"### Guess {guess.num_of_guess}\n\n")
                guess_str = " ".join(guess.guess_lst)
                f.write(f"{guess_str}\n\n")
                f.write("No solution provided.\n\n")

    