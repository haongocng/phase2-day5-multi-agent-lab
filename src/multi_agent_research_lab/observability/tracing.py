"""Tracing hooks.

This file intentionally avoids binding to one provider. Students can plug in LangSmith,
Langfuse, OpenTelemetry, or simple JSON traces.
"""

from collections.abc import Iterator
from contextlib import contextmanager
import os
from time import perf_counter
from typing import Any
from langsmith import Client

# Khởi tạo langsmith client nếu có cấu hình
client = None
if os.environ.get("LANGCHAIN_API_KEY") or os.environ.get("LANGSMITH_API_KEY"):
    try:
        client = Client()
    except Exception:
        pass


@contextmanager
def trace_span(name: str, attributes: dict[str, Any] | None = None) -> Iterator[dict[str, Any]]:
    """Minimal span context used by the skeleton.

    Replace or augment with LangSmith/Langfuse provider spans.
    """
    started = perf_counter()
    span: dict[str, Any] = {"name": name, "attributes": attributes or {}, "duration_seconds": None}
    
    run_id = None
    if client:
        try:
            run = client.create_run(
                name=name,
                run_type="chain",
                inputs={"attributes": attributes or {}},
            )
            run_id = run.id
        except Exception:
            pass

    try:
        yield span
    finally:
        span["duration_seconds"] = perf_counter() - started
        if client and run_id:
            try:
                client.update_run(
                    run_id,
                    outputs={"duration_seconds": span["duration_seconds"]},
                )
            except Exception:
                pass

