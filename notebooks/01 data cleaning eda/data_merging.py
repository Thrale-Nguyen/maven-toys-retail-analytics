"""
Module: data_merging.py
Package: notebooks.01 data cleaning eda
Môn học: Năng lực số (HK3 - 2026)
Đề tài: Phân tích hiệu quả kinh doanh và ứng dụng Machine Learning trong dự báo nhu cầu bán hàng
        nhằm tối ưu tồn kho tại chuỗi bán lẻ Maven Toys
Nhóm sinh viên thực hiện:
    - Nguyễn Đỗ Tuấn Tú    - MSSV: 2521001112
    - Huỳnh Đức Phương Thảo - MSSV: 2521001097

Mô tả: Hợp nhất dữ liệu chuỗi bán lẻ đồ chơi Maven Toys theo mô hình Star Schema:
       1. Nạp và tiền xử lý chuẩn hóa 3 bảng dữ liệu gốc: sales.csv (Fact), products.csv (Dim), stores.csv (Dim).
       2. Làm sạch giá trị tiền tệ: loại bỏ ký tự '$' và khoảng trắng thừa trong Product_Cost & Product_Price.
       3. Thực hiện Left Join bảo toàn Grain giao dịch (Zero fan-out: đúng 829,262 dòng).
       4. Tính toán các chỉ số kinh doanh phái sinh: Doanh thu (Revenue), Giá vốn (Cost), Lợi nhuận gộp (Gross_Profit).
       5. Xuất tập dữ liệu hợp nhất hoàn chỉnh sang 'data/processed/maven_toy_sales.csv' (và định dạng tối ưu .parquet).
"""

import sys
from pathlib import Path
from typing import Optional, Tuple, Union
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

# Hằng số cấu hình dữ liệu
EXPECTED_SALES_ROWS = 829_262


def find_directories(
    custom_raw_dir: Optional[Union[str, Path]] = None,
    custom_processed_dir: Optional[Union[str, Path]] = None
) -> Tuple[Path, Path]:
    """
    Xác định đường dẫn thư mục dữ liệu gốc (raw) và thư mục lưu trữ đã xử lý (processed).
    Hỗ trợ linh hoạt chạy từ thư mục gốc đồ án hoặc từ bên trong thư mục con.
    """
    # 1. Tìm thư mục raw
    raw_dir: Optional[Path] = None
    if custom_raw_dir:
        p = Path(custom_raw_dir)
        if p.exists() and p.is_dir():
            raw_dir = p.resolve()

    if raw_dir is None:
        candidate_raw = [
            Path("data/raw/csv"),
            Path(__file__).resolve().parent.parent.parent / "data" / "raw" / "csv" if "__file__" in globals() else None,
            Path(__file__).resolve().parent.parent / "data" / "raw" / "csv" if "__file__" in globals() else None,
            Path("../data/raw/csv"),
            Path("../../data/raw/csv"),
        ]
        for c in candidate_raw:
            if c and c.exists() and c.is_dir():
                raw_dir = c.resolve()
                break

    if raw_dir is None:
        raise FileNotFoundError("Không tìm thấy thư mục 'data/raw/csv' chứa dữ liệu gốc.")

    # 2. Tìm thư mục processed
    proc_dir: Optional[Path] = None
    if custom_processed_dir:
        p = Path(custom_processed_dir)
        p.mkdir(parents=True, exist_ok=True)
        proc_dir = p.resolve()

    if proc_dir is None:
        candidate_proc = [
            Path("data/processed"),
            Path(__file__).resolve().parent.parent.parent / "data" / "processed" if "__file__" in globals() else None,
            Path(__file__).resolve().parent.parent / "data" / "processed" if "__file__" in globals() else None,
            Path("../data/processed"),
            Path("../../data/processed"),
        ]
        for c in candidate_proc:
            if c:
                c.mkdir(parents=True, exist_ok=True)
                proc_dir = c.resolve()
                break

    if proc_dir is None:
        proc_dir = (raw_dir.parent.parent / "processed").resolve()
        proc_dir.mkdir(parents=True, exist_ok=True)

    return raw_dir, proc_dir


def load_and_clean_dimension_tables(raw_dir: Path) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Nạp và tiền xử lý chuẩn hóa 2 bảng chiều (Dimension Tables): products và stores.
    Loại bỏ ký tự '$' và khoảng trắng thừa ở cột giá tiền.
    """
    products_path = raw_dir / "products.csv"
    stores_path = raw_dir / "stores.csv"

    if not products_path.exists():
        raise FileNotFoundError(f"Không tìm thấy tệp {products_path.name} tại: {products_path}")
    if not stores_path.exists():
        raise FileNotFoundError(f"Không tìm thấy tệp {stores_path.name} tại: {stores_path}")

    # Đọc bảng products
    df_prod = pd.read_csv(products_path)
    # Làm sạch ký tự '$' và chuyển đổi sang số thực float
    df_prod["Product_Cost"] = (
        df_prod["Product_Cost"]
        .astype(str)
        .str.replace("$", "", regex=False)
        .str.strip()
        .astype(float)
    )
    df_prod["Product_Price"] = (
        df_prod["Product_Price"]
        .astype(str)
        .str.replace("$", "", regex=False)
        .str.strip()
        .astype(float)
    )

    # Đọc bảng stores
    df_stores = pd.read_csv(stores_path)

    return df_prod, df_stores


def merge_maven_toy_sales(
    custom_raw_dir: Optional[Union[str, Path]] = None,
    custom_processed_dir: Optional[Union[str, Path]] = None,
    output_filename: str = "maven_toy_sales.csv",
    save_parquet: bool = True,
    verbose: bool = True
) -> pd.DataFrame:
    """
    Thực hiện ghép nối Star Schema giữa Fact Sales và các Dimension Tables.
    Tính toán các trường phái sinh Doanh thu, Chi phí, Lợi nhuận gộp và lưu ra file.
    """
    raw_dir, proc_dir = find_directories(custom_raw_dir, custom_processed_dir)

    if verbose:
        print("=" * 88)
        print("TIẾN TRÌNH HỢP NHẤT DỮ LIỆU BÁN HÀNG CHUỖI MAVEN TOYS (DATA MERGING PIPELINE)")
        print("=" * 88)
        print(f"• Thư mục dữ liệu gốc (Raw)       : {raw_dir}")
        print(f"• Thư mục dữ liệu sau xử lý (Proc): {proc_dir}")

    # 1. Nạp dữ liệu
    sales_path = raw_dir / "sales.csv"
    if not sales_path.exists():
        raise FileNotFoundError(f"Không tìm thấy tệp sales.csv tại: {sales_path}")

    if verbose:
        print("\n1. Đang nạp và làm sạch các bảng dữ liệu...")
    df_sales = pd.read_csv(sales_path)
    df_prod, df_stores = load_and_clean_dimension_tables(raw_dir)

    initial_sales_rows = len(df_sales)
    if verbose:
        print(f"   ✓ Fact Sales : {initial_sales_rows:,d} dòng × {df_sales.shape[1]} cột")
        print(f"   ✓ Dim Products: {len(df_prod):,d} sản phẩm (đã chuẩn hóa Product_Cost, Product_Price sang float)")
        print(f"   ✓ Dim Stores  : {len(df_stores):,d} cửa hàng")

    # 2. Thực hiện Left Join theo mô hình Star Schema
    if verbose:
        print("\n2. Đang thực hiện ghép nối theo mô hình Star Schema...")

    # Ghép bảng sales với products
    merged = df_sales.merge(
        df_prod[["Product_ID", "Product_Name", "Product_Category", "Product_Cost", "Product_Price"]],
        on="Product_ID",
        how="left"
    )

    # Ghép tiếp với stores
    merged = merged.merge(
        df_stores[["Store_ID", "Store_Name", "Store_City", "Store_Location", "Store_Open_Date"]],
        on="Store_ID",
        how="left"
    )

    # 3. Kiểm định bảo toàn grain (Zero fan-out) & kiểm tra nulls
    merged_rows = len(merged)
    if verbose:
        print("\n3. Kiểm tra tính toàn vẹn và bảo toàn Grain:")
        if merged_rows == initial_sales_rows:
            print(f"   ✓ BẢO TOÀN GRAIN HOÀN HẢO: Đúng {merged_rows:,d} dòng (Zero fan-out / 1 dòng = 1 giao dịch bán hàng)")
        else:
            print(f"   ✗ CẢNH BÁO: Số dòng thay đổi từ {initial_sales_rows:,d} -> {merged_rows:,d}")

        null_summary = merged.isnull().sum()
        total_nulls = null_summary.sum()
        if total_nulls == 0:
            print(f"   ✓ TOÀN VẸN THAM CHIẾU 100%: 0 giá trị Null xuất hiện sau khi ghép nối")
        else:
            print(f"   ✗ CẢNH BÁO NULL: Phát hiện {total_nulls} giá trị Null sau ghép nối!")

    # 4. Tính toán các chỉ số kinh doanh phái sinh
    if verbose:
        print("\n4. Đang tính toán các chỉ số kinh doanh phái sinh (Revenue, Cost, Gross_Profit)...")
    merged["Revenue"] = (merged["Units"] * merged["Product_Price"]).round(2)
    merged["Cost"] = (merged["Units"] * merged["Product_Cost"]).round(2)
    merged["Gross_Profit"] = (merged["Revenue"] - merged["Cost"]).round(2)

    # Sắp xếp lại thứ tự cột khoa học, dễ theo dõi
    final_columns = [
        "Sale_ID",
        "Date",
        "Store_ID",
        "Store_Name",
        "Store_City",
        "Store_Location",
        "Store_Open_Date",
        "Product_ID",
        "Product_Name",
        "Product_Category",
        "Product_Cost",
        "Product_Price",
        "Units",
        "Revenue",
        "Cost",
        "Gross_Profit",
    ]
    merged = merged[final_columns]

    # 5. Lưu kết quả ra file trong data/processed
    out_csv_path = proc_dir / output_filename
    if verbose:
        print(f"\n5. Đang xuất dữ liệu ra file '{out_csv_path.name}'...")

    merged.to_csv(out_csv_path, index=False, encoding="utf-8")
    file_size_mb = out_csv_path.stat().st_size / (1024 * 1024)
    if verbose:
        print(f"   ✓ Đã lưu thành công tệp CSV: {out_csv_path}")
        print(f"     - Kích thước tệp: {file_size_mb:.2f} MB")
        print(f"     - Số dòng       : {len(merged):,d} dòng")
        print(f"     - Số cột        : {len(final_columns)} cột")

    # Lưu thêm định dạng tối ưu Parquet nếu được yêu cầu (tiết kiệm dung lượng và tốc độ truy vấn cao)
    if save_parquet:
        out_parquet_path = proc_dir / f"{Path(output_filename).stem}.parquet"
        try:
            merged.to_parquet(out_parquet_path, index=False)
            pq_size_mb = out_parquet_path.stat().st_size / (1024 * 1024)
            if verbose:
                print(f"   ✓ Đã lưu tệp Parquet dự phòng: {out_parquet_path.name} ({pq_size_mb:.2f} MB)")
        except Exception as e:
            if verbose:
                print(f"   (Bỏ qua lưu parquet: {e})")

    # 6. Tổng kết số liệu kinh doanh chuẩn (Ground Truth)
    if verbose:
        print_business_kpis(merged)

    return merged


def print_business_kpis(df: pd.DataFrame) -> None:
    """In bảng tổng kết các chỉ số kinh doanh chính (KPIs) của tập dữ liệu sau hợp nhất."""
    total_units = int(df["Units"].sum())
    total_rev = float(df["Revenue"].sum())
    total_cost = float(df["Cost"].sum())
    total_profit = float(df["Gross_Profit"].sum())
    avg_margin = (total_profit / total_rev * 100) if total_rev > 0 else 0

    print("\n" + "=" * 88)
    print("TỔNG KẾT CHỈ SỐ KINH DOANH CHUẨN (GROUND TRUTH CHO EXCEL / POWER BI / ML):")
    print("-" * 88)
    print(f" • Khung thời gian giao dịch          : {df['Date'].min()} đến {df['Date'].max()} (21 tháng)")
    print(f" • Tổng số giao dịch ghi nhận (Rows)  : {len(df):,d} dòng")
    print(f" • Tổng sản lượng bán ra (Units)      : {total_units:,d} sản phẩm")
    print(f" • Tổng Doanh thu chuỗi (Revenue)     : ${total_rev:,.2f} USD")
    print(f" • Tổng Giá vốn hàng bán (COGS / Cost): ${total_cost:,.2f} USD")
    print(f" • Tổng Lợi nhuận gộp (Gross Profit)  : ${total_profit:,.2f} USD")
    print(f" • Tỷ suất Lợi nhuận gộp toàn chuỗi   : {avg_margin:.2f}%")
    print("=" * 88)


if __name__ == "__main__":
    merge_maven_toy_sales()
