import dash
from dash import html, Output, Input, dcc, callback, get_app
import dash_bootstrap_components as dbc
from flask import Response
import pys.camera as camera
import os

dash.register_page(__name__, title="Camera Control", name="feature-camera-control")

# SOME CONFIGURATION
APPLICATION_DIR = os.path.dirname(__file__)
FOLDER_TO_SAVE_IMAGES = "saved"
PATH_TO_SAVE_IMAGES = os.path.join(APPLICATION_DIR, FOLDER_TO_SAVE_IMAGES)

# Functionality of Camera (connection of camera.py to cam)
adapter = camera.AdapterPiCamera()
cam = camera.CameraController(adapter=adapter)
res = cam.check()
print("Camera Ceck", res)

# Endpoint for videofeed
app = get_app()


@app.server.route("/video_feed")
def video_feed():
    return Response(
        camera.gen(cam), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


# LAYOUT
layout = html.Div(
    [
        html.H2("Camera Control"),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H4("Output"),
                        html.Img(
                            src="/video_feed", id="video-feed", style={"width": "70%"}
                        ),
                    ],
                    width=8,
                ),
                dbc.Col(
                    [
                        html.H4("Transformations"),
                        # "(server-side)",
                        dbc.Container(
                            [
                                dbc.Checklist(
                                    options=["grayscale", "vflip", "hflip", "info"],
                                    value=[],
                                    id="camera-checklist",
                                ),
                            ]
                        ),
                        html.H4("Actions", style={"margin-top": "20px"}),
                        dbc.Container(
                            [
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
                            ]
                        ),
                    ],
                    width=4,
                ),
            ]
        ),
    ]
)

# CALLBACKS


@app.callback(
    Output("placeholder", "children"),
    Input("camera-checklist", "value"),
)
def set_camera_paramters(value):
    cam.use_grayscale = "grayscale" in value
    cam.flip_v = "vflip" in value
    cam.flip_h = "hflip" in value
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
