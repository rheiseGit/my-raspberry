import dash
from dash import html, dcc

dash.register_page(__name__, title="Welcome", name="welcome")

layout = html.Div(
    [
        html.H2("Welcome"),
        html.P(
            "This project aims at providing access to several features implemented on a RPi! ",
            style={"font-style": "italic"},
        ),
        html.Img(
            src=dash.get_asset_url("squirrel.png"), style={"padding-bottom": "10px"}
        ),
        # html.Img(
        #    src=dash.get_asset_url("github-mark.svg"), style={"padding-bottom": "10px"}
        # ),
        # html.Img(src=dash.get_asset_url("github-mark.svg")),
        html.H3("Repository"),
        html.P(
            html.A(
                "https://github.com/rheiseGit/my-raspberry",
                href="https://github.com/rheiseGit/my-raspberry",
            )
        ),
    ]
)
