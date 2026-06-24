"""Command-line entrypoint for the lab starter."""

from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.observability.logging import configure_logging

app = typer.Typer(help="Multi-Agent Research Lab starter CLI")
console = Console()


def _init() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)


@app.command()
def baseline(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run a minimal single-agent baseline placeholder."""
    import time
    from multi_agent_research_lab.services.llm_client import LLMClient
    from multi_agent_research_lab.core.schemas import AgentName, AgentResult

    _init()
    request = ResearchQuery(query=query)
    state = ResearchState(request=request)
    
    llm_client = LLMClient()
    system_prompt = (
        "You are an expert research assistant. "
        "Your task is to analyze the user's query, perform research (based on your internal knowledge), "
        "and draft a comprehensive summary."
    )
    
    start_time = time.time()
    try:
        response = llm_client.complete(system_prompt=system_prompt, user_prompt=request.query)
        latency = time.time() - start_time
        
        state.final_answer = response.content
        
        state.agent_results.append(
            AgentResult(
                agent=AgentName.WRITER,
                content=response.content,
                metadata={
                    "latency_seconds": latency,
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                    "cost_usd": response.cost_usd,
                }
            )
        )
        state.add_trace_event(
            name="baseline_completed",
            payload={
                "latency_seconds": latency,
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
                "cost_usd": response.cost_usd,
            }
        )
        
        console.print(Panel.fit(state.final_answer, title="Single-Agent Baseline"))
        console.print(f"[bold green]Latency:[/bold green] {latency:.2f} seconds")
        console.print(f"[bold green]Tokens:[/bold green] Input: {response.input_tokens}, Output: {response.output_tokens}")
    except Exception as e:
        console.print(Panel.fit(f"[bold red]Error during baseline execution:[/bold red] {str(e)}", title="Error"))
        raise typer.Exit(code=1)


@app.command("multi-agent")
def multi_agent(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run the multi-agent workflow skeleton."""

    _init()
    state = ResearchState(request=ResearchQuery(query=query))
    workflow = MultiAgentWorkflow()
    try:
        result = workflow.run(state)
    except StudentTodoError as exc:
        console.print(Panel.fit(str(exc), title="Expected TODO", style="yellow"))
        raise typer.Exit(code=2) from exc
    console.print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    app()
