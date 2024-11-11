# Official Repo of LLMs as Method Actors

Official implementation for paper [LLMs as Method Actors: A Model for Prompt Engineering and Architecture](https://arxiv.org/abs/2411.05778) with code, prompts, and sample outputs.

## Setup

1. Setup your API key

Store your OpenAI API key in environment variable ``OPENAI_API_KEY``. (To learn more about setting up an OpenAI API key, follow [this link](https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety)). If you would like to use Anthropic or Gemini models, store those keys in environmental variables ``ANTHROPIC_API_KEY`` and ``GEMINI_API_KEY``.

2. Install the necessary packages

```bash
pip install -r requirements.txt
```

This will install all dependencies listed in `requirements.txt`.

## Tutorials

The Jupyter notebook tutorial.ipynb can walk you through how to run each of the approaches from the paper on any Connections puzzle.

## Sample Outputs

Sample outputs for each of the approaches are available in the “sample_outputs” folder as markdown files. For the more complicated approaches, markdown files are included that track the intermediary progress for each guess that was considered. Markdown files named “summary” and “summary_detailed” summarize the overall outcome and the results of the intermediary steps.

The sample outputs were created by running the python scripts on the Connections puzzle from the day that the paper was announced on arXiv.org, November 11, 2024.

The results were as follows:

| Approach                    | Success? | # Correct Guesses | # Incorrect Guesses |
| --------------------------- | -------- | ----------------- | ------------------- |
| Vanilla                     | No       | 0                 | 4                   |
| Chain-of-Thought            | No       | 1                 | 4                   |
| Chain-of-Thought (Scripted) | Yes      | 4                 | 3                   |
| Actor                       | Yes      | 4                 | 0                   |
| Actor-2                     | Yes      | 4                 | 1                   |
| Oneshot-o1                  | No       | 2                 | 2                   |
| Vanilla-o1                  | Yes      | 4                 | 0                   |
| Actor-o1                    | Yes      | 4                 | 0                   |

## Citations

Please cite the paper and star this repo if you find it interesting or useful. Feel free to contact colin.doyle@lls.edu if you have any questions.

```bibtex
@misc{doyle2024method,
      title={LLMs as Method Actors: A Model for Prompt Engineering and Architecture}, 
      author={Colin Doyle},
      year={2024},
      eprint={2411.05778},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```

