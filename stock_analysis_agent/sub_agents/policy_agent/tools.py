from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from google.adk.models.lite_llm import LiteLlm

from ...config import *

if MODEL in GEMINI_LIST:
    model_in_use = MODEL
else:
    model_in_use = LiteLlm(model=MODEL)

google_search_agent_for_policy = LlmAgent(
    model=model_in_use,
    name='google_search_agent_for_policy',
    instruction="""
    You're a spealist in Google Search who take a search query and return the results.
    """,
    tools=[google_search]
)