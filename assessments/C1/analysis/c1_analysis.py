"""Reproducible C1 preparation and decision-focused EDA for UCI Online Retail.

Run from any directory: python analysis/c1_analysis.py
The input is the uncleaned 12-month extract preserved from Workshop 1.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FIGURES = ROOT / "analysis" / "figures"
INPUT = DATA / "online_retail_2010dec_2011nov_input.csv"
START = pd.Timestamp("2010-12-01")
END = pd.Timestamp("2011-12-01")
SOURCE_COLUMNS = ["InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate", "UnitPrice", "CustomerID", "Country"]
MERCHANDISE_REGEX = r"[0-9]{5}[A-Z]?"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def value_stats(values: pd.Series) -> dict[str, float]:
    x = values.dropna().astype(float)
    med = float(x.median())
    return {
        "n": int(x.size),
        "mean": float(x.mean()),
        "median": med,
        "q1": float(x.quantile(0.25)),
        "q3": float(x.quantile(0.75)),
        "iqr": float(x.quantile(0.75) - x.quantile(0.25)),
        "mad": float((x - med).abs().median()),
        "p90": float(x.quantile(0.90)),
        "p99": float(x.quantile(0.99)),
        "max": float(x.max()),
    }


def concentration(lines: pd.DataFrame) -> dict[str, float | int]:
    known = lines.loc[lines["CustomerID"].notna()]
    values = known.groupby("CustomerID", observed=True)["line_value_gbp"].sum().sort_values(ascending=False)
    n_top = math.ceil(len(values) * 0.10)
    return {
        "customers": int(len(values)),
        "top_decile_ids": int(n_top),
        "known_value_gbp": float(values.sum()),
        "top_decile_share_pct": float(100 * values.head(n_top).sum() / values.sum()),
        "known_id_value_coverage_pct": float(100 * values.sum() / lines["line_value_gbp"].sum()),
    }


def prepare(raw: pd.DataFrame) -> pd.DataFrame:
    d = raw.copy()
    d.insert(0, "source_row", np.arange(1, len(d) + 1, dtype=np.int32))
    d["month"] = d["InvoiceDate"].dt.strftime("%Y-%m")
    d["is_c_invoice"] = d["InvoiceNo"].str.startswith("C")
    d["merchandise_rule"] = d["StockCode"].str.fullmatch(MERCHANDISE_REGEX)
    d["missing_customer_id"] = d["CustomerID"].isna()
    d["missing_description"] = d["Description"].isna()
    d["exact_duplicate"] = raw.duplicated(keep="first")
    d["nonpositive_price"] = d["UnitPrice"].le(0)
    d["nonpositive_quantity"] = d["Quantity"].le(0)
    d["negative_non_c_quantity"] = d["Quantity"].lt(0) & ~d["is_c_invoice"]
    d["eligible_purchase"] = (
        d["merchandise_rule"] & ~d["is_c_invoice"]
        & d["Quantity"].gt(0) & d["UnitPrice"].gt(0)
    )
    d["eligible_c_record"] = (
        d["merchandise_rule"] & d["is_c_invoice"]
        & d["Quantity"].lt(0) & d["UnitPrice"].gt(0)
    )
    d["row_group"] = np.select(
        [d["eligible_purchase"], d["eligible_c_record"]],
        ["priced_purchase", "priced_C_record"],
        default="other_retained",
    )
    d["line_value_gbp"] = np.where(
        d["eligible_purchase"], d["Quantity"] * d["UnitPrice"], np.nan
    )
    return d


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(
        INPUT,
        dtype={"InvoiceNo": "string", "StockCode": "string", "CustomerID": "Int64", "Country": "string"},
        parse_dates=["InvoiceDate"],
    )
    assert list(raw.columns) == SOURCE_COLUMNS
    assert len(raw) == 516_384
    assert raw["InvoiceDate"].notna().all()
    assert raw["InvoiceDate"].ge(START).all() and raw["InvoiceDate"].lt(END).all()
    assert raw["InvoiceNo"].notna().all() and raw["StockCode"].notna().all()
    assert raw["Quantity"].notna().all() and raw["UnitPrice"].notna().all()

    d = prepare(raw)
    assert len(d) == len(raw) and d["source_row"].is_unique
    assert not (d["eligible_purchase"] & d["eligible_c_record"]).any()
    assert d["row_group"].value_counts().to_dict() == {
        "priced_purchase": 500_531, "priced_C_record": 8_351, "other_retained": 7_502,
    }
    assert np.array_equal(d["line_value_gbp"].notna().to_numpy(), d["eligible_purchase"].to_numpy(dtype=bool))
    assert d.loc[d["eligible_purchase"], "line_value_gbp"].gt(0).all()
    # One auditable flag record per source row; the unchanged input owns the eight original fields.
    prepared_columns = [
        "source_row", "month", "is_c_invoice", "merchandise_rule", "missing_customer_id",
        "missing_description", "exact_duplicate", "nonpositive_price", "nonpositive_quantity",
        "negative_non_c_quantity", "eligible_purchase", "eligible_c_record", "row_group",
        "line_value_gbp",
    ]
    d[prepared_columns].to_csv(DATA / "prepared_lines.csv", index=False)

    purchase = d.loc[d["eligible_purchase"]].copy()
    known = purchase.loc[~purchase["missing_customer_id"]].copy()
    customers = (
        known.groupby("CustomerID", observed=True)
        .agg(observed_value_gbp=("line_value_gbp", "sum"),
             purchase_invoices=("InvoiceNo", "nunique"), purchase_lines=("InvoiceNo", "size"),
             first_observed=("InvoiceDate", "min"), last_observed=("InvoiceDate", "max"))
        .sort_values("observed_value_gbp", ascending=False).reset_index()
    )
    customers.insert(0, "rank", np.arange(1, len(customers) + 1))
    customers["cumulative_value_share_pct"] = 100 * customers["observed_value_gbp"].cumsum() / customers["observed_value_gbp"].sum()
    customers.to_csv(DATA / "customer_portfolio.csv", index=False)
    customers["observed_invoice_group"] = np.where(customers["purchase_invoices"].eq(1), "one invoice", "two or more invoices")
    frequency_groups = (
        customers.groupby("observed_invoice_group", observed=True)
        .agg(customers=("CustomerID", "size"), observed_value_gbp=("observed_value_gbp", "sum"),
             median_customer_value_gbp=("observed_value_gbp", "median"))
        .reset_index()
    )
    frequency_groups["customer_share_pct"] = 100 * frequency_groups["customers"] / len(customers)
    frequency_groups["known_value_share_pct"] = 100 * frequency_groups["observed_value_gbp"] / customers["observed_value_gbp"].sum()
    frequency_groups.to_csv(DATA / "invoice_frequency_groups.csv", index=False)

    invoice = (
        purchase.groupby("InvoiceNo", observed=True)
        .agg(lines=("source_row", "size"), value_gbp=("line_value_gbp", "sum"),
             customer_ids=("CustomerID", "nunique"), first_date=("InvoiceDate", "min"))
        .reset_index()
    )
    invoice.to_csv(DATA / "purchase_invoices.csv", index=False)
    invoice_id_counts = purchase.groupby("InvoiceNo", observed=True)["CustomerID"].agg(["size", "count", "nunique"])
    mixed_id_invoices = int(((invoice_id_counts["count"] > 0) & (invoice_id_counts["count"] < invoice_id_counts["size"])).sum())
    no_id_invoices = int(invoice_id_counts["count"].eq(0).sum())
    assert mixed_id_invoices == 0 and invoice_id_counts["nunique"].le(1).all()

    monthly = (
        purchase.groupby("month", observed=True)
        .agg(purchase_lines=("source_row", "size"), purchase_invoices=("InvoiceNo", "nunique"),
             purchase_value_gbp=("line_value_gbp", "sum"))
        .reset_index()
    )
    m_known = known.groupby("month", observed=True).agg(
        known_id_lines=("source_row", "size"), known_id_value_gbp=("line_value_gbp", "sum"),
        known_id_customers=("CustomerID", "nunique")
    ).reset_index()
    monthly = monthly.merge(m_known, on="month", validate="one_to_one")
    monthly["known_id_coverage_pct"] = 100 * monthly["known_id_value_gbp"] / monthly["purchase_value_gbp"]
    monthly["top_decile_share_pct"] = monthly["month"].map({
        month: concentration(group)["top_decile_share_pct"]
        for month, group in purchase.groupby("month", observed=True)
    })
    monthly["top_decile_ids"] = monthly["known_id_customers"].map(lambda n: math.ceil(n * .10))
    monthly.to_csv(DATA / "monthly_kpi.csv", index=False)

    quality = (
        d.groupby("month", observed=True)
        .agg(rows=("source_row", "size"), missing_customer_id=("missing_customer_id", "sum"),
             missing_description=("missing_description", "sum"), exact_duplicate=("exact_duplicate", "sum"),
             nonpositive_price=("nonpositive_price", "sum"),
             outside_merchandise_rule=("merchandise_rule", lambda x: (~x).sum()),
             negative_non_c_quantity=("negative_non_c_quantity", "sum"))
        .reset_index()
    )
    quality.to_csv(DATA / "quality_by_month.csv", index=False)

    country = (
        purchase.groupby("Country", observed=True)
        .agg(purchase_lines=("source_row", "size"), value_gbp=("line_value_gbp", "sum"))
        .reset_index()
    )
    known_country = (
        known.groupby("Country", observed=True)
        .agg(known_id_value_gbp=("line_value_gbp", "sum"), known_id_customers=("CustomerID", "nunique"))
        .reset_index()
    )
    country = country.merge(known_country, on="Country", how="left", validate="one_to_one")
    country["known_id_value_coverage_pct"] = 100 * country["known_id_value_gbp"] / country["value_gbp"]
    country.sort_values("value_gbp", ascending=False).to_csv(DATA / "country_coverage.csv", index=False)
    segments = []
    for label, mask in [("United Kingdom", purchase["Country"].eq("United Kingdom")),
                        ("Other countries", purchase["Country"].ne("United Kingdom"))]:
        subset = purchase.loc[mask]
        segments.append({"segment": label, "purchase_lines": len(subset),
                         "purchase_value_gbp": float(subset["line_value_gbp"].sum()),
                         **concentration(subset)})
    pd.DataFrame(segments).to_csv(DATA / "uk_segment_kpi.csv", index=False)

    # Explicit alternative populations: diagnostics, not changes to the baseline.
    baseline = concentration(purchase)
    dedup = concentration(purchase.loc[~purchase["exact_duplicate"]])
    strict = concentration(purchase.loc[purchase["StockCode"].str.fullmatch(r"[0-9]{5}")])
    broad = raw.loc[(~raw["InvoiceNo"].str.startswith("C")) & raw["Quantity"].gt(0) & raw["UnitPrice"].gt(0)].copy()
    broad["line_value_gbp"] = broad["Quantity"] * broad["UnitPrice"]
    broad_result = concentration(broad)
    largest = customers.iloc[0]
    without_largest = concentration(purchase.loc[purchase["CustomerID"].ne(largest["CustomerID"]).fillna(True)])
    sensitivity = pd.DataFrame([
        {"scenario": "baseline", **baseline},
        {"scenario": "drop exact repeat rows", **dedup},
        {"scenario": "strict five-digit codes", **strict},
        {"scenario": "all positive priced stock codes", **broad_result},
        {"scenario": "remove largest known ID (diagnostic)", **without_largest},
    ])
    sensitivity.to_csv(DATA / "sensitivity.csv", index=False)

    value = customers["observed_value_gbp"]
    invoices = customers["purchase_invoices"]
    top_n = baseline["top_decile_ids"]
    top_value = float(customers.head(top_n)["observed_value_gbp"].sum())
    one_invoice = customers.loc[customers["purchase_invoices"].eq(1)]
    report = {
        "source_rows": int(len(raw)), "source_sha256": sha256(INPUT),
        "period_first": str(raw["InvoiceDate"].min()), "period_last": str(raw["InvoiceDate"].max()),
        "eligible_purchase_lines": int(len(purchase)),
        "eligible_c_lines": int(d["eligible_c_record"].sum()),
        "other_retained": int(d["row_group"].eq("other_retained").sum()),
        "missing_customer_id_raw": int(d["missing_customer_id"].sum()),
        "missing_description_raw": int(d["missing_description"].sum()),
        "exact_duplicates_raw": int(d["exact_duplicate"].sum()),
        "nonpositive_price_raw": int(d["nonpositive_price"].sum()),
        "outside_merchandise_rule_raw": int((~d["merchandise_rule"]).sum()),
        "negative_non_c_quantity_raw": int(d["negative_non_c_quantity"].sum()),
        "purchase_value_gbp": float(purchase["line_value_gbp"].sum()),
        "known_id_value_gbp": float(known["line_value_gbp"].sum()),
        "unknown_id_value_gbp": float(purchase.loc[purchase["missing_customer_id"], "line_value_gbp"].sum()),
        "baseline": baseline,
        "top_decile_value_gbp": top_value,
        "top_one_pct_customer_count": int(math.ceil(len(customers) * 0.01)),
        "top_one_pct_share_of_known_value_pct": float(100 * customers.head(math.ceil(len(customers) * 0.01))["observed_value_gbp"].sum() / baseline["known_value_gbp"]),
        "top_one_customer_share_of_known_value_pct": float(100 * largest["observed_value_gbp"] / baseline["known_value_gbp"]),
        "one_invoice_customers": int(len(one_invoice)),
        "one_invoice_id_share_pct": float(100 * len(one_invoice) / len(customers)),
        "one_invoice_value_share_pct": float(100 * one_invoice["observed_value_gbp"].sum() / baseline["known_value_gbp"]),
        "two_plus_invoice_value_share_pct": float(100 * customers.loc[customers["purchase_invoices"].ge(2), "observed_value_gbp"].sum() / baseline["known_value_gbp"]),
        "customer_value_stats": value_stats(value),
        "customer_invoice_stats": value_stats(invoices),
        "invoice_value_stats": value_stats(invoice["value_gbp"]),
        "line_value_stats": value_stats(purchase["line_value_gbp"]),
        "invoice_multiple_customer_ids": int(invoice["customer_ids"].gt(1).sum()),
        "purchase_invoices_entirely_without_id": no_id_invoices,
        "purchase_invoices_with_mixed_known_missing_id": mixed_id_invoices,
        "spearman_customer_invoice_count_vs_value": float(customers["purchase_invoices"].rank().corr(customers["observed_value_gbp"].rank())),
        "pearson_customer_invoice_count_vs_value": float(customers["purchase_invoices"].corr(customers["observed_value_gbp"])),
        "monthly_known_id_coverage_min_pct": float(monthly["known_id_coverage_pct"].min()),
        "monthly_known_id_coverage_max_pct": float(monthly["known_id_coverage_pct"].max()),
        "monthly_top_decile_min_pct": float(monthly["top_decile_share_pct"].min()),
        "monthly_top_decile_max_pct": float(monthly["top_decile_share_pct"].max()),
    }
    (DATA / "report_metrics.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
    color = "#173e56"
    fig, ax = plt.subplots(figsize=(6.5, 3.3))
    ax.hist(value, bins=np.logspace(np.log10(value.min()), np.log10(value.max()), 35), color=color, edgecolor="white")
    ax.set_xscale("log")
    ax.set_xlabel("Observed value per identifiable customer (£, log scale)")
    ax.set_ylabel("Customers")
    ax.set_title("Customer value is strongly right-skewed")
    fig.tight_layout(); fig.savefig(FIGURES / "customer_value_distribution.png", dpi=190); plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.5, 3.3))
    ordered = value.sort_values().to_numpy()
    ax.plot(ordered, np.arange(1, len(ordered) + 1) / len(ordered), color=color, linewidth=2)
    ax.set_xscale("log")
    ax.set_xlabel("Observed value per identifiable customer (£, log scale)")
    ax.set_ylabel("Cumulative share of customer IDs")
    ax.set_title("Empirical distribution of customer value")
    ax.grid(alpha=.2); fig.tight_layout(); fig.savefig(FIGURES / "customer_value_ecdf.png", dpi=190); plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.5, 3.3))
    ax.scatter(invoices, value, color=color, alpha=.16, s=8, rasterized=True)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("Distinct eligible purchase invoices per ID (log scale)")
    ax.set_ylabel("Observed value per ID (£, log scale)")
    ax.set_title("Purchase frequency and value are associated")
    ax.grid(alpha=.2); fig.tight_layout(); fig.savefig(FIGURES / "frequency_value_scatter.png", dpi=190); plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.5, 3.3))
    ax.plot(100 * customers["rank"] / len(customers), customers["cumulative_value_share_pct"], color=color, linewidth=2)
    ax.axvline(10, color="#b96540", linestyle="--", linewidth=1.2)
    ax.scatter([10], [baseline["top_decile_share_pct"]], color="#b96540", s=30, zorder=5)
    ax.set_xlabel("Highest-value customers included (%)")
    ax.set_ylabel("Share of known-ID purchase value (%)")
    ax.set_title("Portfolio concentration in the observed year")
    ax.set_xlim(0, 100); ax.set_ylim(0, 100)
    ax.grid(alpha=.2); fig.tight_layout(); fig.savefig(FIGURES / "concentration_curve.png", dpi=190); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 3.3))
    x = np.arange(len(monthly))
    ax.bar(x, monthly["top_decile_share_pct"], color=color, alpha=.9)
    ax.plot(x, monthly["known_id_coverage_pct"], color="#b96540", marker="o", linewidth=1.5, label="Known-ID value coverage")
    ax.set_xticks(x, monthly["month"], rotation=45, ha="right")
    ax.set_ylim(0, 100); ax.set_ylabel("Percent (%)")
    ax.set_title("Monthly concentration and ID coverage")
    ax.legend(frameon=False, loc="lower right")
    fig.tight_layout(); fig.savefig(FIGURES / "monthly_concentration_coverage.png", dpi=190); plt.close(fig)

    print(json.dumps({"baseline": baseline, "customer_value_stats": report["customer_value_stats"],
                      "sensitivity": sensitivity.to_dict(orient="records")}, indent=2))


if __name__ == "__main__":
    main()
