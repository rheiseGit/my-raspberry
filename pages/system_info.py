"""
PAGE: Provides some information about the platform.
"""

import dash
from dash import html, __version__
import platform
import platform, socket, re, uuid, psutil


def getSystemInfo():
    info = {}
    info["Hostname"] = socket.gethostname()
    info["Platform"] = platform.system()
    info["Platform-release"] = platform.release()
    info["Platform-version"] = platform.version()
    info["Architecture"] = platform.machine()
    info["ip-address"] = socket.gethostbyname(socket.gethostname())
    info["mac-address"] = ":".join(re.findall("..", "%012x" % uuid.getnode()))
    info["Processor"] = platform.processor()
    info["RAM"] = str(round(psutil.virtual_memory().total / (1024.0**3))) + " GB"
    return info


dash.register_page(__name__, title="System Info", name="system_info")

layout = html.Div(
    [
        html.H2("System Information"),
        html.P(
            "Some information read from the server.",
            style={"font-style": "italic"},
        ),
        html.Div(
            [html.Div(f"{key}: {value}") for key, value in getSystemInfo().items()]
            + [html.P(f"Dash Version: {__version__}")]
        ),
    ]
)
