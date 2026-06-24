"""Writer agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.core.schemas import AgentName, AgentResult


class WriterAgent(BaseAgent):
    """Produces final answer from research and analysis notes."""

    name = "writer"

    def __init__(self, llm_client=None) -> None:
        self.llm_client = llm_client or LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.final_answer`.

        Synthesize a clear response with citations or source references.
        """
        system_prompt = (
            "You are a professional technical writer. Synthesize a comprehensive final report.\n"
            f"Audience: {state.request.audience}\n"
            "Combine the information from both the Research Notes and the Analysis Notes.\n"
            "Requirements:\n"
            "- Flow logically with clear markdown headings, bullet points, and bold text.\n"
            "- Maintain factual accuracy.\n"
            "- Cite sources using indices (e.g. [1], [2]) based on the citations in Research Notes.\n"
            "- Provide a References section at the bottom listing the sources."
        )

        sources_text = ""
        for i, src in enumerate(state.sources):
            sources_text += f"[{i+1}] {src.title} - {src.url or 'N/A'}\n"

        user_prompt = (
            f"Query: {state.request.query}\n\n"
            f"Research Notes:\n{state.research_notes or 'None'}\n\n"
            f"Analysis Notes:\n{state.analysis_notes or 'None'}\n\n"
            f"Sources:\n{sources_text}"
        )

        response = self.llm_client.complete(system_prompt, user_prompt)
        state.final_answer = response.content

        state.agent_results.append(
            AgentResult(
                agent=AgentName.WRITER,
                content=response.content,
                metadata={
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                }
            )
        )
        return state

