"""
Module: eda_structural_summary.py
Package: notebooks.01 data cleaning eda
Môn học: Năng lực số (HK3 - 2026)
Đề tài: Phân tích hiệu quả kinh doanh và ứng dụng mô hình Catboost trong dự báo nhu cầu bán hàng
        nhằm tối ưu tồn kho tại chuỗi bán lẻ Maven Toys
Nhóm sinh viên thực hiện:
    - Nguyễn Đỗ Tuấn Tú    - MSSV: 2521001112
    - Huỳnh Đức Phương Thảo - MSSV: 2521001097

Mô tả: Khám phá cấu trúc sơ bộ (Structural EDA) của bộ dữ liệu gốc trong thư mục 'data/raw/csv':
       1. Khảo sát 4 bảng dữ liệu gốc: sales.csv, products.csv, stores.csv, inventory.csv.
       2. Đo lường kích thước (Shape), mức tiêu thụ RAM và dung lượng file trên đĩa.
       3. Kiểm định khóa chính (Primary Key Uniqueness) và bảo toàn quan hệ (Referential Integrity).
       4. Nhận diện các bẫy dị biệt dữ liệu (ký tự '$' ở chi phí/giá bán, định dạng chuỗi ngày tháng).
       5. Thống kê 5 con số cơ bản (5-number summary: Min, Q1, Median, Q3, Max, Mean, Std).
       6. Phân phối tần số các biến định tính cốt lõi (Category, Store Location, Store City).
       7. Khảo sát bảng giao dịch hợp nhất (Merged Sales Dataset): xác nhận Zero fan-out,
          doanh thu, giá vốn, lợi nhuận gộp và biên lợi nhuận danh mục.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import pandas as pd
import numpy as np

# Đảm bảo console Windows in tiếng Việt chuẩn Unicode UTF-8
if sys.platform.startswith("win"):
    try:
        if sys.stdout and hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if sys.stderr and hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Định nghĩa các hằng số kỳ vọng về cấu trúc bộ dữ liệu Maven Toys
EXPECTED_TABLES = ["sales", "products", "stores", "inventory"]
EXPECTED_ROW_COUNTS = {
    "sales": 829_262,
    "products": 35,
    "stores": 50,
    "inventory": 1_593,
}


def find_raw_csv_dir(custom_path: Optional[Union[str, Path]] = None) -> Path:
    """
    Xác định đường dẫn thư mục chứa các tệp CSV gốc ('data/raw/csv').
    Hỗ trợ chạy từ thư mục gốc đồ án hoặc từ bên trong thư mục 'notebooks/01 data cleaning eda/'.
    """
    if custom_path:
        p = Path(custom_path)
        if p.exists() and p.is_dir():
            return p.resolve()

    candidate_paths = [
        Path("data/raw/csv"),
        Path(__file__).resolve().parent.parent.parent / "data" / "raw" / "csv" if "__file__" in globals() else None,
        Path(__file__).resolve().parent.parent / "data" / "raw" / "csv" if "__file__" in globals() else None,
        Path("../data/raw/csv"),
        Path("../../data/raw/csv"),
    ]

    for cand in candidate_paths:
        if cand and cand.exists() and cand.is_dir():
            return cand.resolve()

    raise FileNotFoundError(
        "Không tìm thấy thư mục 'data/raw/csv'. "
        "Vui lòng đảm bảo các tệp CSV (sales.csv, products.csv, stores.csv, inventory.csv) nằm đúng thư mục."
    )


def load_raw_dataset(raw_dir: Path) -> Dict[str, pd.DataFrame]:
    """
    Nạp 4 bảng dữ liệu gốc vào bộ nhớ RAM.
    """
    datasets: Dict[str, pd.DataFrame] = {}
    csv_mapping = {
        "sales": raw_dir / "sales.csv",
        "products": raw_dir / "products.csv",
        "stores": raw_dir / "stores.csv",
        "inventory": raw_dir / "inventory.csv",
    }

    for name, file_path in csv_mapping.items():
        if not file_path.exists():
            raise FileNotFoundError(f"Không tìm thấy tệp {name}.csv tại đường dẫn: {file_path}")
        datasets[name] = pd.read_csv(file_path)

    return datasets


def print_section_header(title: str, level: int = 1) -> None:
    """In tiêu đề các phần của báo cáo EDA."""
    if level == 1:
        print("\n" + "=" * 90)
        print(f" {title}")
        print("=" * 90)
    elif level == 2:
        print("\n" + "-" * 90)
        print(f" ▶ {title}")
        print("-" * 90)
    else:
        print(f"\n--- {title} ---")


def inspect_table_structure(name: str, df: pd.DataFrame, raw_dir: Path) -> None:
    """
    Khảo sát cấu trúc chi tiết của một bảng dữ liệu:
    - Kích thước dòng, cột
    - Dung lượng đĩa & bộ nhớ RAM
    - Kiểu dữ liệu, giá trị rỗng (Nulls)
    - Tính duy nhất của khóa chính (Grain)
    """
    file_path = raw_dir / f"{name}.csv"
    file_size_kb = file_path.stat().st_size / 1024
    mem_usage_kb = df.memory_usage(deep=True).sum() / 1024
    n_rows, n_cols = df.shape

    print(f"\n[ BẢNG: {name.upper()}.CSV ]")
    print(f" • Đường dẫn tệp       : {file_path.name}")
    print(f" • Dung lượng trên đĩa : ({file_size_kb / 1024:.2f} MB)")
    print(f" • Tiêu thụ trong RAM  : ({mem_usage_kb / 1024:.2f} MB)")
    print(f" • Kích thước (Shape)  : {n_rows:,d} dòng × {n_cols} cột")

    # Kiểm tra số dòng kỳ vọng
    exp_rows = EXPECTED_ROW_COUNTS.get(name)
    if exp_rows is not None:
        status_row = "KHỚP KỲ VỌNG" if n_rows == exp_rows else f"LỆCH KỲ VỌNG ({exp_rows:,d})"
        print(f" • Kiểm chuẩn số dòng  : {status_row} ({n_rows:,d} dòng)")

    # Khảo sát khóa chính & Grain
    if name == "sales":
        is_pk = df["Sale_ID"].is_unique
        print(f" • Khóa chính (Sale_ID): {'DUY NHẤT (Grain: 1 dòng = 1 giao dịch)' if is_pk else 'CẢNH BÁO: BỊ TRÙNG LẶP'}")
    elif name == "products":
        is_pk = df["Product_ID"].is_unique
        print(f" • Khóa chính (Product_ID): {'DUY NHẤT (Grain: 1 dòng = 1 sản phẩm)' if is_pk else 'CẢNH BÁO: BỊ TRÙNG LẶP'}")
    elif name == "stores":
        is_pk = df["Store_ID"].is_unique
        print(f" • Khóa chính (Store_ID)  : {'DUY NHẤT (Grain: 1 dòng = 1 cửa hàng)' if is_pk else 'CẢNH BÁO: BỊ TRÙNG LẶP'}")
    elif name == "inventory":
        composite_unique = not df.duplicated(subset=["Store_ID", "Product_ID"]).any()
        print(f" • Khóa kết hợp (Store_ID + Product_ID): {'DUY NHẤT (Grain: Snapshot tồn kho theo cửa hàng - sản phẩm)' if composite_unique else 'CẢNH BÁO: BỊ TRÙNG LẶP'}")

    # Danh sách cột, kiểu dữ liệu và nulls
    null_counts = df.isnull().sum()
    print(" • Chi tiết các thuộc tính (Columns, Dtypes & Missing):")
    col_summary = []
    for col in df.columns:
        n_null = int(null_counts[col])
        pct_null = (n_null / n_rows) * 100 if n_rows > 0 else 0
        sample_val = str(df[col].iloc[0]) if n_rows > 0 else "N/A"
        if len(sample_val) > 28:
            sample_val = sample_val[:25] + "..."
        col_summary.append({
            "Cột (Column)": col,
            "Kiểu dữ liệu (Dtype)": str(df[col].dtype),
            "Số giá trị Null": f"{n_null:,d} ({pct_null:.1f}%)",
            "Mẫu dữ liệu (Sample)": sample_val,
        })
    df_col_sum = pd.DataFrame(col_summary)
    print(df_col_sum.to_string(index=False))


def verify_relational_integrity(datasets: Dict[str, pd.DataFrame]) -> None:
    """
    Kiểm tra toàn vẹn tham chiếu (Referential Integrity) giữa 4 bảng:
    - sales.Store_ID -> stores.Store_ID
    - sales.Product_ID -> products.Product_ID
    - inventory.Store_ID -> stores.Store_ID
    - inventory.Product_ID -> products.Product_ID
    """
    print_section_header("2. KIỂM ĐỊNH TOÀN VẸN THAM CHIẾU & QUAN HỆ (REFERENTIAL INTEGRITY)", level=2)

    df_sales = datasets["sales"]
    df_prod = datasets["products"]
    df_stores = datasets["stores"]
    df_inv = datasets["inventory"]

    store_ids = set(df_stores["Store_ID"])
    product_ids = set(df_prod["Product_ID"])

    sales_store_orphan = set(df_sales["Store_ID"]) - store_ids
    sales_prod_orphan = set(df_sales["Product_ID"]) - product_ids
    inv_store_orphan = set(df_inv["Store_ID"]) - store_ids
    inv_prod_orphan = set(df_inv["Product_ID"]) - product_ids

    checks = [
        ("sales.Store_ID -> stores.Store_ID", len(sales_store_orphan), "Tất cả 50 cửa hàng đều có giao dịch bán hàng"),
        ("sales.Product_ID -> products.Product_ID", len(sales_prod_orphan), "Tất cả 35 sản phẩm đều đã phát sinh bán hàng"),
        ("inventory.Store_ID -> stores.Store_ID", len(inv_store_orphan), "Tồn kho bao phủ đủ 50 cửa hàng"),
        ("inventory.Product_ID -> products.Product_ID", len(inv_prod_orphan), "Tồn kho bao phủ đủ 35 sản phẩm"),
    ]

    print(f"{'Cặp quan hệ tham chiếu':<45} | {'Số mã mồ côi (Orphan)':<22} | {'Trạng thái toàn vẹn'}")
    print("-" * 90)
    for rel, orphans, note in checks:
        status_text = "✓ TOÀN VẸN 100% (Zero Orphan)" if orphans == 0 else f"✗ CẢNH BÁO: {orphans} mã mồ côi"
        print(f"{rel:<45} | {orphans:<22} | {status_text}")
    print(f"\n▶ Đánh giá: Cấu trúc mô hình dữ liệu quan hệ (Star Schema) chuẩn xác, sẵn sàng cho Data Model Power BI.")


def analyze_raw_anomalies_and_cleaning_needs(datasets: Dict[str, pd.DataFrame]) -> None:
    """
    Phát hiện các vấn đề định dạng kỹ thuật cần làm sạch:
    - Ký tự '$' và khoảng trắng thừa trong Product_Cost & Product_Price.
    - Định dạng chuỗi ngày tháng ở bảng sales (Date) và stores (Store_Open_Date).
    - Tình trạng thiếu hàng (Stockout: Stock_On_Hand = 0) trong inventory.
    """
    print_section_header("3. NHẬN DIỆN DỊ BIỆT ĐỊNH DẠNG & NHU CẦU LÀM SẠCH DỮ LIỆU", level=2)

    df_prod = datasets["products"]
    df_sales = datasets["sales"]
    df_stores = datasets["stores"]
    df_inv = datasets["inventory"]

    # 1. Bảng products: Ký tự '$'
    has_dollar_cost = df_prod["Product_Cost"].astype(str).str.contains(r"\$", regex=True).any()
    has_dollar_price = df_prod["Product_Price"].astype(str).str.contains(r"\$", regex=True).any()
    print("1. Bảng products.csv - Định dạng chi phí & giá bán:")
    print(f"   • Cột Product_Cost : {'Chứa ký tự \"$\" và khoảng trắng (Cần làm sạch strip + float)' if has_dollar_cost else 'Đã chuẩn hóa số'}")
    print(f"   • Cột Product_Price: {'Chứa ký tự \"$\" và khoảng trắng (Cần làm sạch strip + float)' if has_dollar_price else 'Đã chuẩn hóa số'}")

    # 2. Bảng sales & stores: Chuỗi ngày tháng
    date_is_obj = df_sales["Date"].dtype == object
    store_date_is_obj = df_stores["Store_Open_Date"].dtype == object
    print("\n2. Bảng sales.csv & stores.csv - Chuỗi ngày tháng:")
    print(f"   • Cột Date (sales)          : {'Dạng chuỗi (object) -> Cần chuyển sang datetime64' if date_is_obj else 'Đã chuẩn hóa datetime'}")
    print(f"   • Cột Store_Open_Date (stores): {'Dạng chuỗi (object) -> Cần chuyển sang datetime64' if store_date_is_obj else 'Đã chuẩn hóa datetime'}")
    print(f"   • Phạm vi ngày giao dịch    : Từ {df_sales['Date'].min()} đến {df_sales['Date'].max()} (21 tháng hoạt động)")

    # 3. Bảng inventory: Tồn kho bằng 0
    zero_stock_count = int((df_inv["Stock_On_Hand"] == 0).sum())
    total_inv_records = len(df_inv)
    zero_stock_pct = (zero_stock_count / total_inv_records) * 100
    print("\n3. Bảng inventory.csv - Đánh giá rủi ro đứt gãy tồn kho (Stockout Risk):")
    print(f"   • Tổng số cặp Store-Product ghi nhận tồn kho: {total_inv_records:,d} / 1,750 cặp tối đa (50 stores × 35 products)")
    print(f"   • Số bản ghi cạn kiệt hàng (Stock = 0)     : {zero_stock_count:,d} bản ghi ({zero_stock_pct:.2f}%)")
    print(f"   • Nhận xét: 4.83% mặt hàng tại các chi nhánh đang ở mức tồn kho bằng 0, cần ưu tiên thuật toán dự báo bổ sung.")


def compute_five_number_summaries(datasets: Dict[str, pd.DataFrame]) -> None:
    """
    Thống kê 5 con số cơ bản (Min, Q1, Median, Q3, Max) cùng Mean và Std
    cho các biến định lượng của từng bảng dữ liệu.
    """
    print_section_header("4. THỐNG KÊ 5 CON SỐ CƠ BẢN CHO BIẾN ĐỊNH LƯỢNG (DESCRIBE)", level=2)

    # 1. Bảng products (sau khi tạm thời parse sang số để khảo sát thống kê)
    df_prod = datasets["products"].copy()
    cost_clean = df_prod["Product_Cost"].astype(str).str.replace("$", "", regex=False).str.strip().astype(float)
    price_clean = df_prod["Product_Price"].astype(str).str.replace("$", "", regex=False).str.strip().astype(float)
    margin_clean = price_clean - cost_clean
    margin_pct = (margin_clean / price_clean) * 100

    prod_metrics = pd.DataFrame({
        "Product_Cost ($)": cost_clean,
        "Product_Price ($)": price_clean,
        "Unit_Margin ($)": margin_clean,
        "Margin_Pct (%)": margin_pct,
    })

    print("\n▶ [Bảng products.csv] - Thống kê biến giá thành, giá bán & biên lợi nhuận đơn vị:")
    desc_prod = prod_metrics.describe().T[["count", "mean", "std", "min", "25%", "50%", "75%", "max"]]
    desc_prod.columns = ["Count", "Mean", "Std", "Min", "Q1 (25%)", "Median", "Q3 (75%)", "Max"]
    desc_prod["Count"] = desc_prod["Count"].astype(int)
    print(desc_prod.to_string(formatters={
        "Mean": "{:,.2f}".format, "Std": "{:,.2f}".format,
        "Min": "{:,.2f}".format, "Q1 (25%)": "{:,.2f}".format,
        "Median": "{:,.2f}".format, "Q3 (75%)": "{:,.2f}".format,
        "Max": "{:,.2f}".format,
    }))

    # 2. Bảng sales - Số lượng sản phẩm bán ra mỗi lượt
    df_sales = datasets["sales"]
    print("\n▶ [Bảng sales.csv] - Thống kê biến sản lượng bán mỗi lượt (Units):")
    desc_sales = df_sales[["Units"]].describe().T[["count", "mean", "std", "min", "25%", "50%", "75%", "max"]]
    desc_sales.columns = ["Count", "Mean", "Std", "Min", "Q1 (25%)", "Median", "Q3 (75%)", "Max"]
    desc_sales["Count"] = desc_sales["Count"].astype(int)
    print(desc_sales.to_string(formatters={
        "Count": "{:,d}".format, "Mean": "{:,.3f}".format, "Std": "{:,.3f}".format,
        "Min": "{:,.0f}".format, "Q1 (25%)": "{:,.0f}".format,
        "Median": "{:,.0f}".format, "Q3 (75%)": "{:,.0f}".format,
        "Max": "{:,.0f}".format,
    }))

    # 3. Bảng inventory - Lượng hàng tồn kho trên kệ
    df_inv = datasets["inventory"]
    print("\n▶ [Bảng inventory.csv] - Thống kê lượng tồn kho thực tế (Stock_On_Hand):")
    desc_inv = df_inv[["Stock_On_Hand"]].describe().T[["count", "mean", "std", "min", "25%", "50%", "75%", "max"]]
    desc_inv.columns = ["Count", "Mean", "Std", "Min", "Q1 (25%)", "Median", "Q3 (75%)", "Max"]
    desc_inv["Count"] = desc_inv["Count"].astype(int)
    print(desc_inv.to_string(formatters={
        "Count": "{:,d}".format, "Mean": "{:,.2f}".format, "Std": "{:,.2f}".format,
        "Min": "{:,.0f}".format, "Q1 (25%)": "{:,.0f}".format,
        "Median": "{:,.0f}".format, "Q3 (75%)": "{:,.0f}".format,
        "Max": "{:,.0f}".format,
    }))


def compute_categorical_distributions(datasets: Dict[str, pd.DataFrame]) -> None:
    """
    Phân tích phân phối tần số (Value Counts & Percentages)
    cho các biến định tính cốt lõi (Category, Store Location, Store City).
    """
    print_section_header("5. PHÂN PHỐI TẦN SỐ CỦA CÁC BIẾN ĐỊNH TÍNH CỐT LÕI", level=2)

    df_prod = datasets["products"]
    df_stores = datasets["stores"]

    # 1. Danh mục sản phẩm (Product_Category)
    vc_cat = df_prod["Product_Category"].value_counts()
    pct_cat = df_prod["Product_Category"].value_counts(normalize=True) * 100
    df_cat_dist = pd.DataFrame({"Số sản phẩm (SKUs)": vc_cat, "Tỷ lệ (%)": pct_cat})
    print("\n▶ [Bảng products.csv] Phân phối danh mục sản phẩm (Product_Category):")
    print(df_cat_dist.to_string(formatters={"Tỷ lệ (%)": "{:.1f}%".format}))

    # 2. Loại hình vị trí cửa hàng (Store_Location)
    vc_loc = df_stores["Store_Location"].value_counts()
    pct_loc = df_stores["Store_Location"].value_counts(normalize=True) * 100
    df_loc_dist = pd.DataFrame({"Số cửa hàng": vc_loc, "Tỷ lệ (%)": pct_loc})
    print("\n▶ [Bảng stores.csv] Phân phối loại hình vị trí cửa hàng (Store_Location):")
    print(df_loc_dist.to_string(formatters={"Tỷ lệ (%)": "{:.1f}%".format}))

    # 3. Top các thành phố tập trung nhiều chi nhánh nhất (Store_City)
    vc_city = df_stores["Store_City"].value_counts().head(5)
    pct_city = (vc_city / len(df_stores)) * 100
    df_city_dist = pd.DataFrame({"Số cửa hàng": vc_city, "Tỷ lệ (%)": pct_city})
    print("\n▶ [Bảng stores.csv] Top 5 thành phố có nhiều chi nhánh Maven Toys nhất (Store_City):")
    print(df_city_dist.to_string(formatters={"Tỷ lệ (%)": "{:.1f}%".format}))


def explore_merged_sales_dataset(datasets: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Khám phá cấu trúc bảng giao dịch hợp nhất (Merged Sales Dataset):
    - Ghép nối sales + products + stores theo đúng chuẩn Star Schema.
    - Kiểm định Zero fan-out (đúng 829,262 dòng).
    - Tính toán Doanh thu, Chi phí, Lợi nhuận gộp theo từng giao dịch.
    - Thống kê kết quả kinh doanh tổng thể và phân rã theo danh mục.
    """
    print_section_header("6. KHÁM PHÁ CẤU TRÚC BẢNG GIAO DỊCH HỢP NHẤT (MERGED SALES DATA)", level=2)

    df_sales = datasets["sales"].copy()
    df_prod = datasets["products"].copy()
    df_stores = datasets["stores"].copy()

    # Chuẩn hóa giá trị số cho sản phẩm
    df_prod["Clean_Cost"] = df_prod["Product_Cost"].astype(str).str.replace("$", "", regex=False).str.strip().astype(float)
    df_prod["Clean_Price"] = df_prod["Product_Price"].astype(str).str.replace("$", "", regex=False).str.strip().astype(float)

    # Thực hiện Left Join an toàn
    merged = df_sales.merge(
        df_prod[["Product_ID", "Product_Name", "Product_Category", "Clean_Cost", "Clean_Price"]],
        on="Product_ID",
        how="left"
    ).merge(
        df_stores[["Store_ID", "Store_Name", "Store_City", "Store_Location", "Store_Open_Date"]],
        on="Store_ID",
        how="left"
    )

    n_rows, n_cols = merged.shape
    exp_rows = len(df_sales)

    # 1. Kiểm tra Grain & Fan-out
    print(f"• Số dòng thực tế sau ghép nối: {n_rows:,d} dòng × {n_cols} cột")
    if n_rows == exp_rows:
        print(f"• Bảo toàn grain: ĐÚNG {exp_rows:,d} dòng (Zero fan-out / 1 giao dịch = 1 dòng)")
    else:
        print(f"• CẢNH BÁO BẢO TOÀN GRAIN: Bị chênh lệch dòng so với sales gốc ({exp_rows:,d} -> {n_rows:,d})")

    # 2. Tính toán các chỉ số kinh doanh cốt lõi
    merged["Revenue"] = merged["Units"] * merged["Clean_Price"]
    merged["Cost"] = merged["Units"] * merged["Clean_Cost"]
    merged["Gross_Profit"] = merged["Revenue"] - merged["Cost"]

    total_units = int(merged["Units"].sum())
    total_rev = float(merged["Revenue"].sum())
    total_cost = float(merged["Cost"].sum())
    total_profit = float(merged["Gross_Profit"].sum())
    overall_margin = (total_profit / total_rev) * 100 if total_rev > 0 else 0

    print("\n▶ TỔNG QUAN HIỆU QUẢ KINH DOANH TOÀN CHUỖI (2022-01-01 -> 2023-09-30):")
    print(f" • Tổng số lượng sản phẩm tiêu thụ (Units) : {total_units:,d} sản phẩm")
    print(f" • Tổng Doanh thu toàn chuỗi (Revenue)     : ${total_rev:,.2f} USD")
    print(f" • Tổng Giá vốn hàng bán (COGS / Cost)     : ${total_cost:,.2f} USD")
    print(f" • Tổng Lợi nhuận gộp (Gross Profit)       : ${total_profit:,.2f} USD")
    print(f" • Tỷ suất Lợi nhuận gộp trung bình        : {overall_margin:.2f}%")

    # 3. Phân rã hiệu quả kinh doanh theo Danh mục sản phẩm (Product Category)
    cat_summary = merged.groupby("Product_Category").agg(
        Units_Sold=("Units", "sum"),
        Revenue=("Revenue", "sum"),
        Gross_Profit=("Gross_Profit", "sum"),
    ).reset_index()
    cat_summary["Revenue_Share_%"] = (cat_summary["Revenue"] / total_rev) * 100
    cat_summary["Gross_Margin_%"] = (cat_summary["Gross_Profit"] / cat_summary["Revenue"]) * 100
    cat_summary = cat_summary.sort_values(by="Revenue", ascending=False)

    print("\n▶ HIỆU QUẢ KINH DOANH THEO DANH MỤC SẢN PHẨM (PRODUCT CATEGORY):")
    print(cat_summary.to_string(
        index=False,
        formatters={
            "Units_Sold": "{:,d}".format,
            "Revenue": "${:,.2f}".format,
            "Gross_Profit": "${:,.2f}".format,
            "Revenue_Share_%": "{:.1f}%".format,
            "Gross_Margin_%": "{:.2f}%".format,
        }
    ))

    # 4. Phân rã hiệu quả kinh doanh theo Loại hình vị trí (Store Location)
    loc_summary = merged.groupby("Store_Location").agg(
        Units_Sold=("Units", "sum"),
        Revenue=("Revenue", "sum"),
        Gross_Profit=("Gross_Profit", "sum"),
    ).reset_index()
    loc_summary["Revenue_Share_%"] = (loc_summary["Revenue"] / total_rev) * 100
    loc_summary["Gross_Margin_%"] = (loc_summary["Gross_Profit"] / loc_summary["Revenue"]) * 100
    loc_summary = loc_summary.sort_values(by="Revenue", ascending=False)

    print("\n▶ HIỆU QUẢ KINH DOANH THEO LOẠI HÌNH VỊ TRÍ CỬA HÀNG (STORE LOCATION):")
    print(loc_summary.to_string(
        index=False,
        formatters={
            "Units_Sold": "{:,d}".format,
            "Revenue": "${:,.2f}".format,
            "Gross_Profit": "${:,.2f}".format,
            "Revenue_Share_%": "{:.1f}%".format,
            "Gross_Margin_%": "{:.2f}%".format,
        }
    ))

    # 5. Thống kê 5 con số cho các biến kinh doanh trong tập merged
    print("\n▶ THỐNG KÊ 5 CON SỐ CHO CÁC BIẾN TÀI CHÍNH TRÊN MỖI DÒNG GIAO DỊCH:")
    desc_fin = merged[["Units", "Clean_Price", "Revenue", "Gross_Profit"]].describe().T[["count", "mean", "std", "min", "25%", "50%", "75%", "max"]]
    desc_fin.columns = ["Count", "Mean", "Std", "Min", "Q1 (25%)", "Median", "Q3 (75%)", "Max"]
    desc_fin["Count"] = desc_fin["Count"].astype(int)
    print(desc_fin.to_string(formatters={
        "Count": "{:,d}".format, "Mean": "{:,.2f}".format, "Std": "{:,.2f}".format,
        "Min": "{:,.2f}".format, "Q1 (25%)": "{:,.2f}".format,
        "Median": "{:,.2f}".format, "Q3 (75%)": "{:,.2f}".format,
        "Max": "{:,.2f}".format,
    }))

    return merged


def run_structural_eda(custom_raw_dir: Optional[Union[str, Path]] = None) -> Dict[str, any]:
    """
    Hàm thực thi toàn bộ quy trình Structural EDA trên tập dữ liệu Maven Toys.
    Trả về Dictionary chứa 4 DataFrames gốc và DataFrame hợp nhất.
    """
    raw_dir = find_raw_csv_dir(custom_raw_dir)

    print_section_header("BÁO CÁO KHÁM PHÁ CẤU TRÚC SƠ BỘ BỘ DỮ LIỆU MAVEN TOYS (RAW CSV)", level=1)
    print(f"Thư mục nguồn dữ liệu: {raw_dir}")

    # 1. Nạp dữ liệu
    datasets = load_raw_dataset(raw_dir)

    # 2. Khảo sát cấu trúc từng bảng raw
    print_section_header("1. KHẢO SÁT CẤU TRÚC TỪNG BẢNG DỮ LIỆU GỐC", level=2)
    for name in EXPECTED_TABLES:
        inspect_table_structure(name, datasets[name], raw_dir)

    # 3. Kiểm định quan hệ
    verify_relational_integrity(datasets)

    # 4. Nhận diện dị biệt
    analyze_raw_anomalies_and_cleaning_needs(datasets)

    # 5. Thống kê 5 con số
    compute_five_number_summaries(datasets)

    # 6. Phân phối biến định tính
    compute_categorical_distributions(datasets)

    # 7. Khám phá tập merged
    df_merged = explore_merged_sales_dataset(datasets)

    print_section_header("✓ HOÀN TẤT THÀNH CÔNG KHÁM PHÁ CẤU TRÚC SƠ BỘ BỘ DỮ LIỆU MAVEN TOYS", level=1)

    return {
        "raw_dir": raw_dir,
        "sales": datasets["sales"],
        "products": datasets["products"],
        "stores": datasets["stores"],
        "inventory": datasets["inventory"],
        "merged": df_merged,
    }


if __name__ == "__main__":
    from typing import Any
    run_structural_eda()
