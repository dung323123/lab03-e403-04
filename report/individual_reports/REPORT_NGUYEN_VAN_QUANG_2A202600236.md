# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Nguyễn Văn Quang
- **Student ID**: 2A202600236
- **Date**: 06/04/2026

---

## I. Technical Contribution (15 Points)

*Describe your specific contribution to the codebase (e.g., implemented a specific tool, fixed the parser, etc.).*

- **Modules Implementated**: 
`streamlit.py`
`src/agent/agent.py`
`src/agent/agent_v2.py`
`src/chatbot/chatbot.py`
`src/core/metrics.py`
`src/core/retry.py`
`src/tools/restaurant_tools.py`
`src/tools/menu_tools.py`
- **Code Highlights**:
`streamlit.py[58:247]`
`src/agent/agent.py[25:29, 92:96, 102:108, 152:169, 175:179, 196:202, 247:253, 260:279]`
`src/agent/agent_v2.py[32:35, 59:66, 109:115, 124:132, 186:217, 258:280]`
`src/chatbot/chatbot.py[38:41, 237:251]`
`src/core/metrics.py[all]`
`src/core/retry.py[all]`
`src/tools/restaurant_tools.py[67:82]`
`src/tools/menu_tools.py[119:145]`
`tests/test_restaurant_tools.py[all]`

- **Documentation**: Đoạn code chủ yếu vào việc giám sát token sử dụng và latency, cùng với việc xây dựng UI cho phép người dùng tương tác conversationally với agent và chatbot. Tạo tab monitor để quan sát và so sánh hiệu năng của agent và chatbot. Ngoài ra còn thêm 1 tool để xử lý các trường hợp user gọi các món không chính xác theo tên. Cuối cùng, tạo các test case để kiểm tra các tool đã tạo.

---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**: Không có tool để list các món ăn trong menu, khiến agent tưởng món không có trong menu

- **Diagnosis**: tại không có tool để list các món ăn trong menu, 
- **Solution**: Thêm 1 tool để list các món ăn trong menu

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning**: How did the `Thought` block help the agent compared to a direct Chatbot answer?

> Giai đoạn 'Thought' giúp agent chia nhỏ vấn đề và suy luận từng bước, từ đó đưa ra câu trả lời chính xác hơn với sự kết hợp của tool calling.

2.  **Reliability**: In which cases did the Agent actually perform *worse* than the Chatbot?

> Không trường hợp nào chatbot hoạt động tốt hơn agent vì hệ thống chỉ trả lời các câu hỏi liên quan đến nhà hàng, không được phép bịa câu trả lời.

3.  **Observation**: How did the environment feedback (observations) influence the next steps?

> Nó giúp agent có thể điều chỉnh hành động của mình dựa trên kết quả của các tool call trước đó.

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**:
> Thêm 1 hàng đợi để xử lý các tool call; tạo 2 hàng: 1 hàng song song và 1 hàng tuần tự
- **Safety**:
> Thêm guardrail để kiểm tra các tool call
- **Performance**:
> Dựa vào monitor, ta có thể tối ưu prompt và model để giảm token sử dụng và latency

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
