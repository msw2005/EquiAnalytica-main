from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from google.adk.models.lite_llm import LiteLlm


from ...callbacks import *
from . import prompt
from ...config import *
from .tools import calculate_technical_indicators
from ...tools import get_current_time


if MODEL in GEMINI_LIST:
    model_in_use = MODEL
else:
    model_in_use = LiteLlm(model=MODEL)


technical_agent = LlmAgent(
    model=model_in_use,
    name="technical_agent",
    description="technical_agent for conducting technical analysis using historical price data and indicators and output a structured Markdown report in Chinese.",
    instruction=prompt.TECHNICAL_AGENT_PROMPT,
    output_key="technical_agent_output",
    tools=[calculate_technical_indicators,
           get_current_time],
    before_agent_callback=call_log,
    after_agent_callback=save_agent_output
)