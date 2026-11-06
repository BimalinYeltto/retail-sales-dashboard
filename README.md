# Retail Sales Dashboard (CSV + Matplotlib + Flask)

## Run
    pip install -r requirements.txt
    python generate_data.py     # creates sales_data.csv (or use your own CSV)
    python app.py               # open http://127.0.0.1:5000

## Upload your own CSV
Use the Upload CSV button on the page.
Required columns: date, region, category, product, sales
Optional columns: profit, order_id (other columns are ignored)
Column names are not case sensitive. Use 'Use sample data' to go back to the sample file.

## Files
- generate_data.py: builds the sample dataset
- app.py: loads CSV with pandas, filters, draws charts with matplotlib, serves them with Flask
- templates/index.html: dashboard page (KPI cards, filters, 4 charts)
