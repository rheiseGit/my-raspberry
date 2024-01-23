import dash
from dash import html, __version__
import platform

dash.register_page(__name__, title="System Info", name="system_info")

layout = html.Div(
    [
        html.H2("System Information"),
        html.P(
            "Some information read from the server.",
            style={"font-style": "italic"},
        ),
        html.P(f"System: {platform.system()} ({platform.release()})"),
        html.P(f"Processor: {platform.processor()}"),
        html.P(f"Dash Version: {__version__}"),
    ]
)
