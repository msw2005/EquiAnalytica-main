from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from google.adk.models.lite_llm import LiteLlm

from . import prompt
from ...config import *
from .tools import fetch_stock_financial_indicators
from ...callbacks import *
from ...tools import get_current_time


if MODEL in GEMINI_LIST:
    model_in_use = MODEL
else:
    model_in_use = LiteLlm(model=MODEL)


fundamental_agent = LlmAgent(
    model=model_in_use,
    name="fundamental_agent",
    description="fundamental_agent for conducting fundamental analysis using financial statements and output a structured Markdown report in Chinese.",
    instruction=prompt.FUNDAMENTAL_AGENT_PROMPT,
    output_key="fundamental_agent_output",
    tools=[
        fetch_stock_financial_indicators,
        get_current_time
    ],
    before_agent_callback=call_log,
    after_agent_callback=save_agent_output
)