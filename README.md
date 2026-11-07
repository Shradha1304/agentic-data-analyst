# Agentic Data Analyst

An LLM-powered agent that explores a dataset on its own: it inspects the data, decides what to investigate, calls analysis tools, and writes a report where every number traces back to a tool result.

> **Status:** early development. Tools and tests are in place; the agent loop is next.

## Why this project

Most "chat with your data" demos let the LLM do the math, which makes results hard to trust. This project takes a different approach:

- The **LLM decides what to look at**; **Python code computes everything**.
- Every claim in the report should be **verifiable against logged tool outputs**.
- The focus is on **evaluation and trustworthiness**, not just calling an API.

## How it works (planned)

```
CSV -> profile (pandas) -> LLM chooses tools -> tools run and return results -> LLM writes report
```

The agent loops: it picks a tool, reads the result, and decides the next step, until it has enough to write a report or hits a step limit.

## Current features

- `get_schema`: shape, column types, missing counts, sample rows
- `describe_column`: summary stats for numeric columns, top values for categorical ones
- `plot_histogram`: saves a histogram and returns the path plus a text description
- Helpful error messages (e.g. listing valid column names) so the agent can self-correct
- Unit tests checked against known Titanic results

## Roadmap

- [x] Core tools with tests
- [ ] Tool specs for the LLM API
- [ ] Agent loop with step limit and call deduplication
- [ ] Report generation with cited tool results
- [ ] Run logging (JSON per run)
- [ ] Streamlit front end
- [ ] Grounding check: verify numbers in the report against tool outputs
- [ ] Evaluation on clean and messy datasets
- [ ] Optional: model training step, sandboxed code execution

## Project structure

```
agentic_data_analyst/
├── analyst/          # core package (tools, agent, reporting)
├── data/             # input datasets
├── tests/            # unit tests
├── outputs/          # generated charts, reports, run logs (gitignored)
└── requirements.txt
```

## Setup

```bash
git clone https://github.com/YOUR-USERNAME/agentic-data-analyst.git
cd agentic-data-analyst

python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# Mac/Linux
# source .venv/bin/activate

pip install -r requirements.txt
```

Add your API key to a `.env` file (never commit this):

```
LLM_KEY=your-key-here
```

## Running tests

```bash
python -m pytest
```

## Data

The tests use the Titanic dataset (`data/titanic.csv`, 891 rows, 12 columns), from Kaggle.

## License

MIT (or your choice)
