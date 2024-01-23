import dash
from dash import html

dash.register_page(__name__, title="Default", name="default")

layout = html.Div(
    [
        html.H2("Default"),
        html.P(
            "Just an empty page, which can serve as an template.",
            style={"font-style": "italic"},
        ),
    ]
)
