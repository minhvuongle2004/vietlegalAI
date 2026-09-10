# BÁO CÁO THÍ NGHIỆM ĐIỀU KHIỂN TRỌNG SỐ RRF (CONTROLLED RRF EXPERIMENT)
## BƯỚC 2.0 — TỐI ƯU HÓA GHÉP DENSE VÀ SPARSE TRÊN BỘ DỮ LIỆU GOLD V2 (225 CASES)

- **Thời gian thực hiện**: 2026-09-11 01:17:48
- **Tập dữ liệu chuẩn hóa**: `gold_retrieval_225_cases_v2.json` (225 cases)
- **Trạng thái Production**: Qdrant 7.982 points (bảo toàn); 25 benchmark regression cases (bảo toàn)
- **Cơ chế**: Cô lập hoàn toàn RRF trên truy vấn gốc, khảo sát 8 dải trọng số Sparse, sau đó đo lường riêng ảnh hưởng của Query Decomposition.

---

### I. TỔNG HỢP HIỆU NĂNG CÁC CẤU HÌNH TRỌNG SỐ (WEIGHT EXPLORATION)

> [!NOTE]
> **Acceptance Target Vòng 1**: `Hybrid Hit@5 >= Dense Hit@5 = 54.67% (123/225)`.
> Cận trên lý thuyết (`Dense OR Sparse` Top 5) = **128/225 (56.89%)**.

| Cấu hình Truy xuất | Trọng số Dense | Trọng số Sparse | Hit@1 | Hit@3 | Hit@5 | Miss@5 | Cứu hộ (Rescue) | Thoái lui (Regress) | Trạng thái Vòng 1 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Dense-only (Baseline)** | 1.00 | 0.00 | 86 (38.22%) | 115 (51.11%) | **123 (54.67%)** | 102 (45.33%) | - | - | *Baseline nòng cốt* |
| **Sparse-only (Baseline)** | 0.00 | 1.00 | 13 (5.78%) | 20 (8.89%) | 23 (10.22%) | 202 (89.78%) | - | - | *Baseline từ khóa* |
| **Hybrid (0.10)** ⭐ **(BEST)** | 1.00 | 0.10 | 73 (32.44%) | 114 (50.67%) | **132 (58.67%)** | 93 (41.33%) | +10 | -1 | ACCEPT 🟢 |
| **Hybrid (0.20)** | 1.00 | 0.20 | 61 (27.11%) | 101 (44.89%) | **123 (54.67%)** | 102 (45.33%) | +10 | -10 | ACCEPT 🟢 |
| **Hybrid (0.25)** | 1.00 | 0.25 | 57 (25.33%) | 94 (41.78%) | **119 (52.89%)** | 106 (47.11%) | +10 | -14 | REGRESSION 🔴 |
| **Hybrid (0.30)** | 1.00 | 0.30 | 54 (24.0%) | 92 (40.89%) | **116 (51.56%)** | 109 (48.44%) | +10 | -17 | REGRESSION 🔴 |
| **Hybrid (0.40)** | 1.00 | 0.40 | 53 (23.56%) | 90 (40.0%) | **117 (52.0%)** | 108 (48.0%) | +11 | -17 | REGRESSION 🔴 |
| **Hybrid (0.50)** | 1.00 | 0.50 | 52 (23.11%) | 89 (39.56%) | **116 (51.56%)** | 109 (48.44%) | +11 | -18 | REGRESSION 🔴 |
| **Hybrid (0.75)** | 1.00 | 0.75 | 49 (21.78%) | 88 (39.11%) | **116 (51.56%)** | 109 (48.44%) | +11 | -18 | REGRESSION 🔴 |
| **Hybrid (1.00)** | 1.00 | 1.00 | 49 (21.78%) | 86 (38.22%) | **110 (48.89%)** | 115 (51.11%) | +9 | -22 | REGRESSION 🔴 |

---

### II. PHÂN TÍCH THOÁI LUI VÀ CỨU HỘ (REGRESSION & RESCUE ANALYSIS)

Tại cấu hình tối ưu nhất (**Dense = 1.00, Sparse = 0.10**):
- **Số ca Sparse cứu Dense thành công (Dense FAIL → Hybrid PASS)**: **10 ca**.
- **Số ca Dense đúng nhưng bị Hybrid làm thoái lui (Dense PASS → Hybrid FAIL)**: **1 ca**.
- **Dense PASS → Hybrid PASS**: 122 / 123 cases.
- **Dense FAIL → Hybrid FAIL**: 92 / 102 cases.

#### 1. Chi tiết các ca được Sparse cứu hộ thành công:
| Test Case ID | Lĩnh vực | Truy vấn | Dense Rank | Sparse Rank | Hybrid Rank |
| :--- | :--- | :--- | :---: | :---: | :---: |
| `GOLD-DIR-03` | DIRECT_RULE | Người lái xe ô tô có được sử dụng điện thoại bằng tay khi xe đang... | None | None | **5** |
| `GOLD-DIR-11` | DIRECT_RULE | Niên hạn sử dụng của xe ô tô chở hàng (xe tải) tối đa là bao nhiê... | None | 2 | **5** |
| `GOLD-DIR-12` | DIRECT_RULE | Niên hạn sử dụng của xe ô tô chở người từ 10 chỗ ngồi trở lên tối... | None | 2 | **4** |
| `GOLD-DIR-13` | DIRECT_RULE | Biển số xe cơ giới được cấp và quản lý theo mã định danh của ai?... | None | 1 | **3** |
| `GOLD-DIR-27` | DIRECT_RULE | Việc lắp thêm phụ kiện như bậc lên xuống, giá nóc dưới 20cm có bị... | None | None | **5** |
| `GOLD-ART-19` | ARTICLE_RETRIEVAL | Quy định về hồ sơ, thủ tục đổi, cấp lại giấy phép lái xe nằm ở Đi... | None | None | **3** |
| `GOLD-ART-20` | ARTICLE_RETRIEVAL | Điều nào của Thông tư 73/2024/TT-BCA quy định các trường hợp Cảnh... | None | None | **5** |
| `GOLD-EXC-25` | CONDITIONAL_EXCEPTION | Ngoại lệ nào đối với xe kinh doanh vận tải hành khách không cần l... | None | None | **5** |
| `GOLD-MUL-24` | MULTI_DOCUMENT | Quy định về thu phí sử dụng đường bộ cao tốc theo Nghị định 130 v... | None | 1 | **3** |
| `GOLD-AMD-03` | AMENDMENT_LINEAGE | Nghị định 241/2026/NĐ-CP sửa đổi, bổ sung các quy định nào của Ng... | None | None | **5** |

#### 2. Chi tiết các ca bị thoái lui (Regression cases):
| Test Case ID | Lĩnh vực | Truy vấn | Dense Rank | Sparse Rank | Hybrid Rank |
| :--- | :--- | :--- | :---: | :---: | :---: |
| `GOLD-DIR-04` | DIRECT_RULE | Tốc độ tối đa cho phép xe con chạy trong khu vực đông dân cư trên... | 2 | None | **None** |

---

### III. ĐO LƯỜNG ẢNH HƯỞNG CỦA QUERY DECOMPOSITION (ISOLATED COMPARISON)

So sánh độc lập trên cùng cấu hình trọng số tối ưu giữa:
1. **Cấu hình A (Original Query)**: Query gốc → Dense (1.00) + Sparse (best weight) → RRF
2. **Cấu hình B (Decomposed Query)**: Query gốc + Subqueries (1.30) + Target Injection + Sparse → RRF

| Phương pháp Truy vấn | Hit@1 | Hit@3 | Hit@5 | Số ca cải thiện | Số ca bị kéo sai lệch (Hại) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Cấu hình A (Original Query)** | 73 (32.44%) | 114 (50.67%) | **132 (58.67%)** | Baseline A | Baseline A |
| **Cấu hình B (Decomposed Query)** | 59 (26.22%) | 94 (41.78%) | **121 (53.78%)** | +3 | -14 |

> [!WARNING]
> **Kết luận về Query Decomposition**: Cơ chế phân rã câu hỏi hiện tại làm thay đổi Hit@5 từ **58.67%** thành **53.78%**. Có **14 cases bị kéo sai lệch** do các subqueries phạt hành chính gán nhầm target articles vào các câu hỏi nguyên tắc.

---

### IV. KHUYẾN NGHỊ VÀ HÀNH ĐỘNG TIẾP THEO (RECOMMENDED NEXT ACTION)

1. **Khóa cấu hình RRF tối ưu**: Sử dụng `w_dense = 1.00`, `w_sparse = 0.10`, `rrf_k = 60`.
2. **Tách biệt hoặc tái cấu trúc Query Decomposition**: Loại bỏ việc gán cứng 'target_article' ép vào candidate pool, tránh làm loãng các truy vấn nguyên tắc/tốc độ/khoảng cách.
3. **Chuẩn bị cho Tầng Reranker (nếu cần)**: Sau khi tầng Hybrid RRF đạt mức ổn định vững chắc, mới xem xét đưa Cross-Encoder Reranker vào để tinh chỉnh Top 1/Top 3.

---

### V. KẾT LUẬN CUỐI CÙNG (FINAL VERDICT)

# **FINAL VERDICT: `RRF CONFIGURATION SELECTED 🟢`**