# Design Template

## Problem

Hệ thống cần xử lý các câu hỏi nghiên cứu dài và phức tạp từ người dùng về các chủ đề công nghệ. Đầu ra yêu cầu là một bài báo cáo khoa học, có cấu trúc rõ ràng, tổng hợp đa chiều từ nhiều nguồn tin trên internet, có phản biện logic cao và trích dẫn cụ thể (citation) để tránh hiện tượng ảo giác (hallucination).

## Why multi-agent?

Single-Agent không đủ năng lực vì:
1. **Thiếu khả năng phản biện chéo**: Single-Agent có xu hướng đồng thuận ngay lập tức với thông tin tìm thấy đầu tiên và dễ bị ảo giác thông tin.
2. **Quá tải Context**: Khi vừa phải tìm kiếm, vừa tóm tắt, vừa phân tích phản biện và vừa định dạng viết bài, chất lượng từng phần của Single-Agent bị giảm sút do giới hạn về sự tập trung (attention) trong một lượt gọi duy nhất.
3. **Thiếu tính modular**: Khó debug lỗi xảy ra ở bước nào (lỗi do tìm kiếm thông tin sai hay lỗi do viết bài kém).

## Agent roles

| Agent | Responsibility | Input | Output | Failure mode |
|---|---|---|---|---|
| Supervisor | Điều phối đồ thị, quyết định node chạy tiếp theo hoặc dừng. | `ResearchState` (chứa route_history, notes) | Route tiếp theo (`researcher`, `analyst`, `writer`, `critic`, `done`) | Định tuyến sai hướng do prompt không bao quát hết các cạnh. |
| Researcher | Tìm kiếm internet qua Tavily và tổng hợp ghi chú thô. | `state.request.query` | `state.sources`, `state.research_notes` | Tavily không trả về kết quả hoặc snippets quá ngắn. |
| Analyst | Phân tích phản biện, phát hiện mâu thuẫn hoặc lỗ hổng logic. | `state.research_notes` | `state.analysis_notes` | Over-analyzing dẫn đến tạo mâu thuẫn giả định không có thật. |
| Writer | Tổng hợp thông tin, viết báo cáo Markdown có trích dẫn cụ thể. | `state.research_notes`, `state.analysis_notes` | `state.final_answer` (bản thảo) | Bỏ quên References hoặc dẫn citation sai lệch. |
| Critic | Fact-check, rà soát ảo giác, kiểm duyệt bài viết thô đối chiếu nguồn thô. | `state.final_answer`, `state.sources` | `state.final_answer` (bản tinh chỉnh) | Khắt khe quá mức dẫn đến viết lại toàn bộ làm mất phong cách tác giả. |

## Shared state

*   `request: ResearchQuery`: Chứa câu hỏi ban đầu, số lượng nguồn tối đa.
*   `iteration: int`: Số lần lặp để làm guardrail chống lặp vô hạn.
*   `route_history: list[str]`: Lịch sử các bước định tuyến để Supervisor ra quyết định và phục vụ tracing.
*   `sources: list[SourceDocument]`: Danh sách các nguồn tin thô thu thập từ internet.
*   `research_notes: str`: Ghi chú nghiên cứu ban đầu từ Researcher.
*   `analysis_notes: str`: Ghi chú phân tích phản biện từ Analyst.
*   `final_answer: str`: Kết quả báo cáo cuối cùng đã qua tinh chỉnh.
*   `agent_results: list[AgentResult]`: Nhật ký kết quả chi tiết của từng Agent để phục vụ tính toán token/chi phí.
*   `trace: list[dict[str, Any]]`: Lưu trữ dấu vết sự kiện của toàn hệ thống.
*   `errors: list[str]`: Ghi nhận các lỗi phát sinh trong quá trình chạy.

## Routing policy

```text
Supervisor ➔ Researcher ➔ Analyst ➔ Writer ➔ Critic ➔ done (END)
               ▲            ▲         ▲         ▲
               └────────────┴─────────┴─────────┘ (Vòng lặp qua Supervisor sau mỗi node)
```

## Guardrails

- **Max iterations**: Giới hạn tối đa 6 lần lặp của đồ thị (quản lý bởi Supervisor) để chống vòng lặp vô hạn.
- **Timeout**: Đặt giới hạn 60 giây cho mỗi cuộc gọi API LLM.
- **Retry**: Thiết lập cơ chế tự động thử lại (retry) tối đa 3 lần với exponential backoff bằng thư viện `tenacity` đối với `LLMClient`.
- **Validation**: Đảm bảo các trường dữ liệu bắt buộc có mặt trước khi chuyển giao State giữa các node.

## Benchmark plan

*   **Queries**: Các câu hỏi nghiên cứu về công nghệ dạng: *"Research GraphRAG state-of-the-art and summarize in 300 words"*.
*   **Metrics**: Latency (s), Cost (USD), Quality Score (0-10, chấm bởi LLM-as-a-judge), Citation count.
*   **Expected outcome**: Multi-Agent cho chất lượng vượt trội rõ rệt (Quality Score cao hơn 20%, có trích dẫn chính xác) nhưng chấp nhận Latency và Cost cao hơn Baseline.
