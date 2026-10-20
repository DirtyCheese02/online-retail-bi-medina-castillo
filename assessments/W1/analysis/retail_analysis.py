"""Reproducible first inspection of the UCI Online Retail case.

All outputs describe recorded lines and invoices. They are not profit, demand,
or a matched probability that a particular purchase was cancelled.
"""

from pathlib import Path
import hashlib
import json
import math
import re

import matplotlib.pyplot as plt
import pandas as pd


START = pd.Timestamp("2010-12-01")
END = pd.Timestamp("2011-12-01")
MERCHANDISE = re.compile(r"^\d{5}[A-Z]?$")
OFFICIAL_SOURCE_SHA256 = "43465a06f2ccf7c8b5bd2892bc7defb52f97487934fe93b16ae4c3936424676d"
COLUMNS = ["InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate", "UnitPrice", "CustomerID", "Country"]


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def extract_case(source_xlsx, output_csv, manifest_path):
    source_xlsx = Path(source_xlsx)
    output_csv = Path(output_csv)
    manifest_path = Path(manifest_path)
    df = pd.read_excel(source_xlsx, dtype={"InvoiceNo": str, "StockCode": str, "CustomerID": "Int64"})
    if list(df.columns) != COLUMNS or len(df) != 541909:
        raise ValueError("Source workbook does not match the verified UCI Online Retail layout")
    case = df.loc[df.InvoiceDate.ge(START) & df.InvoiceDate.lt(END), COLUMNS].copy()
    case["InvoiceDate"] = case.InvoiceDate.dt.strftime("%Y-%m-%d %H:%M:%S")
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    case.to_csv(output_csv, index=False)
    source_hash = sha256(source_xlsx)
    manifest = {
        "source_title": "Online Retail",
        "source_url": "https://archive.ics.uci.edu/dataset/352/online+retail",
        "source_doi": "10.24432/C5BW33",
        "license": "CC BY 4.0",
        "source_filename": source_xlsx.name,
        "source_sha256": source_hash,
        "matches_uci_download_checked_2026_09_25": source_hash == OFFICIAL_SOURCE_SHA256,
        "source_rows": len(df),
        "extract_rows": len(case),
        "filter": "2010-12-01 <= InvoiceDate < 2011-12-01; all eight source columns and all matching rows retained",
        "extract_sha256": sha256(output_csv),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def load_case(path):
    df = pd.read_csv(path, dtype={"InvoiceNo": str, "StockCode": str, "CustomerID": "Int64"}, parse_dates=["InvoiceDate"])
    if list(df.columns) != COLUMNS:
        raise ValueError("Unexpected input columns")
    if not (df.InvoiceDate.ge(START) & df.InvoiceDate.lt(END)).all():
        raise ValueError("Input contains dates outside the documented case")
    return df


def inspect(df):
    invoice = df.InvoiceNo.astype(str)
    merch = df.StockCode.astype(str).str.fullmatch(MERCHANDISE.pattern)
    is_cancel = invoice.str.startswith("C")
    return {
        "rows": len(df),
        "min_date": str(df.InvoiceDate.min()),
        "max_date": str(df.InvoiceDate.max()),
        "invoices": int(df.InvoiceNo.nunique()),
        "countries": int(df.Country.nunique()),
        "stock_codes": int(df.StockCode.nunique()),
        "missing_customer_id": int(df.CustomerID.isna().sum()),
        "missing_description": int(df.Description.isna().sum()),
        "exact_duplicate_rows": int(df.duplicated().sum()),
        "zero_or_negative_price": int(df.UnitPrice.le(0).sum()),
        "zero_price_rows": int(df.UnitPrice.eq(0).sum()),
        "negative_price_rows": int(df.UnitPrice.lt(0).sum()),
        "non_merchandise_code_rows": int((~merch).sum()),
        "cancel_prefix_rows": int(is_cancel.sum()),
        "negative_quantity_rows": int(df.Quantity.lt(0).sum()),
        "cancel_prefix_nonnegative_quantity": int((is_cancel & df.Quantity.ge(0)).sum()),
        "negative_quantity_without_cancel_prefix": int((~is_cancel & df.Quantity.lt(0)).sum()),
    }


def analyze(df):
    d = df.copy()
    d["month"] = d.InvoiceDate.dt.strftime("%Y-%m")
    d["merchandise"] = d.StockCode.astype(str).str.fullmatch(MERCHANDISE.pattern)
    d["is_cancel"] = d.InvoiceNo.astype(str).str.startswith("C")
    sales = d.loc[d.merchandise & ~d.is_cancel & d.Quantity.gt(0) & d.UnitPrice.gt(0)].copy()
    sales["line_value_gbp"] = sales.Quantity * sales.UnitPrice
    cancels = d.loc[d.merchandise & d.is_cancel & d.Quantity.lt(0) & d.UnitPrice.gt(0)].copy()

    monthly_sales = (sales.groupby("month").agg(lines=("InvoiceNo", "size"), invoices=("InvoiceNo", "nunique"),
                    units=("Quantity", "sum"), observed_value_gbp=("line_value_gbp", "sum"))
                    .reset_index())
    monthly_cancel = (pd.DataFrame({"month": sorted(d.month.unique())})
                      .merge(sales.groupby("month").agg(purchase_lines=("InvoiceNo", "size"), purchase_invoices=("InvoiceNo", "nunique")).reset_index(), on="month", how="left")
                      .merge(cancels.groupby("month").agg(cancel_lines=("InvoiceNo", "size"), cancel_invoices=("InvoiceNo", "nunique"), cancel_units=("Quantity", lambda s: -s.sum())).reset_index(), on="month", how="left")
                      .fillna(0))
    monthly_cancel["cancel_invoice_share_pct"] = 100 * monthly_cancel.cancel_invoices / (monthly_cancel.purchase_invoices + monthly_cancel.cancel_invoices)
    monthly_cancel["cancel_line_share_pct"] = 100 * monthly_cancel.cancel_lines / (monthly_cancel.purchase_lines + monthly_cancel.cancel_lines)

    product = sales.groupby("StockCode").agg(lines=("InvoiceNo", "size"), observed_value_gbp=("line_value_gbp", "sum")).sort_values("observed_value_gbp", ascending=False).head(10).reset_index()
    names = sales.dropna(subset=["Description"]).groupby("StockCode").Description.agg(lambda x: x.value_counts().index[0])
    product.insert(1, "description", product.StockCode.map(names))

    known = sales.loc[sales.CustomerID.notna()].copy()
    customers = (known.groupby("CustomerID").agg(
        observed_value_gbp=("line_value_gbp", "sum"),
        invoices=("InvoiceNo", "nunique"),
        lines=("InvoiceNo", "size"),
    ).sort_values("observed_value_gbp", ascending=False).reset_index())
    customers.insert(0, "rank", range(1, len(customers) + 1))
    customers["cumulative_value_share_pct"] = 100 * customers.observed_value_gbp.cumsum() / customers.observed_value_gbp.sum()

    country_sales = sales.groupby("Country").agg(purchase_lines=("InvoiceNo", "size"), observed_value_gbp=("line_value_gbp", "sum")).sort_values("purchase_lines", ascending=False)
    country_cancels = cancels.groupby("Country").agg(cancel_lines=("InvoiceNo", "size"))
    countries = country_sales.join(country_cancels, how="left").fillna(0)
    countries["cancel_line_share_pct"] = 100 * countries.cancel_lines / (countries.purchase_lines + countries.cancel_lines)
    countries = countries.reset_index()

    info = inspect(df)
    dedup_value = float(sales.drop_duplicates(subset=COLUMNS).line_value_gbp.sum())
    info.update({
        "purchase_lines": len(sales),
        "cancel_lines_eligible": len(cancels),
        "purchase_invoices": int(sales.InvoiceNo.nunique()),
        "cancel_invoices_eligible": int(cancels.InvoiceNo.nunique()),
        "purchase_line_value_gbp": float(sales.line_value_gbp.sum()),
        "purchase_line_value_if_exact_duplicates_removed_gbp": dedup_value,
        "exact_duplicate_value_difference_pct": float(100 * (sales.line_value_gbp.sum() - dedup_value) / sales.line_value_gbp.sum()),
        "top_10_stockcode_value_share_pct": float(100 * product.observed_value_gbp.sum() / sales.line_value_gbp.sum()),
        "uk_purchase_value_share_pct": float(100 * country_sales.loc["United Kingdom", "observed_value_gbp"] / sales.line_value_gbp.sum()),
        "known_customer_id_purchase_lines": int(sales.CustomerID.notna().sum()),
        "missing_customer_id_purchase_lines": int(sales.CustomerID.isna().sum()),
        "known_customer_id_purchase_value_gbp": float(known.line_value_gbp.sum()),
        "known_customer_id_value_share_pct": float(100 * known.line_value_gbp.sum() / sales.line_value_gbp.sum()),
        "known_customers": len(customers),
        "top_1pct_customer_count": math.ceil(len(customers) * .01),
        "top_1pct_customer_value_share_pct": float(100 * customers.head(math.ceil(len(customers) * .01)).observed_value_gbp.sum() / known.line_value_gbp.sum()),
        "top_10pct_customer_count": math.ceil(len(customers) * .10),
        "top_10pct_customer_value_share_pct": float(100 * customers.head(math.ceil(len(customers) * .10)).observed_value_gbp.sum() / known.line_value_gbp.sum()),
        "one_invoice_customers": int(customers.invoices.eq(1).sum()),
        "one_invoice_customer_value_share_pct": float(100 * customers.loc[customers.invoices.eq(1), "observed_value_gbp"].sum() / known.line_value_gbp.sum()),
    })
    return info, monthly_sales, monthly_cancel, product, countries, customers


def write_outputs(df, data_dir, figure_dir):
    data_dir, figure_dir = Path(data_dir), Path(figure_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    figure_dir.mkdir(parents=True, exist_ok=True)
    info, sales, cancel, product, countries, customers = analyze(df)
    (data_dir / "case_checks.json").write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")
    for name, table in [("monthly_purchase_value.csv", sales), ("monthly_cancellations.csv", cancel),
                        ("top_products.csv", product), ("country_comparison.csv", countries),
                        ("customer_concentration.csv", customers)]:
        table.to_csv(data_dir / name, index=False)

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    ax.plot(sales.month, sales.observed_value_gbp / 1e6, marker="o", color="#164863", linewidth=2)
    ax.set_ylabel("Observed purchase-line value (£m)")
    ax.set_xlabel("Month")
    ax.tick_params(axis="x", labelrotation=45)
    ax.grid(axis="y", alpha=.2)
    fig.tight_layout()
    fig.savefig(figure_dir / "monthly_purchase_value.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    ax.bar(cancel.month, cancel.cancel_invoice_share_pct, color="#a75d42")
    ax.set_ylabel("Cancellation-invoice share (%)")
    ax.set_xlabel("Month")
    ax.tick_params(axis="x", labelrotation=45)
    ax.set_ylim(0, max(cancel.cancel_invoice_share_pct) * 1.25)
    ax.grid(axis="y", alpha=.2)
    fig.tight_layout()
    fig.savefig(figure_dir / "monthly_cancellation_share.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    x = 100 * customers["rank"] / len(customers)
    ax.plot(x, customers.cumulative_value_share_pct, color="#164863", linewidth=2)
    ax.axvline(10, color="#a75d42", linestyle="--", linewidth=1)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_xlabel("Top customers included (%)")
    ax.set_ylabel("Share of value with known customer ID (%)")
    ax.grid(alpha=.2)
    fig.tight_layout()
    fig.savefig(figure_dir / "customer_concentration.png", dpi=180)
    plt.close(fig)
    return info, sales, cancel, product, countries, customers


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    data = root / "data"
    if not (data / "online_retail_2010dec_2011nov_input.csv").exists():
        source = data / "Online Retail.xlsx"
        extract_case(source, data / "online_retail_2010dec_2011nov_input.csv", data / "source_manifest.json")
    frame = load_case(data / "online_retail_2010dec_2011nov_input.csv")
    result = write_outputs(frame, data, root / "analysis" / "figures")
    print(json.dumps(result[0], indent=2))
