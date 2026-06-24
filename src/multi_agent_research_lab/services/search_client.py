"""Search client abstraction for ResearcherAgent."""

import logging
import requests
from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.schemas import SourceDocument

logger = logging.getLogger(__name__)


class SearchClient:
    """Provider-agnostic search client skeleton."""

    def __init__(self, settings=None) -> None:
        self.settings = settings or get_settings()

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        """Search for documents relevant to a query.

        Implement with Tavily, Bing, SerpAPI, internal docs, or a local mock.
        """
        api_key = self.settings.tavily_api_key
        if not api_key:
            logger.warning("TAVILY_API_KEY is not set. Returning empty search results.")
            return []

        logger.info(f"Searching Tavily for query: '{query}' (max_results={max_results})")
        try:
            response = requests.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": api_key,
                    "query": query,
                    "max_results": max_results,
                },
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])

            docs = []
            for r in results:
                docs.append(
                    SourceDocument(
                        title=r.get("title", "Untitled"),
                        url=r.get("url"),
                        snippet=r.get("content", ""),
                    )
                )
            logger.info(f"Successfully retrieved {len(docs)} search results from Tavily.")
            return docs
        except Exception as e:
            logger.error(f"Error during Tavily search: {str(e)}")
            return []

