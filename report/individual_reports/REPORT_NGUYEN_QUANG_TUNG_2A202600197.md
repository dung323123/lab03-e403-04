# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Nguyen Quang Tung
- **Student ID**: 2A202600197
- **Date**: 2026-04-06

---

## I. Technical Contribution (15 Points)

Trong lab nay, phan em phu trach chinh la **Agent v1** (ReAct loop baseline) trong module `src/agent/agent.py`.

- **Modules Implemented**:
	- `src/agent/agent.py` (trong tam la `_run_v1` va cac helper parse/execute)
	- Tich hop goi tool qua registry tu `src/tools/restaurant_tools.py`
	- Ghi telemetry theo tung buoc qua `src/telemetry/logger.py`

- **Code Highlights**:
	- Xay dung vong lap ReAct co gioi han buoc (`max_steps`) de tranh chay vo han.
	- Chuan hoa prompt he thong trong `get_system_prompt()` de ep dung format:
		- `Thought: ...`
		- `Action: tool_name(args)`
		- `Final Answer: ...`
	- Tach ro cac ham parser:
		- `_parse_action()` dung regex de doc action va tham so.
		- `_extract_final_answer()` de tach cau tra loi cuoi.
		- `_extract_thought()` de luu lai reasoning trace.
	- Thuc thi tool an toan bang `_execute_tool()`:
		- Kiem tra tool ton tai.
		- Bat exception khi tool loi va tra ve object loi co cau truc.
	- Thiet ke duong lui (recovery path) khi model tra output sai dinh dang:
		- Them Observation loi format vao scratchpad.
		- Buoc model sinh lai theo mau Action/Final Answer.

- **Documentation (ReAct interaction)**:
	- Moi vong lap gom:
		1. Build prompt tu lich su + scratchpad (`_build_prompt`).
		2. Model sinh output chua Thought/Action hoac Final Answer.
		3. Neu co Action: chay tool, append Observation vao scratchpad.
		4. Neu co Final Answer: ket thuc vong lap.
	- Cach nay giup agent khong chi "tra loi theo tri nho model", ma co the goi du lieu thuc tu tool truoc khi ket luan.

---

## II. Debugging Case Study (10 Points)

- **Problem Description**:
	- Agent v1 co truong hop model sinh Action sai format (thieu dau `:`), vi du: `Action get_item(GA4)`.
	- Khi do parser khong nhan dien duoc action va agent khong goi duoc tool o buoc do.

- **Log Source**:
	- `logs/2026-04-06.log`
	- Trich doan log:

```json
{"timestamp": "2026-04-06T15:41:24.083533", "event": "AGENT_STEP", "data": {"step": 1, "llm_output": "Thought: Minh can du lieu\nAction get_item(GA4)", "usage": {"prompt_tokens": 50, "completion_tokens": 10}, "latency_ms": 12}}
{"timestamp": "2026-04-06T15:41:24.083997", "event": "AGENT_STEP", "data": {"step": 2, "llm_output": "Thought: Thu dung format\nAction: get_item(GA4)", "usage": {"prompt_tokens": 60, "completion_tokens": 12}, "latency_ms": 10}}
```

- **Diagnosis**:
	- Nguyen nhan chinh la do on dinh format dau ra cua LLM chua cao, khong phai do tool.
	- O step 1, model vi pham format nen regex khong match.
	- Sau khi duoc nhac lai format trong scratchpad, step 2 da sinh dung `Action:` va he thong tiep tuc binh thuong.

- **Solution**:
	- Em trien khai recovery logic trong `_run_v1`:
		- Neu khong parse duoc Action va cung chua co Final Answer, them Observation bao loi dinh dang vao trace.
		- Cho model chay buoc ke tiep voi rang buoc format chat hon.
	- Ket qua: agent khong bi "dung" khi gap output lech chuan mot lan, van co the tu phuc hoi de hoan tat phien.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1. **Reasoning**:
	 - `Thought` giup agent chia bai toan thanh cac buoc nho (can du lieu gi, goi tool nao truoc) thay vi tra loi mot lan nhu chatbot.
	 - Voi truy van nhieu rang buoc (gia, freeship, khu vuc giao hang), ReAct cho ket qua co kiem chung tot hon vi co Observation tu tool.

2. **Reliability**:
	 - Agent co the kem chatbot o cau hoi don gian, vi ton them 1-2 vong lap goi tool nen cham hon.
	 - Agent cung nhay cam voi loi format output (vi du Action sai cu phap), con chatbot thuong tra text truc tiep nen it loi parser.

3. **Observation**:
	 - Observation la tin hieu moi truong rat quan trong de agent sua huong suy luan.
	 - Vi du khi tool tra `not found` hoac `deliverable: false`, agent co co so de tu choi/de nghi nguoi dung cung cap them thong tin thay vi "doan mo".

---

## IV. Future Improvements (5 Points)

- **Scalability**:
	- Tach lop dieu phoi tool sang async executor de chay song song cac truy van doc lap.
	- Bo sung cache ket qua tool theo phien de giam goi lap.

- **Safety**:
	- Them guardrail kiem tra action name + schema args truoc khi thuc thi tool.
	- Bo sung lop policy checker de chan tra loi vi pham rule nghiep vu (vi du giao hang ngoai Ha Noi).

- **Performance**:
	- Toi uu prompt ngan gon hon cho vong lap nhieu buoc de giam token.
	- Them bo danh gia tu dong tu log (step count, token, latency, error rate) de theo doi regression giua v1 va v2.
