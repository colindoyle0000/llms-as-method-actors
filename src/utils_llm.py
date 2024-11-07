"""
Utility functions for working with LLMs.


"""

import logging
import os

from dataclasses import dataclass
from dotenv import load_dotenv
from openai import OpenAI
import google.generativeai as genai
import anthropic

from src.utils_file import get_root_dir
from src.utils_tokens import sleep_for_tokens
from src.utils_string import get_timestamp


# Set up logger
logger = logging.getLogger('connections')


@dataclass
class LLMSettings:
    """Settings for the LLM."""
    # Embeddings
    embeddings = 'OpenAIEmbeddings()'
    # Primary LLM model
    model: str = 'gpt-4o'
    # Maximum tokens for input to primary LLM
    max_tokens: int = 40000
    # LLM model for long inputs
    model_long: str = 'gpt-4o'
    # Maximum tokens for input to long LLM
    max_tokens_long: int = 40000
    # LLM model for doing simpler tasks for less money
    model_cheap: str = 'gpt-4o-mini'
    # Maximum tokens for input to cheap LLM
    max_tokens_cheap: int = 40000
    # Chunk size for breaking up long inputs for primary LLM
    chunk_size: int = 40000
    # Overlapping text between chunks
    chunk_overlap: int = 500
    # Chunk size for breaking up long inputs for long LLM
    chunk_size_long: int = 40000
    # Maximum number of attempts at reducing a long input to a short input by breaking it up
    # into chunks, summarizing those chunks, and then combining the summaries.
    max_attempts: int = 3
    # Temperature for LLM completions
    temperature = 0
    # Response format for LLM completions
    response_format = None


class Response:
    """Response class for LLM completions."""

    def __init__(self,
                 output=None,
                 completion_tokens=None,
                 prompt_tokens=None,
                 total_tokens=None,
                 model=None,
                 timestamp=None,
                 full_response=None,
                 prompts=None,
                 settings=None
                 ):
        self.output = output
        self.completion_tokens = completion_tokens
        self.prompt_tokens = prompt_tokens
        self.total_tokens = total_tokens
        self.model = model
        self.timestamp = timestamp
        self.full_response = full_response
        self.prompts = prompts
        self.settings = settings


def set_openai_key():
    """Set variable for OpenAI API key based on your environmental variables."""
    load_dotenv()
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    return openai_api_key


def set_gemini_key():
    """Set variable for GenAI API key based on your environmental variables."""
    load_dotenv()
    gemini_api_key = os.environ.get('GEMINI_API_KEY')
    return gemini_api_key


def set_anthropic_key():
    """Set variable for Anthropic API key based on your environmental variables."""
    load_dotenv()
    anthropic_api_key = os.environ.get('ANTHROPIC_API_KEY')
    return anthropic_api_key


def get_openai_models():
    """Get a list of OpenAI models available to the user."""
    try:
        client = OpenAI(api_key=set_openai_key())
        available_models = client.models.list()
        models_lst = []
        for model in available_models.data:
            models_lst.append(model.id)
        logger.info("Available OpenAI models: %s", models_lst)
    except Exception as e:
        print(f"Error: {e}")
        print("Unable to retrieve model information.")
    return models_lst


def get_gemini_models():
    """Get a list of GenAI models available to the user."""
    try:
        genai.configure(api_key=set_gemini_key())
        available_models = genai.list_models()
        models_lst = []
        for model in available_models:
            if 'generateContent' in model.supported_generation_methods:
                models_lst.append(model.name)
        logger.info("Available Gemini models: %s", models_lst)
    except Exception as e:
        print(f"Error: {e}")
        print("Unable to retrieve model information.")
    return models_lst


def llm_call(model='gpt-4o', prompts=[], settings=None):
    """Call the LLM with a list of prompts."""
    openai_models = ['whisper-1',
                     'dall-e-2',
                     'gpt-3.5-turbo-16k',
                     'tts-1-hd-1106',
                     'tts-1-hd',
                     'gpt-4-turbo-2024-04-09',
                     'gpt-4-0125-preview',
                     'gpt-4-turbo-preview',
                     'gpt-4-turbo',
                     'gpt-3.5-turbo-instruct-0914',
                     'gpt-3.5-turbo',
                     'gpt-3.5-turbo-instruct',
                     'text-embedding-3-small',
                     'tts-1',
                     'text-embedding-3-large',
                     'gpt-4-1106-preview',
                     'babbage-002',
                     'gpt-3.5-turbo-0125',
                     'tts-1-1106',
                     'dall-e-3',
                     'gpt-4-0613',
                     'text-embedding-ada-002',
                     'gpt-4',
                     'davinci-002',
                     'gpt-3.5-turbo-1106',
                     'gpt-4o-2024-05-13',
                     'gpt-4o',
                     'gpt-4o-mini',
                     'gpt-4o-2024-08-06',
                     'o1-preview',
                     'o1-preview-2024-09-12',
                     'o1-mini',
                     'o1-mini-2024-09-12',]

    gemini_models = ['gemini-1.0-pro',
                     'gemini-1.0-pro-001',
                     'gemini-1.0-pro-latest',
                     'gemini-1.0-pro-vision-latest',
                     'gemini-1.5-flash',
                     'gemini-1.5-flash-001',
                     'gemini-1.5-flash-latest',
                     'gemini-1.5-pro',
                     'gemini-1.5-pro-001',
                     'gemini-1.5-pro-latest',
                     'gemini-pro',
                     'gemini-pro-vision']
    anthropic_models = ['claude-3-5-sonnet-20240620',
                        'claude-3-opus-20240229',
                        'claude-3-sonnet-20240229',
                        'claude-3-haiku-20240307']
    if model in openai_models:
        llm_response = openai_chat_call(model, prompts, settings)
        sleep_for_tokens(llm_response.total_tokens)
    elif model in gemini_models:
        llm_response = gemini_chat_call(model, prompts, settings)
        sleep_for_tokens(llm_response.total_tokens*30)
    elif model in anthropic_models:
        llm_response = anthropic_chat_call(model, prompts, settings)
    else:
        # If model is not recognized, default to GPT-4o
        logger.warning("Model not recognized. Defaulting to GPT-4o.")
        llm_response = openai_chat_call('gpt-4o', prompts, settings)
    return llm_response


def openai_chat_call(model, prompts, settings=None):
    """Call an OpenAI model with a list of prompts."""
    # If settings are provided, use them. Otherwise, use defaults.
    logger.debug("Calling OpenAI model %s", model)
    if settings is not None:
        temperature = settings.temperature
    if model == 'o1-preview':
        temperature = 1
    else:
        temperature = 0
    client = OpenAI(api_key=set_openai_key())
    full_response = client.chat.completions.create(
        model=model,
        messages=prompts,
        temperature=temperature
    )
    llm_response = Response(
        output=full_response.choices[0].message.content,
        completion_tokens=full_response.usage.completion_tokens,
        prompt_tokens=full_response.usage.prompt_tokens,
        total_tokens=full_response.usage.total_tokens,
        model=full_response.model,
        timestamp=full_response.created,
        full_response=full_response,
        prompts=prompts,
        settings=settings
    )

    return llm_response


def gemini_chat_call(model, prompts, settings=None):
    """Call a Gemini model with a list of prompts."""
    # If settings are provided, use them. Otherwise, use defaults.
    logger.debug("Calling Gemini model %s", model)
    if settings is not None:
        temperature = settings.temperature
    else:
        temperature = 0
    # Retrieve the system and user prompts from the list of prompts
    prompt_system_text = next(
        (prompt['content'] for prompt in prompts if prompt['role'] == 'system'), None)
    prompt_user_text = next(
        (prompt['content'] for prompt in prompts if prompt['role'] == 'user'), None)
    if prompt_system_text is None:
        logger.error("System prompt not found.")
    if prompt_user_text is None:
        logger.error("User prompt not found.")

    model_name = f"models/{model}"
    # Call the Gemini model
    genai.configure(api_key=set_gemini_key())
    client = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=prompt_system_text,
        generation_config={"temperature": temperature}
    )

    full_response = client.generate_content(
        prompt_user_text)
    timestamp = get_timestamp()
    llm_response = Response(
        output=full_response.text,
        completion_tokens=full_response.usage_metadata.candidates_token_count,
        prompt_tokens=full_response.usage_metadata.prompt_token_count,
        total_tokens=full_response.usage_metadata.total_token_count,
        model=model,
        timestamp=timestamp,
        full_response=full_response,
        prompts=prompts,
        settings=settings
    )

    return llm_response


def anthropic_chat_call(model, prompts, settings=None):
    """Call an Anthropic model with a list of prompts."""
    # If settings are provided, use them. Otherwise, use defaults.
    logger.debug("Calling Anthropic model %s", model)
    if settings is not None:
        temperature = settings.temperature
    else:
        temperature = 0

    # Retrieve the system and user prompts from the list of prompts
    prompt_system_text = next(
        (prompt['content'] for prompt in prompts if prompt['role'] == 'system'), None)
    prompt_user_text = next(
        (prompt['content'] for prompt in prompts if prompt['role'] == 'user'), None)
    if prompt_system_text is None:
        logger.error("System prompt not found.")
    if prompt_user_text is None:
        logger.error("User prompt not found.")

    client = anthropic.Anthropic()

    if model == 'claude-3-5-sonnet-20240620':
        full_response = client.messages.create(
            model=model,
            max_tokens=8192,
            extra_headers={
                "anthropic-beta": "max-tokens-3-5-sonnet-2024-07-15"},
            temperature=temperature,
            system=prompt_system_text,
            messages=[
                {"role": "user", "content": prompt_user_text},
            ]
        )
    else:
        full_response = client.messages.create(
            model=model,
            max_tokens=4096,
            temperature=temperature,
            system=prompt_system_text,
            messages=[
                {"role": "user", "content": prompt_user_text},
            ]
        )
    timestamp = get_timestamp()

    llm_response = Response(
        output=full_response.content[0].text,
        completion_tokens=full_response.usage.output_tokens,
        prompt_tokens=full_response.usage.input_tokens,
        total_tokens=(full_response.usage.output_tokens +
                      full_response.usage.input_tokens),
        model=full_response.model,
        timestamp=timestamp,
        full_response=full_response,
        prompts=prompts,
        settings=settings
    )

    return llm_response
