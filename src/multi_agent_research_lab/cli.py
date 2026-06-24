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


@app.command()
def benchmark(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run benchmark comparing baseline vs multi-agent."""
    import os
    import time
    from multi_agent_research_lab.evaluation.benchmark import run_benchmark
    from multi_agent_research_lab.evaluation.report import render_markdown_report
    from multi_agent_research_lab.services.llm_client import LLMClient
    from multi_agent_research_lab.core.schemas import AgentName, AgentResult

    _init()
    console.print("[bold blue]Starting Benchmark...[/bold blue]")

    # 1. Định nghĩa runner cho baseline
    def baseline_runner(q: str) -> ResearchState:
        request = ResearchQuery(query=q)
        state = ResearchState(request=request)
        llm_client = LLMClient()
        system_prompt = (
            "You are an expert research assistant. "
            "Your task is to analyze the user's query, perform research (based on your internal knowledge), "
            "and draft a comprehensive summary."
        )
        start_time = time.time()
        response = llm_client.complete(system_prompt=system_prompt, user_prompt=q)
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
        return state

    # 2. Định nghĩa runner cho multi-agent
    def multi_agent_runner(q: str) -> ResearchState:
        state = ResearchState(request=ResearchQuery(query=q))
        workflow = MultiAgentWorkflow()
        return workflow.run(state)

    # 3. Chạy benchmark
    console.print("Running baseline (single-agent) runner...")
    state_base, metrics_base = run_benchmark("Baseline (Single-Agent)", query, baseline_runner)

    console.print("Running multi-agent (LangGraph) runner...")
    state_multi, metrics_multi = run_benchmark("Multi-Agent (LangGraph)", query, multi_agent_runner)

    # 4. Tạo báo cáo
    metrics_list = [metrics_base, metrics_multi]
    report_md = render_markdown_report(metrics_list)

    # Ghi báo cáo vào reports/benchmark_report.md
    os.makedirs("reports", exist_ok=True)
    report_path = "reports/benchmark_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_md)

    console.print(f"[bold green]Benchmark completed successfully![/bold green]")
    console.print(f"Report saved to [bold cyan]{report_path}[/bold cyan]")
    console.print(Panel.fit(report_md, title="Benchmark Report Summary"))


if __name__ == "__main__":
    app()
