"""Researcher agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.services.search_client import SearchClient
from multi_agent_research_lab.core.schemas import AgentName, AgentResult


class ResearcherAgent(BaseAgent):
    """Collects sources and creates concise research notes."""

    name = "researcher"

    def __init__(self, llm_client=None, search_client=None) -> None:
        self.llm_client = llm_client or LLMClient()
        self.search_client = search_client or SearchClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.sources` and `state.research_notes`.

        Implement search, source filtering, citation capture, and notes.
        """
        query = state.request.query
        max_sources = state.request.max_sources

        # 1. Thực hiện tìm kiếm
        sources = self.search_client.search(query, max_results=max_sources)
        state.sources = sources

        if not sources:
            state.research_notes = "No relevant search results found for the query."
            return state

        # 2. Xây dựng prompt để LLM tổng hợp ghi chú nghiên cứu
        sources_text = ""
        for i, src in enumerate(sources):
            sources_text += f"[{i+1}] Title: {src.title}\nURL: {src.url or 'N/A'}\nSnippet: {src.snippet}\n\n"

        system_prompt = (
            "You are a professional researcher. Your task is to analyze the provided search results "
            "and synthesize concise research notes to answer the user's query.\n"
            "Format requirements:\n"
            "- Highlight key facts, dates, and statistics.\n"
            "- Cite the source index (e.g. [1], [2]) for every key claim.\n"
            "- Keep it professional and facts-driven."
        )
        user_prompt = f"Query: {query}\n\nSearch Results:\n{sources_text}"

        response = self.llm_client.complete(system_prompt, user_prompt)
        state.research_notes = response.content

        # 3. Ghi nhận agent result
        state.agent_results.append(
            AgentResult(
                agent=AgentName.RESEARCHER,
                content=response.content,
                metadata={
                    "sources_count": len(sources),
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                }
            )
        )
        return state

