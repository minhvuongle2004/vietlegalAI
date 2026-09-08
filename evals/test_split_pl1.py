import os
import sys
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.reingest_nd135_tables import (
    html_table_to_matrix,
    format_subtable_markdown,
)
from bs4 import BeautifulSoup

html_path = PROJECT_ROOT / "data" / "01_raw" / "html" / "135_2020_ND_CP.html"
with open(html_path, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

tables = soup.find_all("table")
grid_t5 = html_table_to_matrix(tables[4])

note_nam_pl1 = (
    "> **QUY TẮC PHÁP LÝ BẮT BUỘC ĐỐI VỚI LAO ĐỘNG NAM (ĐIỀU KIỆN LAO ĐỘNG BÌNH THƯỜNG)**:\n"
    "> 1. Theo Điều 4 và Phụ lục I Nghị định 135/2020/NĐ-CP, lộ trình tăng tuổi nghỉ hưu của nam kết thúc vào năm 2028 ở mốc đủ 62 tuổi.\n"
    "> 2. **Tất cả lao động nam sinh từ tháng 04/1966 trở đi (bao gồm các năm 1967, 1968, 1969, 1970, 1971, 1972... trở về sau) đều nghỉ hưu khi ĐỦ 62 TUỔI**.\n"
    "> 3. **Thời điểm nghỉ hưu**: Kết thúc ngày cuối cùng của tháng người lao động đủ 62 tuổi.\n"
    "> 4. **Thời điểm hưởng lương hưu**: Bắt đầu ngày đầu tiên của tháng liền kề sau thời điểm nghỉ hưu (Năm hưởng lương hưu = Năm sinh + 62)."
)
md_pl1_nam = format_subtable_markdown(
    grid_t5,
    col_start=0,
    col_end=5,
    title="BẢNG TRA CỨU LỘ TRÌNH TUỔI NGHỈ HƯU ĐỐI VỚI LAO ĐỘNG NAM (PHỤ LỤC I - NGHỊ ĐỊNH 135/2020/NĐ-CP)",
    note_suffix=note_nam_pl1,
    min_row=3,
    max_row=67,
)

note_nu_pl1 = (
    "> **QUY TẮC ĐỐI VỚI LAO ĐỘNG NỮ (ĐIỀU KIỆN LAO ĐỘNG BÌNH THƯỜNG)**:\n"
    "> 1. Kể từ năm 2021, tuổi nghỉ hưu của nữ tăng mỗi năm 4 tháng cho đến khi đủ 60 tuổi vào năm 2035.\n"
    "> 2. Kể từ tháng 01/1975 trở đi, lao động nữ nghỉ hưu khi đủ 60 tuổi."
)
md_pl1_nu = format_subtable_markdown(
    grid_t5,
    col_start=5,
    col_end=10,
    title="BẢNG TRA CỨU LỘ TRÌNH TUỔI NGHỈ HƯU ĐỐI VỚI LAO ĐỘNG NỮ (PHỤ LỤC I - NGHỊ ĐỊNH 135/2020/NĐ-CP)",
    note_suffix=note_nu_pl1,
    min_row=3,
    max_row=None,
)

print(f"md_pl1_nam length: {len(md_pl1_nam)} characters, has 1966: {'1966' in md_pl1_nam}")
print(f"md_pl1_nu length:  {len(md_pl1_nu)} characters, has 1972: {'1972' in md_pl1_nu}")

# Kiểm tra dòng tháng 7/1972 trong md_pl1_nu
for line in md_pl1_nu.split("\n"):
    if "1972" in line and "7" in line:
        print("Line found in md_pl1_nu:", line)
