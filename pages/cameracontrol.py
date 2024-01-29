import dash
from dash import html, Output, Input, State, dcc, callback, get_app
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


# Videostream via Flask
@app.server.route("/video_feed")
def video_feed():
    return Response(
        camera.gen(cam), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


# LAYOUT
# Accordion for controls with checklist
accordion = html.Div(
    dbc.Accordion(
        [
            dbc.AccordionItem(
                [
                    dbc.Container(
                        [
                            dbc.Checklist(
                                options=["grayscale", "vflip", "hflip", "info"],
                                value=[],
                                id="camera-checklist",
                            ),
                        ]
                    ),
                ],
                title="Simple Transformations",
            ),
        ],
    )
)

# Offcanvas includes accordion
offcanvas = html.Div(
    [
        dbc.Offcanvas(
            [
                accordion,
            ],
            id="offcanvas",
            title="Transformations",
            is_open=False,
        ),
    ]
)


value_button_save_image = [
    html.I(className="bi bi-image-fill m-1"),
    "Save",
]
value_button_stop = [
    html.I(className="bi bi-stop-fill"),
    "Stop",
]
value_button_start = [
    html.I(className="bi bi-play-fill"),
    "Start",
]

# Layout of controls
controls = [
    dbc.Row(
        [
            dbc.Col(
                [
                    dbc.Button(
                        value_button_stop,
                        n_clicks=0,
                        id="camera-start-stop-button",
                        className="m-1 d-md-block",
                    ),
                    dbc.Button(
                        value_button_save_image,
                        id="camera-save-button",
                        disabled=True,
                        className="m-1 d-md-block",
                    ),
                ],
            ),
        ]
    ),
    dbc.Row(
        dbc.Col(
            dbc.Button(
                "Transformations",
                id="open-offcanvas",
                n_clicks=0,
                color="secondary",
                className="m-1 d-grid d-md-block",
            )
        )
    ),
]

# Main layout
layout = html.Div(
    [
        dbc.Row([dbc.Col("Camera Control")]),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Img(
                            src="/video_feed",
                            id="video-feed",
                            width="100%",
                            style={"padding-bottom": "4px"},
                        ),
                    ],
                    className="col-sm-9 col-12",
                ),
                dbc.Col(
                    controls,
                    className="col-12 col-sm-3",
                ),
            ],
        ),
        offcanvas,
    ]
)


# CALLBACKS


@app.callback(
    Output("placeholder", "children"),
    Input("camera-checklist", "value"),
)
def set_camera_paramters(value):
    """Applies setting from checklist"""
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
    """Start-stop-button"""
    if n_clicks % 2 == 1:
        cam.running = False
        return value_button_start, False
    else:
        cam.running = True
        return value_button_stop, True


@app.callback(
    Output("camera-save-button", "disabled", allow_duplicate=True),
    Input("camera-save-button", "n_clicks"),
    prevent_initial_call=True,
)
def click_camera_save_button(n_clicks):
    """Save-image-button"""
    filepath = os.path.join(PATH_TO_SAVE_IMAGES, "saved_image.jpg")
    print(filepath)
    cam.save_last_frame_to_file(filepath)
    return True


@app.callback(
    Output("offcanvas", "is_open"),
    Input("open-offcanvas", "n_clicks"),
    [State("offcanvas", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    """Offcanvas"""
    if n1:
        return not is_open
    return is_open
