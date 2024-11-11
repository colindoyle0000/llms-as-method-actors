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

Sample outputs for each of the approaches are available in the “sample_outputs” folder.

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

