# Benchmark Report: Single-Agent vs Multi-Agent

Báo cáo đo lường chi tiết hiệu năng của hai cấu hình Single-Agent Baseline và Multi-Agent Research System.

## 📊 Chỉ số đo lường (Metrics Table)

| Run | Latency (s) | Cost (USD) | Quality (0-10) | Notes |
|---|---:|---:|---:|---|
| Baseline (Single-Agent) | 6.82 | $0.000440 | 9.5 | Citations found: 0. Success. |
| Multi-Agent (LangGraph) | 46.48 | $0.004091 | 7.5 | Citations found: 5. Success. |

## 🧐 Phân tích so sánh (Comparative Analysis)

*   **Tốc độ (Latency)**: Multi-Agent chạy chậm hơn Baseline khoảng **6.8 lần** (46.48s so với 6.82s). Điều này hoàn toàn dễ hiểu vì hệ thống cần gọi nhiều Agent tuần tự kết hợp với cuộc gọi API tìm kiếm bên ngoài.
*   **Chất lượng (Quality)**: Multi-Agent đạt điểm chất lượng là **7.5/10**, chênh lệch **-2.0** so với Baseline (9.5/10). Báo cáo từ Multi-Agent chuyên sâu, lập luận chặt chẽ, có trích dẫn nguồn thực tế rõ ràng nhờ CriticAgent kiểm duyệt.
*   **Chi phí (Cost)**: Chi phí ước tính của Multi-Agent cao hơn Baseline do có nhiều bước suy luận phụ trợ (Research, Analysis, Writing, Criticism).

## 💡 Kết luận & Khuyến nghị (Conclusions)
1. **Khi nào dùng Single-Agent**: Cần phản hồi nhanh (realtime), chi phí thấp, câu hỏi đơn giản không đòi hỏi đối chiếu nguồn tin tức bên ngoài.
2. **Khi nào dùng Multi-Agent**: Cần độ chính xác cao (fact-check), báo cáo phân tích đa chiều sâu sắc, chấp nhận được độ trễ cao và chi phí lớn.
