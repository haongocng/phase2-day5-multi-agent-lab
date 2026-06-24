"""Analyst agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.core.schemas import AgentName, AgentResult


class AnalystAgent(BaseAgent):
    """Turns research notes into structured insights."""

    name = "analyst"

    def __init__(self, llm_client=None) -> None:
        self.llm_client = llm_client or LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.analysis_notes`.

        Extract key claims, compare viewpoints, and flag weak evidence.
        """
        if not state.research_notes:
            state.analysis_notes = "No research notes available to analyze."
            return state

        system_prompt = (
            "You are an expert tech analyst. Your task is to analyze the provided research notes.\n"
            "Identify the key claims, verify if they are logically supported, find any gaps or "
            "contradictions in the research, and highlight any weak arguments. "
            "Organize your thoughts into structured analytical notes."
        )
        user_prompt = f"Query: {state.request.query}\n\nResearch Notes:\n{state.research_notes}"

        response = self.llm_client.complete(system_prompt, user_prompt)
        state.analysis_notes = response.content

        state.agent_results.append(
            AgentResult(
                agent=AgentName.ANALYST,
                content=response.content,
                metadata={
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                }
            )
        )
        return state

