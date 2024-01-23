import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import cv2

dash.register_page(__name__, title="Videostream", name="feature-videostream")

layout = html.Div(
    [
        html.H2("Videostream"),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Img(
                            src="/video_feed", id="video-feed", style={"width": "95%"}
                        ),
                    ],
                    width=9,
                ),
                dbc.Col(
                    [
                        html.H4("Transformations"),
                        dbc.Checklist(
                            options=["grayscale", "flip", "info"],
                            value=[],
                            id="camera-checklist",
                        ),
                        html.H4("Actions", style={"margin-top": "20px"}),
                        dbc.Button(
                            "Stop",
                            n_clicks=0,
                            id="camera-start-stop-button",
                            style={"margin": "2px"},
                        ),
                        dbc.Button(
                            "Save",
                            id="camera-save-button",
                            disabled=True,
                            style={"margin": "2px"},
                        ),
                    ],
                    width=3,
                ),
            ]
        ),
    ]
)

# Callback is defined in app.py
