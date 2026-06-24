# Lab Guide: Multi-Agent Research System

## Scenario

Bạn cần xây dựng một research assistant có thể nhận câu hỏi dài, tìm thông tin, phân tích và viết câu trả lời cuối cùng. Lab yêu cầu so sánh hai cách làm:

1. **Single-agent baseline**: một agent làm toàn bộ.
2. **Multi-agent workflow**: Supervisor điều phối Researcher, Analyst, Writer.

## Quy tắc quan trọng

- Không thêm agent nếu không có lý do rõ ràng.
- Mỗi agent phải có responsibility riêng.
- Shared state phải đủ rõ để debug.
- Phải có trace hoặc log cho từng bước.
- Phải benchmark, không chỉ nhìn output bằng cảm tính.

## Milestone 1: Baseline

File gợi ý:

- `src/multi_agent_research_lab/cli.py`
- `src/multi_agent_research_lab/services/llm_client.py`

TODO(student): thay baseline placeholder bằng một call LLM thật.

## Milestone 2: Supervisor

File gợi ý:

- `src/multi_agent_research_lab/agents/supervisor.py`
- `src/multi_agent_research_lab/graph/workflow.py`

TODO(student): implement routing policy.

Gợi ý câu hỏi thiết kế:

- Khi nào gọi Researcher?
- Khi nào gọi Analyst?
- Khi nào gọi Writer?
- Khi nào stop?
- Nếu agent fail thì retry hay fallback?

## Milestone 3: Worker agents

File gợi ý:

- `agents/researcher.py`
- `agents/analyst.py`
- `agents/writer.py`

TODO(student): implement từng worker.

## Milestone 4: Trace và benchmark

File gợi ý:

- `observability/tracing.py`
- `evaluation/benchmark.py`
- `evaluation/report.py`

Benchmark tối thiểu:

| Metric | Cách đo gợi ý |
|---|---|
| Latency | wall-clock time |
| Cost | token usage hoặc provider usage |
| Quality | rubric 0-10 do peer review |
| Citation coverage | số claims có source / tổng claims chính |
| Failure rate | số query fail / tổng query |

## Exit ticket

Mỗi nhóm trả lời 2 câu:

1. **Case nào nên dùng multi-agent? Vì sao?**
   - **Các tác vụ nghiên cứu / giải quyết vấn đề phức tạp, đòi hỏi nhiều bước xử lý (Multi-hop Reasoning & Search)**: Ví dụ như viết báo cáo phân tích thị trường, nghiên cứu y khoa, hoặc tổng hợp tài liệu từ nhiều nguồn không đồng nhất.
   - **Lý do**: Cần sự phân vai rõ ràng (decoupling). Việc tách nhỏ tác vụ giúp mỗi Agent tập trung tối đa vào vai trò của mình (Researcher chuyên thu thập dữ liệu thô, Analyst chuyên phản biện, Writer chuyên hành văn, Critic chuyên fact-check), giúp nâng cao chất lượng từng phần, tránh hiện tượng quá tải context trong một prompt và tối ưu hóa khả năng phản biện chéo để triệt tiêu ảo giác (hallucination).

2. **Case nào không nên dùng multi-agent? Vì sao?**
   - **Các tác vụ đơn giản, có tính chất thời gian thực (Real-time / Low-latency requirements)**: Ví dụ như chatbot hỗ trợ khách hàng trả lời nhanh các câu hỏi thường gặp (FAQ), trích xuất thông tin đơn giản từ một đoạn văn ngắn, hoặc dịch thuật trực tiếp.
   - **Lý do**: Hệ thống Multi-Agent có độ trễ (latency) rất cao do phải gọi nhiều cuộc gọi LLM nối tiếp nhau và thực hiện nhiều tác vụ phụ trợ (như tìm kiếm, đọc file). Chi phí token (Cost) cũng tăng lên gấp nhiều lần. Sử dụng Multi-Agent trong các tình huống này là quá phức tạp và lãng phí tài nguyên (over-engineering).

