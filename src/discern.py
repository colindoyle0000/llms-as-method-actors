"""Discern class for discerning valuable answers from brainstorming notes for Actor approach."""
import os
import logging
import random
from src.baseclass import BaseClass
from src.utils_file import (
    get_root_dir
)
from src.utils_llm import (
    llm_call
)

from src.utils_tokens import (
    list_to_token_list,
    num_tokens
)

from src.utils_string import get_timestamp

# Set up logger
logger = logging.getLogger('connections')


class Discern(BaseClass):
    """Class for discerning valuable answers from brainstorming note for Actor approach."""

    def __init__(
        self,
        guess,
        brainstorm_responses,
    ):
        self.guess = guess
        self.puzzle = guess.puzzle
        self.solve = guess.solve
        # LLM settings for discerning
        self.llm_settings = self.puzzle.llm_settings
        # Brainstorm responses
        self.brainstorm_responses = brainstorm_responses
        # Brainstorm outputs as a list of items sized to match chunk token size
        self.brainstorm_notes_token_lst = []
        # Extracted answers from brainstorming notes
        self.extract_responses = []
        self.extract_outputs = []
        # Discerning best guess from extracted answers
        self.discern_responses = []
        self.discern_outputs = []
        self.discern_guess_str = ""
        # Deciding whether to select a guess to submit or go back to brainstorming
        self.decide_cot_responses = []
        self.decide_cot_outputs = []
        # Decide Yes-No
        self.decide_yn_responses = []
        self.decide_yn_outputs = []
        # Select guess
        self.select_responses = []
        self.select_outputs = []
        # Submit guess
        self.submit_guess = True

    def set_llm_temperature(self):
        """Set the LLM temperature setting for discern.
        Note that this is not currently used in the code. It is here for any future experiments in changing the temperature for brainstorming process.
        """
        self.llm_settings.temperature = 0.6
        logger.info("Setting LLM temperature to %s for discerning.",
                    self.llm_settings.temperature)

    def extract_answers(self, brainstorm_notes_str):
        """Extract viable answers from brainstorming notes."""
        # Load the system prompt from a .txt file
        with open(os.path.join(
                get_root_dir(), 'data', 'prompts', 'actor', 'extract.txt'),
                'r', encoding='utf-8') as f:
            prompt_system = f.read()
        # Within the system prompt, replace the placeholder {notes} with the brainstorming notes
        prompt_system = prompt_system.replace("{notes}", brainstorm_notes_str)
        # If bad guesses have been made, add them to the system prompt
        bad_guesses_str = self.guess.set_bad_guesses_str()
        prompt_system = prompt_system.replace('{bad_guesses}', bad_guesses_str)
        if len(self.solve.guesses_ready_to_submit) > 0:
            ready_to_submit_str = ""
            ready_to_submit_str = "\n You have already decided to submit the following guesses, so you should not select them again as a guess to submit: \n"
            for guess in self.solve.guesses_ready_to_submit:
                guess_str = " ".join(guess.guess_lst)
                ready_to_submit_str += f"{guess_str}\n"
            prompt_system = prompt_system + ready_to_submit_str
        # Create a user prompt
        # Create a list that shuffles the words that remain to be solved
        words_remain_shuffled = self.solve.words_remain_lst.copy()
        random.shuffle(words_remain_shuffled)
        # Create a string of the words that remain to be solved
        words_remain_str = " ".join(words_remain_shuffled)
        prompt_user = f"From your brainstorming notes, extract viable answers for this puzzle: {words_remain_str}"
        # Set up prompts for the LLM
        prompts = [
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": prompt_user},
        ]
        # Call the LLM
        llm_response = llm_call(
            model=self.llm_settings.model, prompts=prompts, settings=self.llm_settings)
        return llm_response

    def extract_all(self):
        """Extract all viable answers from brainstorming notes."""
        self.brainstorm_notes_token_lst = []
        self.extract_responses = []
        self.extract_outputs = []
        # Turn the brainstorming notes list into a list of max_token sized strings
        brainstorm_notes_lst = []
        for response in self.brainstorm_responses:
            brainstorm_notes_lst.append(response.output)
        brainstorm_notes_lst = [
            f"## Brainstorming Note #{i+1} \n \n" + note + "\n *** \n" for i, note in enumerate(brainstorm_notes_lst)]
        self.brainstorm_notes_token_lst = list_to_token_list(
            brainstorm_notes_lst, self.llm_settings.chunk_size, self.llm_settings.chunk_overlap)
        logger.info("Created token list of brainstorming notes. Number of notes in list: %s",
                    len(self.brainstorm_notes_token_lst))
        # For each set of notes in the token list, extract answers
        for notes in self.brainstorm_notes_token_lst:
            count = 1
            logger.info(
                "Extracting answers from brainstorming notes... %s of %s", count, len(self.brainstorm_notes_token_lst))
            # Extract answers from the brainstorming notes
            response = self.extract_answers(notes)
            self.extract_responses.append(response)
            self.extract_outputs.append(response.output)
            count += 1

    def discern_guess(self, extract_notes_str: str):
        """Discern valuable answers from answers extracted from brainstorming notes."""
        # Load the system prompt from a .txt file
        with open(os.path.join(
                get_root_dir(), 'data', 'prompts',  'actor', 'discern.txt'),
                'r', encoding='utf-8') as f:
            prompt_system = f.read()
        # Within the system prompt, replace the placeholder {notes} with the extract notes
        prompt_system = prompt_system.replace("{notes}", extract_notes_str)
        # If bad guesses have been made, add them to the system prompt
        bad_guesses_str = self.guess.set_bad_guesses_str()
        prompt_system = prompt_system.replace('{bad_guesses}', bad_guesses_str)
        # Create a user prompt
        # Create a list that shuffles the words that remain to be solved
        words_remain_shuffled = self.solve.words_remain_lst.copy()
        random.shuffle(words_remain_shuffled)
        # Create a string of the words that remain to be solved
        words_remain_str = " ".join(words_remain_shuffled)
        prompt_user = f"From your notes, let's discern the strongest viable guesses for this puzzle: {words_remain_str}"

        # Set up prompts for the LLM
        prompts = [
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": prompt_user},
        ]
        # Call the LLM
        llm_response = llm_call(
            model=self.llm_settings.model, prompts=prompts, settings=self.llm_settings)
        return llm_response

    def discern_guess_all(self):
        """Discern the best guess from extracted answers."""
        self.discern_responses = []
        self.discern_outputs = []
        self.discern_guess_str = ""
        # Turn the extracted notes list into a list of max_token sized strings
        extract_notes_token_lst = list_to_token_list(
            self.extract_outputs, self.llm_settings.chunk_size, self.llm_settings.chunk_overlap)
        logger.info("Created token list of extracted notes. Number of notes in list: %s",
                    len(extract_notes_token_lst))
        # For each set of notes in the token list, discern the best guess
        for notes in extract_notes_token_lst:
            count = 1
            logger.info(
                "Discerning the best guess from extracted answers... %s of %s", count, len(extract_notes_token_lst))
            # Discern the best guess from the extracted answers
            response = self.discern_guess(notes)
            self.discern_responses.append(response)
            self.discern_outputs.append(response.output)
            count += 1
        if len(extract_notes_token_lst) > 1:
            # If needing to run discern method multiple times, do a final run of the discern method on the outputs of the prior runs
            logger.info(
                "Discerning best guess from all prior discerned guesses...")
            # For the discern outputs, join them into a single string
            discern_notes_str = " ".join(self.discern_outputs)
            self.discern_responses = []
            self.discern_outputs = []
            self.discern_guess_str = ""
            # Discern the best guess from the discerned guesses
            response = self.discern_guess(discern_notes_str)
            self.discern_responses.append(response)
            self.discern_outputs.append(response.output)
        self.discern_guess_str = " ".join(self.discern_outputs)

    def decide_cot(self, discern_guess_str: str):
        """Decide whether to submit a guess from the discern method."""
        # Load the system prompt from a .txt file
        with open(os.path.join(
                get_root_dir(), 'data', 'prompts',  'actor', 'decide_cot.txt'),
                'r', encoding='utf-8') as f:
            prompt_system = f.read()
        # If bad guesses have been made, add them to the system prompt
        bad_guesses_str = self.guess.set_bad_guesses_str()
        prompt_system = prompt_system.replace('{bad_guesses}', bad_guesses_str)
        # Within the system prompt, replace the placeholder {notes} with the discerned guess
        prompt_system = prompt_system.replace("{notes}", discern_guess_str)
        # Create a user prompt
        # Create a list that shuffles the words that remain to be solved
        words_remain_shuffled = self.solve.words_remain_lst.copy()
        random.shuffle(words_remain_shuffled)
        # Create a string of the words that remain to be solved
        words_remain_str = " ".join(words_remain_shuffled)
        prompt_user = f"Should I submit a guess from these notes as an answer for this puzzle: {words_remain_str}"
        # Set up prompts for the LLM
        prompts = [
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": prompt_user},
        ]
        # Call the LLM
        llm_response = llm_call(
            model=self.llm_settings.model, prompts=prompts, settings=self.llm_settings)
        return llm_response

    def decide_yn(self, decide_cot_str: str):
        """Interpret the output of the LLM in decide_cot to decide yes or no."""
        # Yes = submit guess
        # No = brainstorm
        # Load the system prompt from a .txt file
        with open(os.path.join(get_root_dir(), 'data', 'prompts', 'actor', 'decide_yn.txt'), 'r', encoding='utf-8') as f:
            prompt_system = f.read()
        # Within the system prompt, replace {notes} with decide_cot notes
        prompt_system = prompt_system.replace('{notes}', decide_cot_str)
        # Create a user prompt
        prompt_user = "Yes = submit a guess. No = go back to brainstorming."
        # Set up prompts for the LLM
        prompts = [
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": prompt_user},
        ]
        # Call the LLM
        llm_response = llm_call(
            model=self.llm_settings.model_cheap, prompts=prompts, settings=self.llm_settings)
        return llm_response

    def decide_all(self):
        """Go through decide process."""
        self.decide_cot_responses = []
        self.decide_cot_outputs = []
        self.decide_yn_responses = []
        self.decide_yn_outputs = []
        response = self.decide_cot(self.discern_guess_str)
        self.decide_cot_responses.append(response)
        self.decide_cot_outputs.append(response.output)
        response = self.decide_yn(response.output)
        self.decide_yn_responses.append(response)
        self.decide_yn_outputs.append(response.output)
        if "yes" in response.output.lower():
            logger.info(
                "Discern method produced good options for a guess. Continuing...")
            self.guess.good_options_for_guess = True
        else:
            logger.info(
                "Discern method did not produce good options for a guess. Need to start over.")
            self.guess.good_options_for_guess = False

    def select(self, notes_str: str):
        """Select the best discerned guess."""
        # Load the system prompt from a .txt file
        with open(os.path.join(
                get_root_dir(), 'data', 'prompts', 'actor', 'select.txt'),
                'r', encoding='utf-8') as f:
            prompt_system = f.read()
        # Within the system prompt, replace the placeholder {notes} with the notes_str
        prompt_system = prompt_system.replace("{notes}", notes_str)
        # If bad guesses have been made, add them to the system prompt
        bad_guesses_str = self.guess.set_bad_guesses_str()
        prompt_system = prompt_system.replace('{bad_guesses}', bad_guesses_str)
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

    def select_fix(self, guess_str: str):
        """If the guess does not contain four words, ask the LLM to fix it."""
        # Load the system prompt from a .txt file
        with open(os.path.join(
                get_root_dir(), 'data', 'prompts', 'select_fix.txt'),
                'r', encoding='utf-8') as f:
            prompt_system = f.read()
        # Create a user prompt
        prompt_user = f"Please fix the guess: {guess_str}"
        # Set up prompts for the LLM
        prompts = [
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": prompt_user},
        ]
        # Call the LLM
        llm_response = llm_call(
            model=self.llm_settings.model, prompts=prompts, settings=self.llm_settings)
        return llm_response

    def select_all(self):
        """Select the best discerned guess."""
        self.select_responses = []
        self.select_outputs = []
        # Run the select function to get a guess from the LLM
        logger.info("Selecting the best guess...")
        notes_str = ""
        for response in self.decide_cot_responses:
            notes_str += response.output
            notes_str += "/n *** /n"
        llm_response = self.select(notes_str)
        self.select_responses.append(llm_response)
        self.select_outputs.append(llm_response.output)
        # Turn the guess into a list of words and fix formatting
        guess = llm_response.output
        # Remove "Output:" or "Response:" from guess if it appears in the string
        guess = guess.replace("Output:", "").strip()
        guess = guess.replace("Response:", "").strip()
        guess_lst = self.puzzle.split_puzzle_text(guess, 4, "***")
        
        # Sort the guess_lst in alphabetical order
        guess_lst = sorted(guess_lst)  
        
        if len(guess_lst) != 4:
            logger.warning(
                "Guess does not contain four words. Trying to get LLM to fix...")
            llm_response = self.select_fix(guess)
            # Turn the guess into a list of words and fix formatting
            guess = llm_response.output
            # Remove "Output:" from guess if it appears in the string
            guess = guess.replace("Output:", "").strip()
            guess_lst = self.puzzle.split_puzzle_text(guess, 4, "***")
            if len(guess_lst) != 4:
                logger.warning(
                    "Failed to fix guess. Guess still does not contain four words.")
            else:
                logger.info("Fixed guess!")
        
        self.guess.guess_lst = guess_lst
        logger.info("Selected guess: %s", " ".join(guess_lst))

    def validate_guess_format(self):
        """Validate the guess formatting."""
        # If the guess list has more or less than four items, log a warning
        if len(self.guess.guess_lst) != 4:
            logger.warning("Invalid guess. Guess does not contain four words.")
            return False
        else:
            logger.info("Valid guess format. Guess contains four words.")
            return True

    def validate_guess_content(self):
        """Check to make sure the guess content can be submmitted."""
        # Conditions for valid guess content:
        # - The guess only contains words from the words_remain_lst
        # - The guess is not already in bad_guesses_lst
        guess_set = set(self.guess.guess_lst)
        if not guess_set.issubset(set(self.solve.words_remain_lst)):
            logger.info(
                "Invalid guess. Guess contains words not in words_remain_lst.")
            return False
        for bad_guess in self.solve.bad_guesses_lst:
            if guess_set == set(bad_guess):
                logger.info(
                    "Invalid guess: Guess is already in bad_guesses_lst.")
                return False
        logger.info("Valid guess content.")
        return True


    def select_and_validate_all(self):
        """Select the best guess and validate it for errors."""

        # Select guess
        self.select_all()

        # Validate the guess formatting, and if it is not valid, try again
        attempts = 1
        while self.validate_guess_format() is False or self.validate_guess_content() is False:
            if attempts > 2:
                logger.warning(
                    "Failed to select a correctly formatted guess after retrying.")
                return False
            logger.warning("Trying to select guess again...")
            self.select_all()
            attempts += 1
        return True

    def make_ready_to_submit(self):
        """Make the guess ready to submit by summarizing rationale."""
        logger.info("Making guess ready to submit.")
        self.guess.guess_rationale = ""
        # Load the system prompt from a .txt file
        with open(os.path.join(
                get_root_dir(), 'data', 'prompts', 'actor', 'make_ready_to_submit.txt'),
                'r', encoding='utf-8') as f:
            prompt_system = f.read()
        # Within the system prompt, replace the placeholder {guess} with the guess
        prompt_system = prompt_system.replace(
            "{guess}", " ".join(self.guess.guess_lst))
        # Within the system prompt, replace the placeholder {notes} with decide_cot outputs
        notes_str = ""
        for response in self.decide_cot_responses:
            notes_str += response.output
            notes_str += "/n *** /n"
        prompt_system = prompt_system.replace("{notes}", notes_str)
        # Create a user prompt
        prompt_user = "Please summarize the connection and rationale for this guess."
        # Set up prompts for the LLM
        prompts = [
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": prompt_user},
        ]
        # Call the LLM
        llm_response = llm_call(
            model=self.llm_settings.model, prompts=prompts, settings=self.llm_settings)
        self.guess.guess_rationale = llm_response.output
        self.guess.guess_is_ready_to_submit = True
