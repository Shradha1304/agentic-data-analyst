from analyst.tools import get_schema, describe_column, plot_histogram

# 1. What the LLM sees: names, descriptions, argument schemas
TOOL_SPECS = [
    {
        "name": "get_schema",
        "description": (
            "Returns the dataset's shape, each column's dtype, missing count and "
            "number of unique values, plus 3 sample rows. Call this first."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "describe_column",
        "description": (
            "Returns summary statistics (mean, std, min, median, max) for a numeric "
            "column, or the top 10 value counts for a categorical column."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "col": {"type": "string", "description": "Exact column name."}
            },
            "required": ["col"],
        },
    },
    {
        "name": "plot_histogram",
        "description": (
            "Saves a histogram of a numeric column as a PNG and returns the file "
            "path and a text description (range, skewness). Numeric columns only."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "col": {"type": "string", "description": "Exact name of a numeric column."},
                "bins": {"type": "integer", "description": "Number of bins (5 to 100). Optional."},
            },
            "required": ["col"],
        },
    },
]

# 2. Lookup table: tool name -> your real function
TOOL_FUNCTIONS = {
    "get_schema": get_schema,
    "describe_column": describe_column,
    "plot_histogram": plot_histogram,
}


# 3. Dispatcher: runs a tool by name, never raises
def run_tool(df, name: str, args: dict) -> dict:
    if name not in TOOL_FUNCTIONS:
        return {"error": f"Unknown tool '{name}'. Available: {list(TOOL_FUNCTIONS)}"}
    try:
        return TOOL_FUNCTIONS[name](df, **args)
    except TypeError as e:
        return {"error": f"Bad arguments for '{name}': {e}"}
    except Exception as e:
        return {"error": f"Tool '{name}' failed: {type(e).__name__}: {e}"}


# 4. Converter for OpenAI-compatible APIs (Groq, Gemini, OpenRouter, Ollama)
def to_openai_format(specs: list) -> list:
    return [
        {
            "type": "function",
            "function": {
                "name": s["name"],
                "description": s["description"],
                "parameters": s["input_schema"],
            },
        }
        for s in specs
    ]