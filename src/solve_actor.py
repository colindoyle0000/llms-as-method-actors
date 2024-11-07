"""SolveActor class is a class that solves the Connections puzzle using model of LLMs as method actors for designing prompts.
"""

import logging
import os
import re
import time
import emoji
import random

from src.utils_llm import (
    llm_call
)

from src.baseclass import BaseClass
from src.solve import BaseSolver
from src.utils_string import (
    get_date,
    get_timestamp
)
from src.utils_file import (
    get_root_dir
)

from src.guess_actor import GuessActor

# Set up logger
logger = logging.getLogger('connections')

class SolveActor(BaseSolver):
    """SolveActor class is a class that solves the Connections puzzle using model of LLMs as method actors for designing prompts.
    """
    
    def __init__(self,
                 puzzle
    ):
        super().__init__()
        self.puzzle = puzzle
        self.llm_settings = puzzle.llm_settings
        self.words_remain_lst = puzzle.words_lst
        # Evaluations of multiple guesses
        self.evaluations = []
        # Number of brainstorming templates
        self.templates_num = 24
        # Where previous guess left off going through brainstorm templates
        self.templates_index = 0
        
    
    def set_path_actor(self):
        """Set the path for saving data to file."""
        self.set_path(name="solve_actor")
 
    def solve_puzzle_actor(self):
        """Solve the puzzle using the method actor approach.
        """
        start_time = time.time()
        logger.info("Solving puzzle using Actor method. \n Words in puzzle: \n %s \n Solution: \n %s",
                    self.puzzle.words_lst, self.puzzle.solution_lst)
        # Set self.templates_num to the number of brainstorming templates
        folder = os.path.join(get_root_dir(), 'data', 'templates')
        files = [file for file in os.listdir(folder) if file.endswith('.txt')]
        self.templates_num = len(files)
        logger.info("Number of brainstorming templates: %s", self.templates_num)
        if len(self.guesses_processed) == 0:

            self.current_guess = None
            self.guesses_processed = []
            self.guesses_ready_to_submit = []
            self.guesses_submitted = []
            self.good_guesses = []
            self.good_guesses_lst = []
            self.bad_guesses = []
            self.bad_guesses_lst = []
            self.end_game = False
            self.success = False
        while self.end_game is False:
            self.save_attributes(filepath_pkl=self.path_pkl,
                                 name=f"puzzle_{self.puzzle.number}")
            
            # If the puzzle is not solved, create a new guess
            if self.end_game is False:
                # Create a new guess
                self.current_guess = GuessActor(self)
                guesses_ready_to_submit_str = ""
                for guess in self.guesses_ready_to_submit:
                    guess_str = "Guess: \n"
                    guess_str += " ".join(guess.guess_lst)
                    guess_str += "\n Rationale: \n"
                    guess_str += guess.guess_rationale
                    guesses_ready_to_submit_str += f"{guess_str}\n"
                logger.info("Starting New Guess! \n Current guess number: %s \n %s words remaining: \n %s  \n %s good guesses so far: \n %s \n %s bad guesses so far: \n %s \n %s guesses ready to submit: \n %s",
                            self.current_guess.num_of_guess, len(self.words_remain_lst), self.words_remain_lst, len(self.good_guesses_lst), self.good_guesses_lst, len(self.bad_guesses_lst), self.bad_guesses_lst, len(self.guesses_ready_to_submit), guesses_ready_to_submit_str)
                self.current_guess.process_guess()
                self.guesses_processed.append(self.current_guess)

                if self.current_guess.good_options_for_guess is False:
                    logger.info(
                        "No good options for guess. Starting over.")

                # If the current guess failed because of an error, start over from the beginning.
                if self.current_guess.guess_is_valid is False:
                    logger.info(
                        "Guess is not a valid guess to submit because of a formatting or content error. Starting over.")

                # If the current guess is ready to submit, add it to the list of guesses ready to submit.
                if self.current_guess.guess_is_ready_to_submit is True:
                    self.guesses_ready_to_submit.append(self.current_guess)
                    logger.info("Guess is ready to submit. Adding to list.")
            
            # If the guesses ready to submit list has enough guesses in it, evaluate them all and submit the best one.
            while (
                (len(self.good_guesses) < 2 and len(self.guesses_ready_to_submit) >= 5) or 
                (len(self.good_guesses) == 2 and len(self.guesses_ready_to_submit) >= 3)
            ):
                guesses_ready_to_submit_str = ""
                for guess in self.guesses_ready_to_submit:
                    guess_str = "Guess: \n"
                    guess_str += " ".join(guess.guess_lst)
                    guess_str += "\n Rationale: \n"
                    guess_str += guess.guess_rationale
                    guesses_ready_to_submit_str += f"{guess_str}\n"
                logger.info("%s guesses are ready to submit. Evaluating now...  \n %s",
                            len(self.guesses_ready_to_submit), guesses_ready_to_submit_str)
                self.evaluate_guesses_ready_to_submit_all()

            # If there are only four words left to solve, submit the guess that solves them.
            if len(self.good_guesses) == 3:
                logger.info("Only one possible solution left. Submitting.")
                self.current_guess = GuessActor(self)
                self.current_guess.guess_lst = self.words_remain_lst
                self.current_guess.do_submit()
                if self.current_guess.guess_was_submitted is True:
                    self.guesses_submitted.append(self.current_guess)
                    if self.current_guess.guess_is_correct is True:
                        self.good_guesses.append(self.current_guess)
                        self.good_guesses_lst.append(
                            self.current_guess.guess_lst)
                        # Extend the words_solved_lst to include each word in the guess_lst
                        self.words_solved_lst.extend(
                            self.current_guess.guess_lst)
                        # Make words_remain_lst be words_lst minus words_solved_lst
                        self.words_remain_lst = list(
                            set(self.puzzle.words_lst) - set(self.words_solved_lst))
                    else:
                        self.bad_guesses.append(self.current_guess)
                        self.bad_guesses_lst.append(
                            self.current_guess.guess_lst)
                        logger.debug("Number of bad guesses: %s",
                                     len(self.bad_guesses_lst))
            
            self.check_end_game_conditions()

        self.solve_time = time.time() - start_time
        minutes, seconds = divmod(self.solve_time, 60)
        minutes = int(minutes)
        seconds = int(seconds)
        logger.info("Puzzle finished in %s minutes and %s seconds.",
                    minutes, seconds)
        self.save_results_dict()
        self.save_outputs(filepath_md=self.path_md,
                          name=f"evaluations_puzzle_{self.puzzle.number}",
                          responses=self.evaluations
                          )
        if self.puzzle.solution_lst is not None:
            self.save_summary()
        else:
            self.save_summary_no_solution()
        self.save_summary_detailed_thorough()
        self.save_attributes(filepath_pkl=self.path_pkl,
                             name=f"puzzle_{self.puzzle.number}_actor")
        

    def evaluate_guesses_ready_to_submit_cot(self):
        """Decide which guesses are strongest for submitting."""
        # Load the system prompt from a .txt file
        prompt_system = ""
        if len(self.good_guesses) == 2:
            with open(os.path.join(
                get_root_dir(), 'data', 'prompts', 'actor', "evaluate_guesses_cot_final.txt"),
                'r', encoding='utf-8') as f:
                prompt = f.read()
        else:
            with open(os.path.join(
                    get_root_dir(), 'data', 'prompts', 'actor', "evaluate_guesses_cot.txt"),
                    'r', encoding='utf-8') as f:
                prompt = f.read()
        prompt_system += prompt
        # Add guesses ready to submit to the prompt
        guesses_ready_to_submit_str = ""
        # Create a string of the guesses ready to submit
        # Start by copying over guesses_ready_to_submit but not copying guesses that have the same set of words to submit
        # We do this so that each unique guess is included only once and so that the LLM does not discount the value of these answers for overlapping with one another
        guesses_ready_to_submit_no_overlap = []
        for guess in self.guesses_ready_to_submit:
            overlap = False
            for guess_no_overlap in guesses_ready_to_submit_no_overlap:
                if set(guess.guess_lst) == set(guess_no_overlap.guess_lst):
                    overlap = True
            if overlap is False:
                guesses_ready_to_submit_no_overlap.append(guess)
        # Next, shuffle the guesses ready to submit
        guesses_ready_shuffled = guesses_ready_to_submit_no_overlap.copy()
        random.shuffle(guesses_ready_shuffled)
        for guess in guesses_ready_shuffled:
            guess_str = "Guess: \n"
            guess_str += " ".join(guess.guess_lst)
            guess_str += "\n Rationale: \n"
            guess_str += guess.guess_rationale
            guesses_ready_to_submit_str += f"{guess_str}\n"
        prompt_system = prompt_system.replace(
            "{notes}", guesses_ready_to_submit_str)
        # Create a user prompt
        # Create a list that shuffles the words that remain to be solved
        words_remain_shuffled = self.words_remain_lst.copy()
        random.shuffle(words_remain_shuffled)
        # Create a string of the words that remain to be solved
        words_remain_str = " ".join(words_remain_shuffled)
        prompt_user = f"What is your top choice for a guess to submit for this puzzle? {words_remain_str}"
        # Set up prompts for the LLM
        prompts = [
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": prompt_user},
        ]
        # Call the LLM
        llm_response = llm_call(
            model=self.llm_settings.model, prompts=prompts, settings=self.llm_settings)
        logger.debug("LLM response evaluate_cot: \n %s", llm_response.output)
        return llm_response

    def evaluate_guesses_ready_to_submit_select(self, notes_str):
        """Select the best guess to submit."""
        # Load the system prompt from a .txt file
        with open(os.path.join(
                get_root_dir(), 'data', 'prompts', 'actor', 'evaluate_guesses_select.txt'),
                'r', encoding='utf-8') as f:
            prompt_system = f.read()
        # Within the system prompt, replace the placeholder {notes} with the notes_str
        prompt_system = prompt_system.replace("{notes}", notes_str)
        # Create a user prompt
        prompt_user = "Please select the best guess to submit."
        # Set up prompts for the LLM
        prompts = [
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": prompt_user},
        ]
        # Call the LLM
        llm_response = llm_call(
            model=self.llm_settings.model, prompts=prompts, settings=self.llm_settings)
        return llm_response

    def evaluate_guesses_ready_to_submit_all(self):
        """Call on LLM to evaluate the guesses ready to submit and submit the best one."""
        logger.info("Evaluating all guesses ready to submit. %s guesses ready to submit.",
                    len(self.guesses_ready_to_submit))
        # Evaluate the guesses ready to submit
        llm_response = self.evaluate_guesses_ready_to_submit_cot()
        self.evaluations.append(llm_response)
        # Select the best guess to submit
        llm_response = self.evaluate_guesses_ready_to_submit_select(
            llm_response.output)
        # Turn the guess into a list of words and fix formatting
        guess = llm_response.output
        # Remove "Output:" from guess if it appears in the string
        guess = guess.replace("Output:", "").strip()
        guess_lst = self.puzzle.split_puzzle_text(guess, 4, "***")
        logger.info("Guess selected to submit: %s", " ".join(guess_lst))
        # Identify the guess object that matches the guess selected to submit
        guess_set = set(guess_lst)
        # Check if the guess selected to submit matches any of the guesses ready to submit
        match_guess = False
        for guess in self.guesses_ready_to_submit:
            # If guess_set is the same as the set of words in the guess, match_guess is True
            if guess_set == set(guess.guess_lst):
                match_guess = True
                break
        # If the guess selected to submit does not match any of the guesses ready to submit, start over
        if match_guess is False:
            logger.info("Guess selected to submit does not match any guesses ready to submit. Starting over.")
            return
        
        for guess in self.guesses_ready_to_submit:
            # If guess_set is the same as the set of words in the guess, submit the guess
            if guess_set == set(guess.guess_lst):
                guess.do_submit()
                self.guesses_submitted.append(guess)
                # Remove from the list of guesses ready to submit
                self.guesses_ready_to_submit.remove(guess)
                if guess.guess_is_correct is True:
                    self.good_guesses.append(guess)
                    self.good_guesses_lst.append(guess.guess_lst)
                    # Extend the words_excluded_lst to include each word in the guess_lst
                    self.words_solved_lst.extend(guess.guess_lst)
                    # Make words_remain_lst be words_lst minus words_solved_lst
                    self.words_remain_lst = list(
                        set(self.puzzle.words_lst) - set(self.words_solved_lst))
                    # Iterate over a copy of the list using slicing [:]
                    for guess_ready in self.guesses_ready_to_submit[:]:
                        if all(word in self.words_remain_lst for word in guess_ready.guess_lst):
                            logger.info("Guess ready to submit still valid: %s",
                                        guess_ready.guess_lst)
                        else:
                            logger.info("Guess ready to submit no longer valid: %s",
                                        guess_ready.guess_lst)
                            self.guesses_ready_to_submit.remove(guess_ready)
                else:
                    self.bad_guesses.append(guess)
                    self.bad_guesses_lst.append(guess.guess_lst)
                    logger.debug("Number of bad guesses: %s",
                                 len(self.bad_guesses_lst))
                break
        # Remove any guesses that match the guess selected to submit from the list of guesses ready to submit
        for guess_ready in self.guesses_ready_to_submit[:]:
            # If the set of words in guess_lst matches, remove the guess
            if set(guess_ready.guess_lst) == guess_set:
                self.guesses_ready_to_submit.remove(guess_ready)
                logger.info("Removed guess from guesses ready to submit: %s",
                            guess_ready.guess_lst)

    def save_summary_detailed_thorough(self):
            """Save a summary of the results as a markdown file."""
            timestamp = get_timestamp()
            filename = f"summary_detailed_thorough_puzzle{self.puzzle.number}_{self.puzzle.llm_settings.model}_{timestamp}.md"
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
                    solution_str = " ".join(solution)
                    f.write(f"{solution_str}\n\n")
                # New detailed parts (everything above is same as save_summary)
                if len(self.evaluations) > 0:
                    f.write("## Evaluations\n\n")
                    for response in self.evaluations:
                        f.write(
                            f"### Evaluation {self.evaluations.index(response) + 1}\n\n")
                        f.write(f"{response.output}\n\n")
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
            logger.info("Saved detailed summary to %s", filepath)
