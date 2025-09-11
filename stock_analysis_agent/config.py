# List of Gemini models
GEMINI_LIST = [
    "gemini-2.5-flash-preview-05-20",
    "gemini-2.5-pro-preview-06-05",
]

# List of other available models
OTHER_LIST = [
    "openai/gpt-4o-mini",
    "openai/gpt-4.1-mini",
    "openai/o4-mini",
]

# The model that agents will import via `from .config import MODEL`
MODEL = "gemini-2.5-pro-preview-06-05"

# Validate that MODEL is defined in one of the lists
assert MODEL in GEMINI_LIST + OTHER_LIST, \
    f"MODEL ('{MODEL}') must be in GEMINI_LIST or OTHER_LIST"