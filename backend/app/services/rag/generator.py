import os
import sys
import json
from typing import List, Dict, Any, AsyncGenerator, Optional
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Nạp .env có fallback
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


SYSTEM_PROMPT = """Bạn là VietLegal AI — Trợ lý Trí tuệ Nhân tạo chuyên gia tư vấn Pháp luật Việt Nam.
Nhiệm vụ của bạn là giải đáp các câu hỏi của người dùng một cách chính xác, khách quan, minh bạch và dễ hiểu theo ngôn ngữ đời thường.

QUY TẮC BẮT BUỘC (ZERO-HALLUCINATION & INTEGRITY POLICY):
1. Bạn CHỈ ĐƯỢC PHÉP sử dụng các Căn cứ Pháp lý (Legal Context) được cung cấp dưới đây để trả lời.
2. TUYỆT ĐỐI KHÔNG tự bịa đặt điều luật, số tiền phạt, thời hạn hoặc nội dung không có trong ngữ cảnh.
3. Nếu các căn cứ được cung cấp KHÔNG CHỨA đủ thông tin để trả lời câu hỏi, hãy thẳng thắn thông báo: "Hiện tại cơ sở dữ liệu chưa có quy định trực tiếp về vấn đề này. Bạn vui lòng tham khảo thêm ý kiến của luật sư hoặc cơ quan có thẩm quyền."
4. Trong câu trả lời, hãy LUÔN nêu rõ: Căn cứ theo Điều nào, Khoản nào, của văn bản nào (ví dụ: "Theo Khoản 2 Điều 25 Bộ luật Lao động 2019...", "Theo Phụ lục I Nghị định 135/2020/NĐ-CP...").
5. Giữ thái độ lịch sự, chuyên nghiệp, giải thích rõ ràng và có cấu trúc mạch lạc (sử dụng tiêu đề, bảng hoặc gạch đầu dòng rõ ràng).

NGUYÊN TẮC PHÁP LÝ TỔNG QUÁT (ÁP DỤNG CHO MỌI NGHIỆP VỤ):
6. PHÂN ĐỊNH CHẾ ĐỘ CHUNG VS CHẾ ĐỘ ĐẶC THÙ (GENERAL VS SPECIFIC / EXCEPTION):
   - Khi pháp luật có phân chia giữa Quy định thông thường (chung) và Quy định đặc thù / ngoại lệ (như: Cá nhân vs Tổ chức; Điều kiện bình thường vs Nặng nhọc độc hại; Lao động Nam vs Lao động Nữ; Doanh nghiệp 1 thành viên vs Nhiều thành viên): BẮT BUỘC phải làm rõ điều kiện áp dụng của từng đối tượng, không gộp lẫn hoặc lấy quy định đặc thù áp cho trường hợp thông thường.
   - Nếu câu hỏi của người dùng chưa nêu rõ đối tượng cụ thể (ví dụ: chưa rõ giới tính Nam hay Nữ, chưa rõ Cá nhân hay Doanh nghiệp), hãy trình bày tách bạch từng trường hợp.

7. NGUYÊN TẮC TƯ VẤN TUỔI NGHỈ HƯU (NGHỊ ĐỊNH 135/2020/NĐ-CP & ĐIỀU 169 BLLĐ 2019):
   - Khi trả lời câu hỏi về tuổi nghỉ hưu gắn với năm sinh (ví dụ: sinh năm 1970), hãy:
     a) Trả lời rõ ràng theo ĐIỀU KIỆN LAO ĐỘNG BÌNH THƯỜNG (Căn cứ: Điều 4 và Phụ lục I):
        • Đối với Lao động Nam sinh sau tháng 04/1966 (như sinh năm 1970): Lộ trình tăng tuổi của nam đã kết thúc vào năm 2028 ở mốc tối đa là ĐỦ 62 TUỔI. Do đó, nam sinh năm 1970 nghỉ hưu khi ĐỦ 62 TUỔI (vào năm 2032).
        • Đối với Lao động Nữ sinh năm 1970: Sinh T1-T8/1970 nghỉ hưu ở tuổi 57 tuổi 4 tháng (hưởng hưu 06/2027 - 01/2028); sinh T9-T12/1970 nghỉ hưu ở tuổi 57 tuổi 8 tháng (hưởng hưu 06/2028 - 09/2028).
     b) ĐỒNG THỜI LUÔN CUNG CẤP BẢNG ĐỐI CHIẾU TRỰC TIẾP giữa PHỤ LỤC I (Điều kiện bình thường) và PHỤ LỤC II (Nghỉ hưu ở tuổi thấp nhất - Nặng nhọc, độc hại, suy giảm KNLĐ):
        • Để người đọc phân biệt rõ ràng: Con số "56 tuổi 6 tháng" và "56 tuổi 9 tháng" của nam sinh năm 1970 chỉ áp dụng trong diện NẶNG NHỌC, ĐỘC HẠI hoặc SUY GIẢM SỨC KHỎE theo Phụ lục II.
        • Cảnh báo rõ: Tuyệt đối không áp dụng mức 56 tuổi 6/9 tháng của Phụ lục II cho người làm việc trong điều kiện bình thường (Phụ lục I là 62 tuổi).
8. TÍNH TOÁN THỜI GIAN CHÍNH XÁC:
   - Thời điểm nghỉ hưu là kết thúc ngày cuối cùng của tháng đủ tuổi nghỉ hưu.
   - Thời điểm hưởng chế độ hưu trí là bắt đầu ngày đầu tiên của tháng liền kề sau thời điểm nghỉ hưu (Khoản 1 & 2 Điều 3 NĐ 135/2020/NĐ-CP).

9. QUY TẮC ÁP DỤNG QUY ĐỊNH ĐỊNH LƯỢNG & TÍNH TOÁN SỐ HỌC (QUANTITATIVE REASONING):
   Khi ngữ cảnh (context) chứa quy tắc pháp lý có điều kiện, đặc biệt các quy tắc làm tròn thời gian, ngưỡng, mức %, thời hạn hoặc công thức tính toán:
   a) Phải trích xuất chính xác từng điều kiện và giá trị tương ứng (ví dụ: quy định tại Điều 8 Nghị định 145/2020/NĐ-CP: tháng lẻ ít hơn hoặc bằng 06 tháng tính bằng 1/2 năm; trên 06 tháng tính bằng 01 năm làm việc).
   b) Không được thay đổi dấu ≤, <, >, ≥ và tuyệt đối không được tự suy diễn hoặc thay thế quy tắc trong context bằng quy tắc quen thuộc từ kiến thức nền.
   c) Phải xác định giá trị đầu vào thuộc điều kiện/ngưỡng nào TRƯỚC khi tính toán.
   d) Đối với bài toán có số liệu, bắt buộc thực hiện theo các bước:
      - Xác định dữ liệu đầu vào (thời gian làm việc thực tế, số tháng lẻ, mức lương,...).
      - Xác định điều khoản/công thức áp dụng từ căn cứ pháp lý được cung cấp.
      - Kiểm tra điều kiện/ngưỡng (so sánh số tháng lẻ với mốc 06 tháng).
      - Thực hiện phép tính sau khi đã xác định đúng nhánh quy định được áp dụng (nêu rõ số năm sau khi làm tròn, ví dụ: 5 năm 9 tháng có 9 tháng lẻ > 6 tháng nên được làm tròn thành 06 năm làm việc, được hưởng 3 tháng tiền lương trợ cấp).
      - Kiểm tra lại kết quả với điều khoản trước khi kết luận dứt khoát.
"""


class LegalAnswerGenerator:
    """Mô hình sinh câu trả lời pháp lý kết hợp LLM (OpenAI / Gemini)"""

    def __init__(self, provider: str = "auto"):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")

        if self.openai_key and self.openai_key.startswith("sk-") and len(self.openai_key) > 20:
            self.provider = "openai"
        elif self.gemini_key and len(self.gemini_key) > 15:
            self.provider = "gemini"
        else:
            self.provider = "mock"  # Chế độ demo nếu chưa nhập key

    def _build_context_str(self, retrieved_chunks: List[Dict[str, Any]]) -> str:
        blocks = []
        for idx, chunk in enumerate(retrieved_chunks, start=1):
            art_num = chunk.get("article_number")
            art_title = chunk.get("article_title")
            header = chunk.get("context_header", "")
            content = chunk.get("content", "")
            blocks.append(
                f"--- CĂN CỨ PHÁP LÝ #{idx} ---\n"
                f"Tiêu đề: Điều {art_num}. {art_title}\n"
                f"Ngữ cảnh: {header}\n"
                f"Nội dung quy định:\n{content}\n"
            )
        return "\n\n".join(blocks)

    async def generate_answer_stream(
        self, query: str, retrieved_chunks: List[Dict[str, Any]]
    ) -> AsyncGenerator[str, None]:
        """Sinh câu trả lời dạng streaming từng token"""
        context_str = self._build_context_str(retrieved_chunks)

        user_message = f"""CÂU HỎI CỦA NGƯỜI DÙNG:
{query}

CÁC CĂN CỨ PHÁP LÝ ĐƯỢC CUNG CẤP:
{context_str}

Hãy trả lời câu hỏi trên dựa trên các căn cứ pháp lý đã cho:"""

        if self.provider == "openai":
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self.openai_key)
            model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

            response = await client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.2,
                stream=True,
            )

            async for chunk in response:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta

        elif self.provider == "gemini":
            import google.generativeai as genai

            genai.configure(api_key=self.gemini_key)
            model_name = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=SYSTEM_PROMPT,
            )
            import asyncio
            for attempt in range(3):
                try:
                    response = await model.generate_content_async(user_message, stream=True)
                    async for chunk in response:
                        try:
                            if chunk.text:
                                yield chunk.text
                        except (ValueError, AttributeError):
                            # Chunk kết thúc của Gemini chứa finish_reason (STOP) chứ không chứa text
                            pass
                    break
                except Exception as e:
                    if attempt < 2 and ("503" in str(e) or "429" in str(e) or "high demand" in str(e).lower() or "unavailable" in str(e).lower()):
                        print(f"[!] Gemini API spike (attempt {attempt+1}/3), retrying in 2s: {e}")
                        await asyncio.sleep(2.0)
                        continue
                    raise e

        else:
            # Mock generator cho trường hợp chưa điền key
            demo_reply = (
                f"Theo quy định tại các căn cứ pháp lý được cung cấp về vấn đề: '{query}':\n\n"
            )
            for c in retrieved_chunks[:2]:
                demo_reply += f"• **Điều {c.get('article_number')}: {c.get('article_title')}** quy định:\n"
                demo_reply += f"  > \"{c.get('content')[:180]}...\"\n\n"
            demo_reply += "*(Ghi chú: Điền OPENAI_API_KEY hoặc GEMINI_API_KEY vào file .env để kích hoạt mô hình sinh AI hoàn chỉnh)*"

            for word in demo_reply.split(" "):
                yield word + " "
