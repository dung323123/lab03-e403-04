from typing import List, Dict
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger

# Chỉ trả lời các câu hỏi liên quan đến thực đơn, giá cả, combo, mã giảm giá và đặt hàng.
# Với câu hỏi ngoài phạm vi (thời tiết, tin tức, v.v.) hãy từ chối lịch sự.

# --- THỰC ĐƠN ---
# Món chính:
#   GA2  - Gà rán 2 miếng       : 69.000đ
#   GA4  - Gà rán 4 miếng       : 129.000đ
#   BURGER - Burger gà           : 45.000đ
#   NUGGETS - Gà viên 6 miếng   : 55.000đ

# Món phụ:
#   FRIES  - Khoai tây chiên     : 30.000đ
#   SALAD  - Salad bắp cải       : 25.000đ

# Nước uống:
#   PEPSI  - Pepsi lon            : 15.000đ

# Không có sẵn:
#   CHEESE_BALLS - Bóng phô mai  : hết hàng

# --- COMBO ---
#   PERSONAL (1 người) : GA2 + FRIES + PEPSI          = 99.000đ  (gốc 114.000đ)
#   FF2      (2 người) : GA4 + 2 FRIES + 2 PEPSI      = 159.000đ (gốc 189.000đ)
#   FAMILY   (4 người) : 2×GA4 + 2×FRIES + 4×PEPSI + NUGGETS = 329.000đ (gốc 393.000đ)

# --- MÃ GIẢM GIÁ ---
#   GA20      : Giảm 20%, đơn tối thiểu 150.000đ   (đang hoạt động)
#   STUDENT10 : Giảm 10%, đơn tối thiểu 100.000đ   (đang hoạt động)
#   FREESIDE  : Giảm 30.000đ món phụ, đơn tối thiểu 120.000đ (đang hoạt động)
#   OLD50     : Giảm 50% — ĐÃ HẾT HẠN

# --- GIAO HÀNG ---
#   Chỉ giao trong Hà Nội.
#   Miễn phí giao hàng cho đơn từ 200.000đ.

class RestaurantChatbot:
    """
    Baseline chatbot WITHOUT tools.
    Dùng để minh họa hạn chế của LLM thuần so với ReAct Agent:
    - Không tính toán chính xác được
    - Không kiểm tra tồn kho / trạng thái thực tế
    - Không phát hiện cross-city
    - Dễ hallucinate giá sai
    """

    SYSTEM_PROMPT = """Bạn là chatbot của nhà hàng gà rán tại Hà Nội.

Trả lời ngắn gọn, lịch sự bằng tiếng Việt."""

    def __init__(self, llm: LLMProvider):
        self.llm = llm
        self.history: List[Dict[str, str]] = []

    def chat(self, user_message: str) -> str:
        self.history.append({"role": "user", "content": user_message})

        # Build single-turn prompt from history
        history_text = "\n".join(
            f"{'Người dùng' if m['role'] == 'user' else 'Chatbot'}: {m['content']}"
            for m in self.history
        )

        result = self.llm.generate(history_text, system_prompt=self.SYSTEM_PROMPT)
        response = result["content"]

        self.history.append({"role": "assistant", "content": response})
        logger.log_event("CHATBOT_RESPONSE", {
            "input": user_message,
            "output": response,
            "usage": result["usage"],
            "latency_ms": result["latency_ms"],
        })
        return response

    def reset(self):
        self.history = []
