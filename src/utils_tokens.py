"""
Utility functions for measuring tokens and modifying strings to fit within token limits.

"""
import logging
import tiktoken
import time
from langchain.text_splitter import (
    TokenTextSplitter
)

# Set up logger
logger = logging.getLogger('method-actors')


def num_tokens(str, encoding_name="cl100k_base") -> int:
    """Returns the number of tokens in a text string using the CL100k_base tokenizer."""
    encoding = tiktoken.get_encoding(encoding_name)
    tokens = len(encoding.encode(str))
    return tokens


def time_tokens(str, model='gpt-4'):
    """Returns the time needed to wait before the next request to the LLM."""
    tps = 3000000 / 60  # tokens per minute under my account
    tokens = num_tokens(str)
    return tokens / tps


def sleep_for_time_tokens(str, model='gpt-4'):
    """Sleeps for the time needed to wait before the next request to the LLM."""
    time_to_sleep = time_tokens(str, model)
    logger.debug("Sleeping for %s seconds...", time_to_sleep)
    time.sleep(time_to_sleep)


def sleep_for_tokens(tokens, model='gpt-4'):
    """Sleeps for the time needed to wait before the next request to the LLM.
    Difference between this and sleep_for_time_tokens is that tokens are provided in argument
    rather than text strings that the function converts to tokens.
    """
    tps = 300000 / 60  # tokens per minute under my account
    time_to_sleep = tokens / tps
    logger.debug("Sleeping for %s seconds...", time_to_sleep)
    time.sleep(time_to_sleep)


def trim_to_last_blank_line(string):
    """Trims string back to the last blank line."""
    lines = string.splitlines()
    for i in range(len(lines)-1, -1, -1):
        if not lines[i].strip():
            return '\n'.join(lines[:i+1])
    return ''


def trim_for_tokens(string, max_tokens=6000, max_attempts=3000):
    """Trims string to max_tokens."""
    tokens = num_tokens(string)
    count = 1
    while tokens > max_tokens and count < max_attempts:
        logger.debug(
            "trim_for_tokens: String is too long. Trimming to last blank line. (Attempt %s).",
            count
        )
        if string == trim_to_last_blank_line(string):
            logger.debug(
                "trim_for_tokens: String is too long. Trimming to last sentence. (Attempt %s).",
                count
            )
            string = string[:string.rfind(".")+1]
            tokens = num_tokens(string)
            count += 1
            continue
        string = trim_to_last_blank_line(string)
        tokens = num_tokens(string)
        count += 1
    return string


def trim_part_for_tokens(part, remainder, max_tokens=6000, trim_tokens=3000, max_attempts=3000):
    """Trims part so that part + remainder is under token limit."""
    if num_tokens(remainder) > max_tokens:
        logger.debug(
            "trim_query_for_tokens: Other parts exceed %s tokens. Reducing to %s tokens.",
            max_tokens,
            trim_tokens
        )
        part = trim_for_tokens(part, trim_tokens)
        return part
    tokens = num_tokens(part + remainder)
    count = 1
    while tokens > max_tokens and count < max_attempts:
        logger.debug(
            "trim_part_for_tokens: Part is too long. Trimming to last blank line. (Attempt %d).",
            count
        )
        if part == trim_to_last_blank_line(part):
            logger.debug(
                "trim_part_for_tokens: Part is too long. Trimming to last sentence. (Attempt %d).",
                count
            )
            part = part[:part.rfind(".")+1]
            tokens = num_tokens(part + remainder)
            count += 1
            continue
        part = trim_to_last_blank_line(part)
        tokens = num_tokens(part + remainder)
        count += 1
    return part


def string_to_token_list(string, chunk_size=6000, chunk_overlap=0):
    """Turns string into list of token-sized strings."""
    text_splitter = TokenTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return text_splitter.split_text(string)


def list_to_token_list(lst, chunk_size=6000, chunk_overlap=0):
    """Combines strings in a list so that each string in the list approaches token limit.
    This increases efficiency when you want an LLM to process all the items in a list
    but you don't need to process each item individually with its own LLM call.
    """
    temp_list = lst
    token_list = []
    total_tokens = 0
    scratchpad = ""
    index = 0
    while index < len(temp_list):
        x = temp_list[index]
        try:
            tokens = num_tokens(x)
        except Exception as e:
            logging.error(
                "Error calculating tokens for item at index %s: %s", index, e)
            index += 1
            continue
        # If item exceeds token limit, split item into its own token_list,
        # insert that list, end the current iteration, and continue to the next iteration.
        if tokens >= chunk_size:
            try:
                x_list = string_to_token_list(
                    x,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap
                )
            except Exception as e:
                logging.error(
                    "Error splitting string into token list for item at index %d: %s",
                    index,
                    e
                )
                index += 1
                continue
            temp_list.pop(index)
            # insert x_list items at current position
            temp_list[index:index] = x_list
            continue
        # If item plus scratchpad exceeds token limit, add scratchpad to list,
        # clear scratchpad, and clear total tokens.
        if total_tokens + tokens >= chunk_size:
            token_list.append(scratchpad)
            scratchpad = ""
            total_tokens = 0
        # Add item to scratchpad, add tokens to token count
        scratchpad += "\n " + x
        total_tokens += tokens
        index += 1
    if scratchpad:  # handle any remaining content in scratchpad
        token_list.append(scratchpad)
    return token_list
