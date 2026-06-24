"""LLM client abstraction.

Production note: agents should depend on this interface instead of importing an SDK directly.
"""

from dataclasses import dataclass
import logging
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from multi_agent_research_lab.core.config import get_settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LLMResponse:
    content: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None


class LLMClient:
    """Provider-agnostic LLM client skeleton."""

    def __init__(self, settings=None) -> None:
        self.settings = settings or get_settings()
        self.client = OpenAI(
            base_url=self.settings.kira_base_url,
            api_key=self.settings.kira_api_key,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Return a model completion.

        Connect OpenAI, Azure OpenAI, or another provider.
        Keep retry, timeout, and token logging here rather than inside agents.
        """
        logger.info(f"Calling LLM with model: {self.settings.kira_model}")
        
        response = self.client.chat.completions.create(
            model=self.settings.kira_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            timeout=self.settings.timeout_seconds,
        )
        
        content = response.choices[0].message.content or ""
        usage = response.usage
        input_tokens = usage.prompt_tokens if usage else None
        output_tokens = usage.completion_tokens if usage else None
        cost_usd = 0.0
        
        logger.info(f"LLM call successful. Tokens: input={input_tokens}, output={output_tokens}")
        
        return LLMResponse(
            content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
        )

