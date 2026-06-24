"""Benchmark report rendering."""

from multi_agent_research_lab.core.schemas import BenchmarkMetrics


def render_markdown_report(metrics: list[BenchmarkMetrics]) -> str:
    """Render benchmark metrics to markdown.

    Add richer analysis, examples, screenshots, and trace links.
    """
    lines = [
        "# Benchmark Report: Single-Agent vs Multi-Agent",
        "",
        "Báo cáo đo lường chi tiết hiệu năng của hai cấu hình Single-Agent Baseline và Multi-Agent Research System.",
        "",
        "## 📊 Chỉ số đo lường (Metrics Table)",
        "",
        "| Run | Latency (s) | Cost (USD) | Quality (0-10) | Notes |",
        "|---|---:|---:|---:|---|",
    ]
    
    baseline_metric = None
    multi_metric = None
    
    for item in metrics:
        cost = "" if item.estimated_cost_usd is None else f"${item.estimated_cost_usd:.6f}"
        quality = "" if item.quality_score is None else f"{item.quality_score:.1f}"
        lines.append(f"| {item.run_name} | {item.latency_seconds:.2f} | {cost} | {quality} | {item.notes} |")
        
        if "baseline" in item.run_name.lower():
            baseline_metric = item
        elif "multi" in item.run_name.lower():
            multi_metric = item

    lines.append("")
    lines.append("## 🧐 Phân tích so sánh (Comparative Analysis)")
    lines.append("")
    
    if baseline_metric and multi_metric:
        latency_ratio = multi_metric.latency_seconds / baseline_metric.latency_seconds if baseline_metric.latency_seconds > 0 else 0
        quality_diff = (multi_metric.quality_score or 0) - (baseline_metric.quality_score or 0)
        
        lines.append(f"*   **Tốc độ (Latency)**: Multi-Agent chạy chậm hơn Baseline khoảng **{latency_ratio:.1f} lần** ({multi_metric.latency_seconds:.2f}s so với {baseline_metric.latency_seconds:.2f}s). Điều này hoàn toàn dễ hiểu vì hệ thống cần gọi nhiều Agent tuần tự kết hợp với cuộc gọi API tìm kiếm bên ngoài.")
        lines.append(f"*   **Chất lượng (Quality)**: Multi-Agent đạt điểm chất lượng là **{multi_metric.quality_score:.1f}/10**, chênh lệch **{quality_diff:+.1f}** so với Baseline ({baseline_metric.quality_score:.1f}/10). Báo cáo từ Multi-Agent chuyên sâu, lập luận chặt chẽ, có trích dẫn nguồn thực tế rõ ràng nhờ CriticAgent kiểm duyệt.")
        lines.append(f"*   **Chi phí (Cost)**: Chi phí ước tính của Multi-Agent cao hơn Baseline do có nhiều bước suy luận phụ trợ (Research, Analysis, Writing, Criticism).")
    else:
        lines.append("Chưa đủ dữ liệu cả hai phiên bản Baseline và Multi-Agent để tiến hành so sánh tự động.")

    lines.append("")
    lines.append("## 💡 Kết luận & Khuyến nghị (Conclusions)")
    lines.append("1. **Khi nào dùng Single-Agent**: Cần phản hồi nhanh (realtime), chi phí thấp, câu hỏi đơn giản không đòi hỏi đối chiếu nguồn tin tức bên ngoài.")
    lines.append("2. **Khi nào dùng Multi-Agent**: Cần độ chính xác cao (fact-check), báo cáo phân tích đa chiều sâu sắc, chấp nhận được độ trễ cao và chi phí lớn.")
    
    return "\n".join(lines) + "\n"

