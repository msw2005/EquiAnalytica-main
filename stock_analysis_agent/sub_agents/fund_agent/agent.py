from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from google.adk.models.lite_llm import LiteLlm


from . import prompt
from ...config import *
from .tools import fetch_stock_individual_fund_flow, fetch_stock_chip_distribution, fetch_stock_institute_hold_detail, fetch_stock_hsgt_individual_detail, get_last_quarter
from ...tools import get_current_time
from ...callbacks import *



if MODEL in GEMINI_LIST:
    model_in_use = MODEL
else:
    model_in_use = LiteLlm(model=MODEL)



fund_agent = LlmAgent(
    model=model_in_use,
    name="fund_agent",
    description="fund_agent for conducting fund flow analysis using fund flow data and output a structured Markdown report in Chinese.",
    instruction=prompt.FUND_AGENT_PROMPT,
    output_key="fund_agent_output",
    tools=[
        get_last_quarter,
        fetch_stock_individual_fund_flow,
        fetch_stock_chip_distribution,
        fetch_stock_institute_hold_detail,
        fetch_stock_hsgt_individual_detail,
        get_current_time
    ],
    before_agent_callback=call_log,
    after_agent_callback=save_agent_output
)