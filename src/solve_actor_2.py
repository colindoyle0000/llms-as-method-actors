"""SolveActor2 class is a class that solves the Connections puzzle using Actor-2 approach.
"""

import logging
import os
import re
import copy
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
from src.guess_actor_2 import GuessActor2

# Set up logger
logger = logging.getLogger('connections')

class SolveActor2(BaseSolver):
    """SolveActor2 class is a class that solves the Connections puzzle using Actor-2 approach.
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
        # New variables for Experiment Two
        # List of final guesses to submit
        self.guesses_final = []
        # Temporary words remain list
        self.temp_words_remain_lst = []
        # Guesses that have not been submitted but as a matter of logic based on other bad guesses must also be bad guesses
        self.logically_bad_guesses_lst = []
        
    
    def set_path_actor_2(self):
        """Set the path for saving data to file."""
        self.set_path(name="solve_actor_2")
 
    def solve_puzzle_actor_2(self):
        """Solve the puzzle using the Actor-2 approach.
        """
        start_time = time.time()
        logger.info("Solving puzzle using Actor-2 method. \n Words in puzzle: \n %s \n Solution: \n %s",
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
            self.guesses_final = []
            self.guesses_submitted = []
            self.good_guesses = []
            self.good_guesses_lst = []
            self.bad_guesses = []
            self.bad_guesses_lst = []
            self.end_game = False
            self.success = False
        while self.end_game is False:

            
            # If the puzzle is not solved, create a new guess
            if self.end_game is False:
                
                logger.info("Start of process. \n New Guess!")
                self.temp_words_remain_lst = self.words_remain_lst.copy()
                logger.info("Temporary words remain list set to words list: %s", self.temp_words_remain_lst)
                
                if len(self.good_guesses) <= 1:
                    logger.info("0 or 1 Good guesses. Setting temporary words remain list.")    
                    if len(self.guesses_ready_to_submit) >= 2:
                        # If the words in the last guess in ready to submit have already come up twice in the
                        # ready to submit list, remove them from the temporary words remain list
                        set_last_guess_lst = set(self.guesses_ready_to_submit[-1].guess_lst)
                        count_appearance_last_guess = 0
                        for guess in self.guesses_ready_to_submit:
                            if set_last_guess_lst == set(guess.guess_lst):
                                count_appearance_last_guess += 1
                        if count_appearance_last_guess >= 2:
                            logger.info("Last guess ready to submit has appeared twice or more. Removing from temporary words remain list.")
                            for word in self.guesses_ready_to_submit[-1].guess_lst:
                                self.temp_words_remain_lst.remove(word)
                            logger.info("Temporary words remain list after removing last guess ready to submit: %s", self.temp_words_remain_lst)                        
                    if len(self.guesses_final) > 0 and len(self.good_guesses) == 0:
                        # Pick a random number either 0 or 1
                        random_removal_num = random.randint(0, 1)
                        # If the random number is 1, remove all words from a random guess in the final guesses list from the temporary words remain list
                        if random_removal_num == 1:
                            random_guess_final = random.choice(self.guesses_final)
                            for word in random_guess_final.guess_lst:
                                if word in self.temp_words_remain_lst:
                                    self.temp_words_remain_lst.remove(word)
                            logger.info("Temporary words remain list after removing random guess from final guesses: %s", self.temp_words_remain_lst)
                        else:
                            logger.info("Random number was 0. Not removing words from temporary words remain list based on a random guess from final guesses.")
                elif len(self.good_guesses) == 2:
                    logger.info("Two good guesses. Setting temporary words remain list.")
                    if len(self.bad_guesses) < 2:
                        logger.info("Fewer than two bad guesses. Keeping all words in temporary words remain list as is.")
                    elif len(self.bad_guesses) == 2:
                        random_single_mole_num = random.randint(0, 1)
                        for i, guess_lst in enumerate(self.good_guesses_lst):
                            if i == random_single_mole_num:
                                random_mole_word = random.choice(guess_lst)
                                self.temp_words_remain_lst.append(random_mole_word)
                                logger.info("Two bad guesses. Including one random 'mole' word in temporary words remain list. \n %s", self.temp_words_remain_lst)
                    else:
                        for guess_lst in self.good_guesses_lst:
                            random_mole_word = random.choice(guess_lst)
                            self.temp_words_remain_lst.append(random_mole_word)
                            logger.info("Three bad guesses. Including two random 'mole' words (one from each guess in good_guesses).")           
                # Create a new guess
                self.current_guess = GuessActor2(self)
                guesses_ready_to_submit_str = "Guesses ready to submit: \n"
                for guess in self.guesses_ready_to_submit:
                    guess_str = "Guess: \n"
                    guess_str += " ".join(guess.guess_lst)
                    guess_str += "\n Rationale: \n"
                    guess_str += guess.guess_rationale
                    guesses_ready_to_submit_str += f"{guess_str}\n"
                guesses_final_str = "Final guesses: \n"
                for guess in self.guesses_final:
                    guess_str = "Guess: \n"
                    guess_str += " ".join(guess.guess_lst)
                    guess_str += "\n Rationale: \n"
                    guess_str += guess.guess_rationale
                    guesses_final_str += f"{guess_str}\n"
                logger.info("Starting New Guess! \n Current guess number: %s \n %s words remaining \n Temporary word remain list: \n %s  \n %s good guesses so far: \n %s \n %s bad guesses so far: \n %s \n %s guesses ready to submit: \n %s  \n %s final guesses: \n %s",
                            self.current_guess.num_of_guess, len(self.words_remain_lst), self.words_remain_lst, len(self.good_guesses_lst), self.good_guesses_lst, len(self.bad_guesses_lst), self.bad_guesses_lst, len(self.guesses_ready_to_submit), guesses_ready_to_submit_str, len(self.guesses_final), guesses_final_str)
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
            
            if len(self.good_guesses) < 2:
                logger.info("Fewer than two good guesses.")
                if len(self.guesses_final) == 0:
                    logger.info("Final guesses list is empty.")
                    if len(self.guesses_ready_to_submit) >= 5:
                        logger.info("Five or more guesses ready to submit. Evaluating now.")
                        self.evaluate_guesses_ready_to_submit_all()
                else:
                    logger.info("Final guesses list is not empty.")
                    if len(self.guesses_ready_to_submit) >= 5:
                        no_overlap_count = 0
                        for guess in self.guesses_ready_to_submit:
                            for guess_final in self.guesses_final:
                                if set(guess.guess_lst) != set(guess_final.guess_lst):
                                    no_overlap_count += 1
                            for guess_good in self.good_guesses:
                                if set(guess.guess_lst) != set(guess_good.guess_lst):
                                    no_overlap_count += 1
                            if no_overlap_count >= 2:
                                logger.info("Two or more guesses do not overlap with final guesses or good guesses. Five or more guesses ready to submit. Evaluating now.")
                                self.evaluate_guesses_ready_to_submit_all()
                                break
                
                # If there are two non-overlapping guesses in guesses_final, start submitting.
                guesses_two_no_overlap = []
                for current_guess in self.guesses_final:
                    # Only proceed if the current guess is not already in guesses_two_no_overlap
                    if current_guess not in guesses_two_no_overlap:
                        for match_guess in self.guesses_final:
                            logger.debug("Checking overlap between guesses: %s and %s",
                                        current_guess.guess_lst, match_guess.guess_lst)
                            overlap = False
                            for word in current_guess.guess_lst:
                                if word in match_guess.guess_lst:
                                    overlap = True
                            if overlap is False:
                                logger.info("No overlap between guesses: %s and %s",
                                            current_guess.guess_lst, match_guess.guess_lst)
                                guesses_two_no_overlap.append(current_guess)
                                guesses_two_no_overlap.append(match_guess)
                if len(guesses_two_no_overlap) == 2:
                    logger.info("Two non-overlapping guesses in guesses_final. Submitting.")
                    # Submit the guess with fewer words in common with other guesses
                    guess0_words_in_common = 0
                    guess1_words_in_common = 0
                    for word in guesses_two_no_overlap[0].guess_lst:
                        for guess in self.guesses_final:
                            if word in guess.guess_lst:
                                guess0_words_in_common += 1
                    for word in guesses_two_no_overlap[1].guess_lst:
                        for guess in self.guesses_final:
                            if word in guess.guess_lst:
                                guess1_words_in_common += 1
                    logger.info(" %s words in common in final guesses with %s /n %s words in common in final guesses with %s.",
                                guess0_words_in_common, guesses_two_no_overlap[0].guess_lst, guess1_words_in_common, guesses_two_no_overlap[1].guess_lst)
                    if guess0_words_in_common <= guess1_words_in_common:
                        logger.info("Submitting %s", guesses_two_no_overlap[0].guess_lst)
                        self.submit_guess_final(guesses_two_no_overlap[0])
                        # if submission is good, submit the other one
                        if guesses_two_no_overlap[0].guess_is_correct is True:
                            logger.info("Submitting %s", guesses_two_no_overlap[1].guess_lst)
                            self.submit_guess_final(guesses_two_no_overlap[1])
                    elif guess1_words_in_common < guess0_words_in_common:
                        logger.info("Submitting %s", guesses_two_no_overlap[1].guess_lst)
                        self.submit_guess_final(guesses_two_no_overlap[1])
                        # if submission is good, submit the other one
                        if guesses_two_no_overlap[1].guess_is_correct is True:
                            logger.info("Submitting %s", guesses_two_no_overlap[0].guess_lst)
                            self.submit_guess_final(guesses_two_no_overlap[0])
                elif len(guesses_two_no_overlap) > 2:
                    logger.info("Three or more non-overlapping guesses in guesses_final. Submitting one.")
                    # Submit the guess that doesn't have words in common with the other guesses
                    for guess in guesses_two_no_overlap:
                        words_in_common = 0
                        for word in guess.guess_lst:
                            for match_guess in guesses_two_no_overlap:
                                # Only check if the guess is not the same as the match_guess
                                if guess != match_guess:
                                    if word in match_guess.guess_lst:
                                        words_in_common += 1
                                        logger.debug("%s has words in common with %s", guess.guess_lst, match_guess.guess_lst)
                        if words_in_common == 0:
                            logger.info("Unique guess! Submitting %s", guess.guess_lst)
                            self.submit_guess_final(guess)
                            break
                
                # If there are three identical guesses in guesses_final, submit one of them.
                guesses_three_identical = []
                for current_guess in self.guesses_final:
                    guesses_three_identical = []
                    guesses_three_identical.append(current_guess)
                    for match_guess in self.guesses_final:
                        if current_guess != match_guess:
                            if set(current_guess.guess_lst) == set(match_guess.guess_lst):
                                guesses_three_identical.append(match_guess)
                    if len(guesses_three_identical) == 3:
                        logger.info("Three identical guesses in guesses_final. \n %s \n %s \n %s \n Submitting one.",
                                    guesses_three_identical[0].guess_lst, guesses_three_identical[1].guess_lst, guesses_three_identical[2].guess_lst)
                        self.submit_guess_final(guesses_three_identical[0])
                        break
                    
                            
            if len(self.good_guesses) == 2:
                logger.info("Two good guesses.")
                if len(self.guesses_ready_to_submit) >= 3:
                    logger.info("Three or more guesses ready to submit. Evaluating now.")
                    self.evaluate_guesses_ready_to_submit_all()
                
                # If there are two non-overlapping guesses in guesses_final, start submitting.
                guesses_two_no_overlap = []
                for current_guess in self.guesses_final:
                    # Only proceed if the current guess is not already in guesses_two_no_overlap
                    if current_guess not in guesses_two_no_overlap:
                        for match_guess in self.guesses_final:
                            logger.debug("Checking overlap between guesses: %s and %s",
                                        current_guess.guess_lst, match_guess.guess_lst)
                            overlap = False
                            for word in current_guess.guess_lst:
                                if word in match_guess.guess_lst:
                                    overlap = True
                            if overlap is False:
                                logger.info("No overlap between guesses: %s and %s",
                                            current_guess.guess_lst, match_guess.guess_lst)
                                guesses_two_no_overlap.append(current_guess)
                                guesses_two_no_overlap.append(match_guess)
                if len(guesses_two_no_overlap) == 2:
                    logger.info("Two non-overlapping guesses in guesses_final. Submitting.")
                    self.submit_guess_final(guesses_two_no_overlap[0])
                    if guesses_two_no_overlap[0].guess_is_correct is True:
                        logger.info("Submitting %s", guesses_two_no_overlap[1].guess_lst)
                        self.submit_guess_final(guesses_two_no_overlap[1])
                    else:
                        logger.info("Because the first guess was incorrect, removing %s from guesses_final", guesses_two_no_overlap[1].guess_lst)
                        self.guesses_final.remove(guesses_two_no_overlap[1])
                elif len(self.guesses_final) > 1:
                    # If there are two identical guesses in guesses_final, submit one of them.
                    guesses_two_identical = []
                    for current_guess in self.guesses_final:
                        for match_guess in self.guesses_final:
                            if current_guess != match_guess:
                                if set(current_guess.guess_lst) == set(match_guess.guess_lst):
                                    logger.info("Two identical guesses in guesses_final. Submitting one.")
                                    self.submit_guess_final(current_guess)
                                    break
                    if len(self.guesses_final) > 1 and len(self.guesses_processed) > 20:
                        logger.info("More than one guess in guesses_final and more than 20 guesses processed. Returning to ready to submit list.")
                        # Go through self.guesses_final and add each guess to self.guesses_ready_to_submit
                        for guess in self.guesses_final:
                            self.guesses_ready_to_submit.append(guess)
                        self.guesses_final = []
                elif len(self.guesses_final) == 1 and len(self.guesses_processed) > 15:
                    logger.info("One guess in guesses_final and more than 15 guesses processed. Submitting.")
                    for guess in self.guesses_final:
                        self.submit_guess_final(guess)


            # If there are only four words left to solve, submit the guess that solves them.
            if len(self.good_guesses) == 3:
                logger.info("Only one possible solution left. Submitting.")
                self.current_guess = GuessActor2(self)
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
                             name=f"puzzle_{self.puzzle.number}_actor_2")
        

    def evaluate_guesses_ready_to_submit_cot(self):
        """Decide which guesses are strongest for submitting."""
        # Load the system prompt from a .txt file
        prompt_system = ""
        if len(self.good_guesses) == 2:
            with open(os.path.join(
                get_root_dir(), 'data', 'prompts', 'actor_2', "evaluate_guesses_cot_final.txt"),
                'r', encoding='utf-8') as f:
                prompt = f.read()
        else:
            with open(os.path.join(
                    get_root_dir(), 'data', 'prompts', 'actor_2', "evaluate_guesses_cot.txt"),
                    'r', encoding='utf-8') as f:
                prompt = f.read()
        prompt_system += prompt
        # Add guesses ready to submit to the prompt
        guesses_ready_to_submit_str = ""
        # Create a string of the guesses ready to submit
        # Start by copying over guesses_ready_to_submit but not copying guesses that have the same set of words to submit
        # We do this so that each unique guess is included only once and so that the LLM does not discount the value of these answers for overlapping with one another
        guesses_ready_to_submit_no_overlap = []
        # Make a deep copy of guesses_ready_to_submit
        guesses_ready_copy = copy.deepcopy(self.guesses_ready_to_submit)
        random.shuffle(guesses_ready_copy)
        for guess in guesses_ready_copy:
            overlap = False
            for guess_no_overlap in guesses_ready_to_submit_no_overlap:
                if set(guess.guess_lst) == set(guess_no_overlap.guess_lst):
                    overlap = True
            if overlap is False:
                guesses_ready_to_submit_no_overlap.append(guess)
        # Shuffle the guesses ready to submit
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
                get_root_dir(), 'data', 'prompts', 'actor_2', 'evaluate_guesses_select.txt'),
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
        guesses_ready_to_submit_str = ""
        for guess in self.guesses_ready_to_submit:
            guess_str = "Guess: \n"
            guess_str += " ".join(guess.guess_lst)
            guess_str += "\n Rationale: \n"
            guess_str += guess.guess_rationale
            guesses_ready_to_submit_str += f"{guess_str}\n"
        logger.info("%s guesses are ready to submit. Evaluating now...  \n %s",
                    len(self.guesses_ready_to_submit), guesses_ready_to_submit_str)
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
            # If guess_set is the same as the set of words in the guess, add the guess to guesses_final
            if guess_set == set(guess.guess_lst):
                # Add the guess to guesses_final
                self.guesses_final.append(guess)
                # Remove from the list of guesses ready to submit
                self.guesses_ready_to_submit.remove(guess)
                # Remove any guesses from guesses ready to submit that have the same set of words as the guess selected to submit
                for guess_ready in self.guesses_ready_to_submit[:]:
                    if set(guess_ready.guess_lst) == guess_set:
                        self.guesses_ready_to_submit.remove(guess_ready)
                        logger.info("Removed guess from guesses ready to submit: %s",
                                    guess_ready.guess_lst)
                break
        for guess in self.guesses_ready_to_submit:
            # Increment the count of how many times the guess has been evaluated for submission as a final guess.
            guess.guess_eval_count += 1
            logger.info("Guess %s has been evaluated %s times for submission as a final guess.",
                        guess.guess_lst, guess.guess_eval_count)
            # Remove guesses that have been evaluated four or more times
            if guess.guess_eval_count >= 4:
                logger.info("Guess %s has been evaluated four or more times for submission as a final guess. Removing from consideration.",
                            guess.guess_lst)
                self.guesses_ready_to_submit.remove(guess)
    
    def submit_guess_final(self, guess):
        # If the length of words_remain_lst is 8, make sure the four words not in the guess are not in a guess in the bad guesses list
        if len(self.words_remain_lst) == 8:
            bad_guess_check_lst = []
            for word in self.words_remain_lst:
                if word not in guess.guess_lst:
                    bad_guess_check_lst.append(word)
            for bad_guess in self.bad_guesses:
                if set(bad_guess_check_lst) == set(bad_guess.guess_lst):
                    logger.info("Words in guess to be submitted are the other half of four words that are a bad guess. Not submitting.")
                    self.guesses_final.remove(guess)
                    match_bad_guess = False
                    for bad_guess in self.logically_bad_guesses_lst:
                        if set(bad_guess) == set(guess.guess_lst):
                            match_bad_guess = True
                            break
                    if match_bad_guess is False:
                        logger.info("Adding guess to logically bad guesses list: %s", guess.guess_lst)
                        self.logically_bad_guesses_lst.append(guess.guess_lst)
                    guess.guess_is_correct = False
                    return
        guess.do_submit()
        self.guesses_submitted.append(guess)
        if guess in self.guesses_final:
            self.guesses_final.remove(guess)
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
            for guess_ready in self.guesses_final[:]:
                if all(word in self.words_remain_lst for word in guess_ready.guess_lst):
                    logger.info("Guess final still valid: %s",
                                guess_ready.guess_lst)
                else:
                    logger.info("Guess final no longer valid: %s",
                                guess_ready.guess_lst)
                    self.guesses_final.remove(guess_ready)
        else:
            self.bad_guesses.append(guess)
            self.bad_guesses_lst.append(guess.guess_lst)
            guess_set = set(guess.guess_lst)
            for guess_ready in self.guesses_ready_to_submit[:]:
                if guess_set == set(guess_ready.guess_lst):
                    self.guesses_ready_to_submit.remove(guess_ready)
                    logger.info("Removed matching guess from guesses ready to submit: %s",guess_ready.guess_lst)
            for guess_final in self.guesses_final[:]:
                if guess_set == set(guess_final.guess_lst):
                    self.guesses_final.remove(guess_final)
                    logger.info("Removed matching guess from guesses final: %s",guess_final.guess_lst)
                
            if len(self.words_remain_lst) == 8:
                logger.info("Only eight words left. Other four words not in bad guess must also be bad guesses.")
                logically_bad_guess = []
                for word in self.words_remain_lst:
                    if word not in guess.guess_lst:
                        logically_bad_guess.append(word)
                self.logically_bad_guesses_lst.append(logically_bad_guess)
                logger.info("Logically bad guesses list: %s", self.logically_bad_guesses_lst)
                        
            logger.debug("Number of bad guesses: %s",
                            len(self.bad_guesses_lst))
                

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
