---
name: nhat-ky-do-an-nls
description: Tự động ghi chép, cập nhật và khôi phục ngữ cảnh làm việc cho Đồ án cuối kỳ môn Năng lực số (Đề tài Phân tích dữ liệu & Tối ưu tồn kho chuỗi bán lẻ Maven Toys) theo cấu trúc chuẩn bài bản kết hợp phương pháp P-D-M-V trong tệp 'nhật ký làm việc.md'. Kích hoạt khi bắt đầu phiên làm việc, khi hoàn thành tác vụ/thay đổi dữ liệu, file Excel, file Power BI (.pbix), mã nguồn Python, mô hình Machine Learning, hoặc khi người dùng yêu cầu lưu/tổng kết nhật ký đồ án.
---
<!--
Author: Nhóm Sinh viên Đồ án Năng lực số
Description: Antigravity Skill for NLS Final Project (Maven Toys Retail & Inventory Analytics) Session Worklog Management
-->

# Session Worklog Manager - Đồ Án Cuối Kỳ Năng Lực Số (Chuẩn P-D-M-V)

Kỹ năng này giúp duy trì bộ nhớ dài hạn, tính liên tục và lưu vết toàn bộ tiến trình thực hiện đồ án môn **Năng lực số (HK3 - 2026)** với đề tài: **Phân tích hiệu quả kinh doanh và ứng dụng Machine Learning trong dự báo nhu cầu bán hàng nhằm tối ưu tồn kho tại chuỗi bán lẻ Maven Toys**.

Kỹ năng đảm bảo việc ghi chép bám sát **Rubric đánh giá đồ án cuối kỳ (CLO1, CLO2, CLO3, CLO5)**, tích hợp phương pháp tư duy kỹ thuật chuyên sâu **P-D-M-V** (Prompt & Produce, Deconstruct & Read, Mutate & Break, Validate & Refine).

Tệp nhật ký mục tiêu duy nhất: `./nhật ký làm việc.md` (tại thư mục gốc của đồ án).

---

## 1. Thông Tin Đồ Án & Nhóm Sinh Viên

- **Môn học:** Năng lực số (HK3 - 2026)
- **Tên đề tài:** Phân tích hiệu quả hoạt động kinh doanh và ứng dụng Machine Learning trong dự báo nhu cầu bán hàng nhằm tối ưu tồn kho chuỗi bán lẻ Maven Toys
- **Bộ dữ liệu:** Maven Toys / Mexico Toy Sales (4 bảng: `sales.csv`, `inventory.csv`, `products.csv`, `stores.csv`)
- **Nhóm sinh viên thực hiện:**
  - Nguyễn Đỗ Tuấn Tú - MSSV: 2521001112
  - Huỳnh Đức Phương Thảo - MSSV: 2521001097

---

## 2. Nguyên Tắc Cốt Lõi (Core Principles)

1. **Vị trí và tên tệp (Scope & File Path):**
   - Bắt buộc là `./nhật ký làm việc.md` tại thư mục gốc của đồ án (`D:/University/Chương trình đào tạo/Năm 2026/HK3 - 2026/Năng lực số/Đồ án NDTT/nhật ký làm việc.md`).
   - **Tuyệt đối không ghi lẫn** sang các thư mục đồ án khác hoặc tệp nhật ký của môn học khác.

2. **Thứ tự thời gian đảo ngược (Reverse Chronological Order):**
   - Phiên làm việc mới nhất **luôn luôn được chèn lên trên cùng** (ngay bên dưới phần Header thông tin đồ án và đường phân cách `---` đầu tiên).

3. **Cấu trúc phiên bắt buộc (Session Structure):**
   Mỗi phiên làm việc phải tuân thủ nghiêm ngặt 5 mục gạch đầu dòng bắt buộc:
   1. `- **Môi trường:**` Windows (PowerShell) / macOS / Linux.
   2. `- **Mục tiêu phiên:**` Mô tả bài toán nghiệp vụ bán lẻ hoặc kỹ thuật cần giải quyết (Làm sạch data / Excel / Power BI / Python EDA / Machine Learning / Soạn thảo báo cáo Word).
   3. `- **Nội dung đã hoàn thành:**` Mô tả chi tiết tác vụ đã xong; liệt kê các file kèm link Markdown: `[tên_file](file:///đường_dẫn)`.
   4. `- **Tương tác Prompt & Quyết định kỹ thuật:**` Chứa 3 mục con tích hợp phương pháp **P-D-M-V**:
      - `*Prompt chiến lược đã thực thi:*` (P - Prompt & Produce): Ghi lại chính xác prompt đã giao cho Antigravity IDE để sinh mã xử lý dữ liệu, công thức Excel, DAX measure hoặc code huấn luyện ML.
      - `*Kinh nghiệm bóc tách code & Mutate/Break:*` (D - Deconstruct & Read & M - Mutate & Break): Bóc tách logic công thức cốt lõi (Excel Subtotal/Pivot, DAX CALCULATE/FILTER, thuật toán Random Forest/Linear Regression...); ghi lại các lỗi dữ liệu phát hiện và các thử nghiệm thay đổi tham số/ngưỡng điều kiện để quan sát biến thiên kết quả.
      - `*Quyết định kiến trúc & Nghiệp vụ:*` (V - Validate & Refine): Đối chiếu kết quả phân tích với nghiệp vụ bán lẻ thực tế (vòng quay tồn kho, tính mùa vụ, biên lợi nhuận), kiểm chứng mô hình ML và định hướng hoàn thiện báo cáo 30–40 trang theo đúng Rubric.
   5. `- **Tồn đọng & Bước tiếp theo:**` 2–3 đầu việc ưu tiên cần làm trong phiên tiếp theo.

4. **Tiết kiệm Token & Tối ưu Ngữ cảnh (Context Efficiency):**
   - Khi khôi phục ngữ cảnh đầu phiên, chỉ đọc phần Header và **3–5 phiên gần nhất** để tối ưu hóa context window.

5. **Chuẩn Typography & Markdown:**
   - Dấu câu dính liền ký tự trước nó, có đúng 1 khoảng trắng sau nó.
   - Bắt buộc có dòng trắng rỗng (blank line) trước và sau mỗi danh sách gạch đầu dòng (`-`) hoặc đánh số (`1.`).
   - Sử dụng Markdown link chuẩn: `[tên_file](file:///đường_dẫn)`.

---

## 3. Quy Trình Thực Thi (Execution Workflow)

### A. Khôi Phục Ngữ Cảnh Đầu Phiên (Session Startup)

1. Kiểm tra sự tồn tại của tệp `./nhật ký làm việc.md`. Nếu chưa có, khởi tạo tệp với phần Header chuẩn.
2. Đọc Header và **3–5 phiên gần nhất**.
3. Tóm tắt ngắn gọn và chủ động cho người dùng:
   > *"✅ Đã khôi phục ngữ cảnh Đồ án Năng lực số (Maven Toys Analytics). Phiên trước ([YYYY-MM-DD HH:MM]) đã hoàn thành: [Tóm tắt công việc/kết quả Excel, Power BI hoặc ML]. Quyết định kỹ thuật/Thử nghiệm gần nhất: [Tóm tắt]. Bước tiếp theo dự kiến: [Đầu việc tiếp theo]. Sẵn sàng bắt đầu!"*

### B. Ghi Nhận Cuối Phiên / Hoàn Tất Tác Vụ (Session Wrap-up)

1. Xác định thời gian thực hiện (`YYYY-MM-DD HH:MM`) và môi trường thực thi (`Windows (PowerShell)`).
2. Tổng hợp nội dung phiên theo đúng mẫu cấu trúc chuẩn Mục 4 tích hợp P-D-M-V.
3. Chèn khối nhật ký mới vào ngay bên dưới đường phân cách ngang `---` đầu tiên của `./nhật ký làm việc.md`.

---

## 4. Mẫu Cấu Trúc Chuẩn Bắt Buộc

```markdown
# Nhật ký Làm việc Đồ án Năng lực số

Tệp này tự động lưu vết các phiên làm việc giữa Nhóm sinh viên và Antigravity IDE.
- **Tên môn học:** Năng lực số (HK3 - 2026)
- **Tên đề tài:** Phân tích hiệu quả hoạt động kinh doanh và ứng dụng Machine Learning trong dự báo nhu cầu bán hàng nhằm tối ưu tồn kho chuỗi bán lẻ Maven Toys
- **Nhóm sinh viên thực hiện:**
  - Nguyễn Đỗ Tuấn Tú - MSSV: 2521001112
  - Huỳnh Đức Phương Thảo - MSSV: 2521001097

---

## [YYYY-MM-DD HH:MM] - [Tiêu đề Tóm tắt Phiên làm việc]
- **Môi trường:** Windows (PowerShell)
- **Mục tiêu phiên:** Mô tả bài toán hoặc chức năng cần giải quyết trong phiên (ví dụ: làm sạch dữ liệu sales/inventory, thiết lập PivotTable trong Excel, dựng Dashboard Power BI, huấn luyện mô hình Random Forest...).
- **Nội dung đã hoàn thành:**
  - Mô tả chi tiết các tác vụ đã thực hiện thành công.
  - Các tệp đã tạo hoặc chỉnh sửa kèm link Markdown: `[tên_file](file:///đường_dẫn)`.
- **Tương tác Prompt & Quyết định kỹ thuật:**
  - *Prompt chiến lược đã thực thi:* "Prompt chi tiết đã đưa cho Antigravity IDE để phân tích/sinh mã/viết công thức..."
  - *Kinh nghiệm bóc tách code & Mutate/Break:* Bóc tách logic then chốt (công thức Excel, DAX measure, hoặc code Python sklearn); các lỗi phát hiện (sai định dạng tiền tệ, null, lệch data model...) và các tham số thử nghiệm thay đổi (ngưỡng tồn kho, n_estimators, max_depth...).
  - *Quyết định kiến trúc & Nghiệp vụ:* Lựa chọn thuật toán, xử lý tồn kho an toàn (Safety Stock), đối chiếu biên lợi nhuận danh mục sản phẩm theo thực tế bán lẻ và căn chỉnh theo rubric báo cáo.
- **Tồn đọng & Bước tiếp theo:** 2–3 đầu việc ưu tiên cần làm trong phiên tiếp theo.

---
```

---

## 5. Cẩm Nang Lưu Vết P-D-M-V Cho Môn Năng Lực Số

Khi điền mục `- **Tương tác Prompt & Quyết định kỹ thuật:**`, áp dụng 4 trụ cột P-D-M-V cho các mảng nội dung của đồ án:

| Trụ cột | Ứng dụng trong Excel & Power BI | Ứng dụng trong Python & Machine Learning |
| :--- | :--- | :--- |
| **P - Prompt & Produce** | Ghi lại prompt hướng dẫn tạo 2 điều kiện Conditional Formatting, 3 tình huống SubTotal, 3 kịch bản Pivot Table/Chart, các Measure DAX trong Power BI. | Ghi lại prompt viết script EDA với Pandas/Matplotlib và prompt huấn luyện mô hình dự báo nhu cầu bán hàng (Linear Regression & Random Forest). |
| **D - Deconstruct & Read** | Bóc tách cơ chế nhóm SubTotal, cách phối hợp Rows/Values trong Pivot, cơ chế tính toán của hàm DAX (`CALCULATE`, `SUMX`, `DIVIDE`) và Data Model (quan hệ 1-N giữa bảng Dimension và Fact). | Bóc tách ý nghĩa của Feature Engineering (tách ngày/tháng, gom cụm theo Store/Category), bản chất thuật toán cây quyết định Random Forest và cơ chế hồi quy. |
| **M - Mutate & Break** | Thử đổi ngưỡng tồn kho (50 vs 70), đổi hàm Aggregation (Sum vs Average), phát hiện bẫy lỗi định dạng text chứa ký tự `$` gây tính sai doanh thu. | Tinh chỉnh tham số `n_estimators`, `max_depth`; đánh giá hiện tượng Overfitting/Underfitting qua các chỉ số đo lường $R^2$, RMSE, MAE giữa tập Train và Test. |
| **V - Validate & Refine** | Kiểm tra độ hợp lý về mặt số liệu kinh doanh (Doanh thu = Sản lượng × Giá; Lợi nhuận gộp = Doanh thu − Giá vốn). | Đối chiếu dự báo nhu cầu tương lai với lượng tồn kho thực tế (`Stock_On_Hand`) để đưa ra khuyến nghị nhập/xả hàng; lập dàn ý chương báo cáo 30–40 trang. |

---

## 6. Quản Lý Lưu Trữ (Archive Management)

- Khi tệp `./nhật ký làm việc.md` vượt quá **30–50 phiên**, chủ động đề xuất lưu trữ các phiên cũ vào `./docs/history_worklog.md` và chỉ giữ lại 10 phiên gần nhất trong tệp chính để đảm bảo hiệu năng và tối ưu ngữ cảnh.
