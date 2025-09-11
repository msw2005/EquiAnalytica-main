from google.adk.agents import LlmAgent, ParallelAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.models.lite_llm import LiteLlm

from . import prompt
from .config import MODEL, GEMINI_LIST

from .sub_agents.fundamental_agent.agent import fundamental_agent
from .sub_agents.technical_agent.agent import technical_agent
from .sub_agents.fund_agent.agent import fund_agent
from .sub_agents.policy_agent.agent import policy_agent

from .tools import *


if MODEL in GEMINI_LIST:
    model_in_use = MODEL
else:
    model_in_use = LiteLlm(model=MODEL)


analysis_agent = ParallelAgent(
    name="equity_research_pipeline",
    description=(
        "Agent to analyse a stock from fundamental, technical, fund flow, and political perspectives and report findings into a structured detailed Markdown report in Chinese."
    ),
    sub_agents=[
        fundamental_agent,
        technical_agent,
        fund_agent,
        policy_agent
        ]
)


root_agent = LlmAgent(
    name="coordinator_agent",
    model=model_in_use,
    description=(
        "Agent to coordinate input taking, analyses conducting, and report consolidation."
    ),
    instruction=prompt.COORDINATOR_AGENT_PROMPT,
    tools=[get_current_time,
           AgentTool(agent=google_search_agent),
           AgentTool(agent=analysis_agent),
           combine_reports],
    output_key="root_agent_output"
)








