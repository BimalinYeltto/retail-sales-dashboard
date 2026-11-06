import base64, io
import matplotlib
matplotlib.use("Agg")  # render charts without opening a GUI window
import matplotlib.pyplot as plt
import pandas as pd
from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = "retail-dashboard-mini-project"
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB upload limit

REQUIRED = ["date", "region", "category", "product", "sales"]  # profit and order_id are optional
SAMPLE_FILE = "sales_data.csv"


def clean(raw):
    """Validate and tidy an uploaded DataFrame. Raises ValueError with a friendly message."""
    raw = raw.copy()
    raw.columns = [str(c).strip().lower().replace(" ", "_") for c in raw.columns]
    missing = [c for c in REQUIRED if c not in raw.columns]
    if missing:
        raise ValueError("missing column(s): " + ", ".join(missing))
    raw["date"] = pd.to_datetime(raw["date"], errors="coerce")
    raw["sales"] = pd.to_numeric(raw["sales"], errors="coerce")
    if "profit" in raw.columns:
        raw["profit"] = pd.to_numeric(raw["profit"], errors="coerce")
    raw = raw.dropna(subset=["date", "sales"])
    if raw.empty:
        raise ValueError("no valid rows found (check the date and sales columns)")
    for col in ["region", "category", "product"]:
        raw[col] = raw[col].fillna("Unknown").astype(str)
    return raw


def load_sample():
    return clean(pd.read_csv(SAMPLE_FILE))


data = {"df": load_sample(), "name": SAMPLE_FILE + " (sample)"}


def to_b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=110)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode()


def build_charts(d):
    charts = {}

    m = d.set_index("date").resample("MS")["sales"].sum()
    fig, ax = plt.subplots(figsize=(6, 3.2))
    ax.plot(m.index.strftime("%b %y"), m.values, marker="o", color="#2563eb")
    ax.set(title="Monthly Sales Trend", ylabel="Sales")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(alpha=0.3)
    charts["trend"] = to_b64(fig)

    c = d.groupby("category")["sales"].sum().nlargest(10).sort_values()
    fig, ax = plt.subplots(figsize=(6, 3.2))
    ax.barh(c.index, c.values, color="#10b981")
    ax.set(title="Sales by Category", xlabel="Sales")
    charts["category"] = to_b64(fig)

    r = d.groupby("region")["sales"].sum()
    fig, ax = plt.subplots(figsize=(6, 3.2))
    ax.pie(r.values, labels=r.index, autopct="%1.1f%%", startangle=90)
    ax.set_title("Sales Share by Region")
    charts["region"] = to_b64(fig)

    p = d.groupby("product")["sales"].sum().nlargest(5).sort_values()
    fig, ax = plt.subplots(figsize=(6, 3.2))
    ax.barh(p.index, p.values, color="#f59e0b")
    ax.set(title="Top 5 Products", xlabel="Sales")
    charts["products"] = to_b64(fig)
    return charts


@app.route("/")
def index():
    df = data["df"]
    region = request.args.get("region", "All")
    category = request.args.get("category", "All")
    d = df
    if region != "All":
        d = d[d["region"] == region]
    if category != "All":
        d = d[d["category"] == category]

    kpis = charts = None
    if not d.empty:
        kpis = {
            "sales": f"{d['sales'].sum():,.0f}",
            "profit": f"{d['profit'].sum():,.0f}" if "profit" in d else "N/A",
            "orders": f"{d['order_id'].nunique():,}" if "order_id" in d else f"{len(d):,}",
            "avg": f"{d['sales'].mean():,.0f}",
        }
        charts = build_charts(d)
    return render_template(
        "index.html", kpis=kpis, charts=charts, region=region, category=category,
        regions=["All"] + sorted(df["region"].unique()),
        categories=["All"] + sorted(df["category"].unique()),
        filename=data["name"], required=REQUIRED,
    )


@app.route("/upload", methods=["POST"])
def upload():
    f = request.files.get("file")
    if not f or not f.filename.lower().endswith(".csv"):
        flash("Please choose a .csv file.", "error")
        return redirect(url_for("index"))
    try:
        data["df"] = clean(pd.read_csv(f))
        data["name"] = f.filename
        flash(f"Loaded {f.filename} ({len(data['df']):,} rows).", "ok")
    except Exception as e:
        flash(f"Could not use that file: {e}", "error")
    return redirect(url_for("index"))


@app.route("/reset", methods=["POST"])
def reset():
    data["df"] = load_sample()
    data["name"] = SAMPLE_FILE + " (sample)"
    flash("Switched back to the sample data.", "ok")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
