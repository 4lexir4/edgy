"""Dash application entry point."""

import dash

app = dash.Dash(__name__)


if __name__ == "__main__":
    app.run_server(debug=True)
