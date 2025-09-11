from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from google.adk.tools.agent_tool import AgentTool
from google.adk.models.lite_llm import LiteLlm

from dotenv import load_dotenv
import os

from ...callbacks import *
from . import prompt
from ...config import *
from ...tools import get_current_time
from .tools import google_search_agent_for_policy


if MODEL in GEMINI_LIST:
    model_in_use = MODEL
else:
    model_in_use = LiteLlm(model=MODEL)




# Load environment variables from .env file
load_dotenv(dotenv_path="stock_analysis_agent/.env")

# Get the API key
smithery_api_key = os.getenv("SMITHERY_API_KEY")


policy_agent = LlmAgent(
    model=model_in_use,
    name="policy_agent",
    description="policy_agent for conducting policy and regulatory analysis using government announcements, regulatory policies, industry guidelines, and legislative data and output a structured Markdown report in Chinese.",
    instruction=prompt.POLICY_AGENT_PROMPT,
    output_key="policy_agent_output",
    tools=[
        # MCPToolset(
        #     connection_params=StdioServerParameters(
        #         command='npx',
        #         args=[
        #             "-y",
        #             "@smithery/cli@latest",
        #             "run",
        #             "@smithery-ai/server-sequential-thinking",
        #             "--key",
        #             f"{smithery_api_key}"
        #         ]
        #     )
        # ),
        AgentTool(agent=google_search_agent_for_policy),
        get_current_time
    ],
    before_agent_callback=call_log,
    after_agent_callback=save_agent_output
)
