"""Base class for all classes in the project.

This class provides methods for saving instance attributes to disk and loading them back, 
as well as for saving outputs in a markdown file format.
"""

import os
import pickle
import logging
import time

from src.utils_string import get_timestamp

# Set up logger
logger = logging.getLogger('connections')

class BaseClass:
    """Base class for all classes in the project.
    
    Attributes:
        num_responses (int): Number of responses.
        num_input_tokens (int): Number of input tokens.
        num_output_tokens (int): Number of output tokens.
    """
    
    def __init__(self):
        """Initialize the BaseClass with default values."""
        self.num_responses = 0
        self.num_input_tokens = 0
        self.num_output_tokens = 0

    def save_attributes(self, filepath_pkl, name):
        """Save the instance attributes to a .pkl file.
        
        Args:
            filepath_pkl (str): The directory path where the .pkl file will be saved.
            name (str): The name of the .pkl file.
        
        Raises:
            Exception: If saving fails due to file permission or path errors.
        """
        directory = os.path.join(filepath_pkl)
        os.makedirs(directory, exist_ok=True)
        filename = os.path.join(filepath_pkl, f"{name}.pkl")
        with open(filename, 'wb') as f:
            pickle.dump(self.__dict__, f)
            logger.info("Saved attributes to .pkl file: %s", filename)

    def load_attributes(self, filename: str = None, filepath_pkl: str = None, name: str = None):
        """Load attributes from a .pkl file.
        
        Args:
            filename (str, optional): The full path to the .pkl file.
            filepath_pkl (str, optional): The directory path where the .pkl file is located.
            name (str, optional): The name of the .pkl file.
        
        Raises:
            FileNotFoundError: If the specified file does not exist.
        """
        if filename is not None:
            try:
                with open(filename, 'rb') as f:
                    data = pickle.load(f)
                for key, value in data.items():
                    setattr(self, key, value)
            except FileNotFoundError:
                logger.warning("File not found: %s", filename)
        elif name is not None:
            try:
                with open(os.path.join(filepath_pkl, name), 'rb') as f:
                    data = pickle.load(f)
                for key, value in data.items():
                    setattr(self, key, value)
            except FileNotFoundError:
                logger.warning("File not found: %s", os.path.join(filepath_pkl, name))
        else:
            logger.warning("No filepath or name provided.")

    def save_outputs(self, filepath_md, name: str, responses: list):
        """Save the outputs of the class LLM responses to a markdown file.
        
        Args:
            filepath_md (str): The directory path where the markdown file will be saved.
            name (str): The name of the markdown file.
            responses (list): List of response objects, each containing 'prompts' and 'output' attributes.

        Raises:
            Exception: If saving fails due to file permission or path errors.
        """
        timestamp = get_timestamp()
        filename = f"{name}_{timestamp}.md"
        with open(os.path.join(filepath_md, filename), 'w', encoding='utf-8') as f:
            f.write(f"# {name} Prompts and Outputs\n\n")
            for response in responses:
                f.write("## Prompts\n\n")
                # Turn the prompts into a string
                prompts_str = ""
                for prompt in response.prompts:
                    prompts_str += f"{prompt['role']}: {prompt['content']}\n\n"
                f.write(prompts_str)
                f.write("## Output\n\n")
                f.write(response.output)
                f.write("\n\n")
