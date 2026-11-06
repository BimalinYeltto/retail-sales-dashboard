"""Creates a sample retail sales CSV (sales_data.csv). Replace it with any CSV that has the same columns."""
import numpy as np, pandas as pd

rng = np.random.default_rng(42)
n = 1500
products = {
    "Electronics": [("Headphones", 2500), ("Smartwatch", 6000), ("Power Bank", 1500)],
    "Clothing": [("T-Shirt", 600), ("Jeans", 1800), ("Jacket", 3200)],
    "Groceries": [("Rice 5kg", 450), ("Cooking Oil", 180), ("Snacks Pack", 120)],
    "Home": [("Table Lamp", 900), ("Bedsheet Set", 1400), ("Mixer Grinder", 3500)],
}
rows = []
for i in range(n):
    cat = rng.choice(list(products))
    prod, price = products[cat][rng.integers(0, 3)]
    qty = int(rng.integers(1, 6))
    disc = float(rng.choice([0, 0.05, 0.10, 0.20]))
    sales = round(qty * price * (1 - disc), 2)
    rows.append({
        "order_id": 1000 + i,
        "date": pd.Timestamp("2024-01-01") + pd.Timedelta(days=int(rng.integers(0, 366))),
        "region": rng.choice(["North", "South", "East", "West"]),
        "category": cat, "product": prod, "quantity": qty,
        "unit_price": price, "discount": disc, "sales": sales,
        "profit": round(sales * rng.uniform(0.08, 0.30), 2),
    })
pd.DataFrame(rows).sort_values("date").to_csv("sales_data.csv", index=False)
print("sales_data.csv created with", n, "rows")
