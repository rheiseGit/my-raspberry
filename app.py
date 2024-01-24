print('START')

from dash import Dash, Output, Input, html, dcc
import dash
import dash_bootstrap_components as dbc
from flask import Flask, Response, redirect
import pys.camera as camera
import os

print('START')
# SOME CONFIGURATION
APPLICATION_DIR = os.path.dirname(__file__)
FOLDER_TO_SAVE_IMAGES = "saved"
PATH_TO_SAVE_IMAGES = os.path.join(APPLICATION_DIR, FOLDER_TO_SAVE_IMAGES)

# FLASK: used to redirect and set up videostream
server = Flask(__name__)


@server.route("/")
def root_redirect():
    return redirect("/welcome")


# DASH: main framework used
# usage of multi-page feature (partially)
print('START')
app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.DARKLY],
    suppress_callback_exceptions=True,
    server=server,
)

# creation of navbar incluing the pages defined in folder pages
urls = [
    dbc.DropdownMenuItem(page["title"], href=page["relative_path"])
    for page in dash.page_registry.values()
    if not page["name"].startswith("feature")
]

urls_features = [
    dbc.DropdownMenuItem(page["title"], href=page["relative_path"])
    for page in dash.page_registry.values()
    if page["name"].startswith("feature")
]

dropdown_menu_item_list = (
    [dbc.DropdownMenuItem("Information", header=True)]
    + urls
    + [dbc.DropdownMenuItem("Features", header=True)]
    + urls_features
)

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(
            dbc.NavLink(
                html.Img(
                    src=dash.get_asset_url("github-mark.svg"),
                    style={"height": "25px"},
                ),
                href="https://github.com/rheiseGit/my-raspberry",
            )
        ),
        # dbc.NavItem(
        #    dbc.NavLink("GitHub", href="https://github.com/rheiseGit/my-raspberry")
        # ),
        dbc.DropdownMenu(
            dropdown_menu_item_list,
            nav=True,
            in_navbar=True,
            label="Content",
        ),
    ],
    brand="MyRaspberry",
    brand_href="/welcome",
    color="primary",
    dark=True,
)

""" alternative navbar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Welcome", href="/welcome")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Content", header=True),
                dbc.DropdownMenuItem("Welcome", href="/welcome"),
                # dbc.DropdownMenuItem("System Info", href="/system"),
                # dbc.DropdownMenuItem("Camera", href="/camera"),
                dbc.DropdownMenuItem("Logs", href="/logs"),
            ],
            nav=True,
            in_navbar=True,
            label="Content",
        ),
    ],
    brand="MyRaspberry",
    brand_href="#",
    color="primary",
    dark=True,
)
"""

app.layout = html.Div(
    [
        dcc.Location(id="url"),
        navbar,
        dbc.Container(dash.page_container, style={"margin-top": 20}),
        html.Div(id="placeholder"),  # empty placeholder for callbacks without output
    ]
)

# Functionality of Camera (connection of camera.py to cam)
adapter = camera.AdapterPiCamera()
cam = camera.VideoCamera(adapter=adapter)
res = cam.check()
print('Camera Ceck',res)


@server.route("/video_feed")
def video_feed():
    return Response(
        camera.gen(cam), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.callback(
    Output("placeholder", "children"),
    Input("camera-checklist", "value"),
)
def set_camera_paramters(value):
    cam.use_grayscale = "grayscale" in value
    cam.flip = "flip" in value
    cam.info = "info" in value
    return ""


@app.callback(
    Output("camera-start-stop-button", "children"),
    Output("camera-save-button", "disabled", allow_duplicate=True),
    Input("camera-start-stop-button", "n_clicks"),
    prevent_initial_call=True,
)
def click_camera_start_stop_button(n_clicks):
    if n_clicks % 2 == 1:
        cam.running = False
        return "Start", False
    else:
        cam.running = True
        return "Stop", True


@app.callback(
    Output("camera-save-button", "disabled", allow_duplicate=True),
    Input("camera-save-button", "n_clicks"),
    prevent_initial_call=True,
)
def click_camera_save_button(n_clicks):
    filepath = os.path.join(PATH_TO_SAVE_IMAGES, "saved_image.jpg")
    print(filepath)
    cam.save_last_frame_to_file(filepath)
    return True


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port="8050", debug=False)

