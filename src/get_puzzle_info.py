import re
import json
import requests


def extract_puzzle_data_from_url(url):
    # Fetch the HTML content from the webpage
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(
            f"Failed to retrieve webpage content. Status code: {response.status_code}")

    html_content = response.text

    # Extract the JSON data from the script tag
    json_data_match = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', html_content)
    if not json_data_match:
        raise ValueError("Could not find JSON data in the HTML content")

    json_data = json.loads(json_data_match.group(1))

    # Extract the number from the query key
    number = int(json_data['props']['pageProps']['id'])

    # Extract the puzzle words and group them
    puzzle_str = ""
    solution_lst = []

    for answer in json_data['props']['pageProps']['answers']:
        words = "\n".join(answer['words'])
        puzzle_str += words + "\n"
        solution_lst.append(f'\n{words}\n')

    puzzle_str = puzzle_str.strip()  # Remove the last newline

    return puzzle_str, number, solution_lst
