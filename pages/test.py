"""
PAGE: just a test
"""

import dash
from dash import html, dcc, callback, Input, Output

dash.register_page(__name__, title="Test", name="test")

layout = html.Div(
    [
        html.H2("Test"),
        html.P(
            "What should be shown here? So far, just an example for a callback.",
            style={"font-style": "italic"},
        ),
        html.Div(
            [
                "Select a city: ",
                dcc.RadioItems(
                    options=["New York City", "Montreal", "San Francisco"],
                    value="Montreal",
                    id="analytics-input",
                ),
            ]
        ),
        html.Br(),
        html.Div(id="analytics-output"),
    ]
)


@callback(Output("analytics-output", "children"), Input("analytics-input", "value"))
def update_city_selected(input_value):
    return f"You selected: {input_value}"
