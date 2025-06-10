"""Dash application entry point with basic layout."""

from pathlib import Path

import dash
from dash import dash_table, dcc, html
import pandas as pd

from db_utils import init_db


DATA_DIR = Path(__file__).resolve().parent / "data"
SAMPLE_DATA = DATA_DIR / "sample_trades.csv"
SCHEMA_FILE = Path(__file__).resolve().parent / "schema.sql"


def get_connection():
    """Return a DuckDB connection with the trades table initialized."""
    conn = init_db()

    # Load schema to ensure the trades table exists
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        conn.execute(f.read())

    # Populate with sample data if the table is empty
    count = conn.execute("SELECT count(*) FROM trades").fetchone()[0]
    if count == 0 and SAMPLE_DATA.exists():
        df = pd.read_csv(SAMPLE_DATA)
        conn.register("df", df)
        conn.execute("INSERT INTO trades SELECT * FROM df")

    return conn


def load_trades() -> pd.DataFrame:
    """Load all trades from DuckDB into a DataFrame."""
    with get_connection() as conn:
        return conn.execute("SELECT * FROM trades ORDER BY date").fetchdf()


def equity_curve(df: pd.DataFrame) -> pd.DataFrame:
    """Return cumulative equity curve from trade data."""
    if df.empty:
        return pd.DataFrame({"date": [], "equity": []})

    curve = df.copy()
    curve["equity"] = (curve["quantity"] * curve["price"]).cumsum()
    return curve[["date", "equity"]]


app = dash.Dash(__name__)

trades_df = load_trades()
curve_df = equity_curve(trades_df)

app.layout = html.Div(
    [
        html.H1("Trading Journal"),
        html.Div(
            [
                html.Div([
                    html.Label("Ticker"),
                    dcc.Input(id="input-ticker", type="text"),
                ]),
                html.Div([
                    html.Label("Entry"),
                    dcc.Input(id="input-entry", type="number"),
                ]),
                html.Div([
                    html.Label("Exit"),
                    dcc.Input(id="input-exit", type="number"),
                ]),
                html.Div([
                    html.Label("Strategy"),
                    dcc.Input(id="input-strategy", type="text"),
                ]),
                html.Div([
                    html.Label("Notes"),
                    dcc.Textarea(id="input-notes"),
                ]),
                html.Button("Submit", id="submit-trade", n_clicks=0),
            ],
            style={"marginBottom": "20px"},
        ),
        dash_table.DataTable(
            id="trades-table",
            columns=[{"name": i, "id": i} for i in trades_df.columns],
            data=trades_df.to_dict("records"),
        ),
        dcc.Graph(
            id="equity-curve",
            figure={
                "data": [
                    {
                        "x": curve_df["date"],
                        "y": curve_df["equity"],
                        "type": "line",
                    }
                ],
                "layout": {"title": "Equity Curve"},
            },
        ),
    ]
)


if __name__ == "__main__":
    app.run_server(debug=True)
