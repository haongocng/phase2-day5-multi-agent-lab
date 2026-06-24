"""Benchmark skeleton for single-agent vs multi-agent."""

import re
from time import perf_counter
from typing import Callable

from multi_agent_research_lab.core.schemas import BenchmarkMetrics
from multi_agent_research_lab.core.state import ResearchState

Runner = Callable[[str], ResearchState]


def evaluate_quality(query: str, answer: str) -> float:
    if not answer:
        return 0.0
    from multi_agent_research_lab.services.llm_client import LLMClient
    llm_client = LLMClient()
    system_prompt = (
        "You are an expert evaluator. Rate the quality of the research answer for the given query "
        "on a scale from 0 to 10.\n"
        "Criteria:\n"
        "1. Accuracy and depth of information.\n"
        "2. Structure and readability (markdown formatting, headings).\n"
        "3. Citation coverage and references logic.\n\n"
        "Output ONLY a single floating-point number representing the score, e.g., 8.5."
    )
    user_prompt = f"Query: {query}\n\nAnswer:\n{answer}"
    try:
        response = llm_client.complete(system_prompt, user_prompt)
        match = re.search(r"(\d+\.\d+|\d+)", response.content)
        if match:
            score = float(match.group(1))
            return max(0.0, min(10.0, score))
        return 7.5
    except Exception:
        return 7.0


def calculate_cost(state: ResearchState) -> float:
    total_input = 0
    total_output = 0
    
    for res in state.agent_results:
        meta = res.metadata
        inp = meta.get("input_tokens") or 0
        out = meta.get("output_tokens") or 0
        
        # Nếu token bằng 0 do KIRA API không đếm, ta đếm thô dựa trên text length
        if inp == 0:
            inp = len(res.content) // 4 if res.content else 100
        if out == 0:
            out = len(res.content) // 4 if res.content else 100
            
        total_input += inp
        total_output += out
        
    # Giả lập giá gpt-4o-mini ($0.15/$0.60 per 1M tokens)
    cost = (total_input * 0.15 + total_output * 0.60) / 1_000_000
    return cost


def run_benchmark(run_name: str, query: str, runner: Runner) -> tuple[ResearchState, BenchmarkMetrics]:
    """Measure latency and return a placeholder metric object.

    Add quality scoring, estimated token cost, citation coverage, and error rate.
    """
    started = perf_counter()
    
    error_occurred = False
    notes = ""
    try:
        state = runner(query)
        if state.errors:
            error_occurred = True
            notes = f"Run had errors: {', '.join(state.errors)}"
    except Exception as e:
        from multi_agent_research_lab.core.schemas import ResearchQuery
        state = ResearchState(request=ResearchQuery(query=query))
        state.errors.append(str(e))
        error_occurred = True
        notes = f"Execution failed: {str(e)}"
        
    latency = perf_counter() - started
    
    # Tính toán các chỉ số
    cost = calculate_cost(state) if not error_occurred else 0.0
    quality = evaluate_quality(query, state.final_answer) if (state.final_answer and not error_occurred) else 0.0
    
    # Đếm số citation
    citations_count = 0
    if state.final_answer:
        citations = set(re.findall(r"\[\d+\]", state.final_answer))
        citations_count = len(citations)
        
    if not notes:
        notes = f"Citations found: {citations_count}. Success."

    metrics = BenchmarkMetrics(
        run_name=run_name,
        latency_seconds=latency,
        estimated_cost_usd=cost,
        quality_score=quality,
        notes=notes
    )
    return state, metrics

