"""Optional critic agent skeleton for bonus work."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.core.schemas import AgentName, AgentResult


class CriticAgent(BaseAgent):
    """Optional fact-checking and safety-review agent."""

    name = "critic"

    def __init__(self, llm_client=None) -> None:
        self.llm_client = llm_client or LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Validate final answer and append findings.

        Add fact-check, citation coverage, or hallucination checks.
        """
        if not state.final_answer:
            return state

        system_prompt = (
            "You are a strict editorial critic and fact-checker. Your job is to verify the accuracy "
            "and citation coverage of the final research answer against the provided raw source snippets.\n"
            "Guidelines:\n"
            "1. Fact-check: Ensure all factual claims in the final answer are backed by the source snippets.\n"
            "2. Hallucination check: Identify and remove/rewrite any claims that are not supported or are exaggerated.\n"
            "3. Citation check: Make sure source citations (e.g. [1], [2]) are correctly placed and point to correct URLs.\n"
            "Output only the refined final answer. If the original is already accurate and well-cited, return it exactly as is."
        )

        sources_text = ""
        for i, src in enumerate(state.sources):
            sources_text += f"[{i+1}] Title: {src.title}\nSnippet: {src.snippet}\nURL: {src.url or 'N/A'}\n\n"

        user_prompt = (
            f"Original Final Answer:\n{state.final_answer}\n\n"
            f"Raw Sources:\n{sources_text}"
        )

        response = self.llm_client.complete(system_prompt, user_prompt)
        state.final_answer = response.content

        state.agent_results.append(
            AgentResult(
                agent=AgentName.CRITIC,
                content=response.content,
                metadata={
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                }
            )
        )
        return state

