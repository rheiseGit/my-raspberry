"""
PAGE: Simplification of page cameracontrol which allows only to pick up the video
"""

import dash
from dash import html, Output, Input, State, dcc, callback, get_app
import dash_bootstrap_components as dbc
from pys.initialized_camera_connected_to_app import cam
from pys.camera import encode_frame_as_jpg
import os

print("REGISTER", __file__)
dash.register_page(__name__, title="Videostream", name="feature-camera-stream")
app = dash.get_app()

# SOME CONFIGURATION
APPLICATION_DIR = os.path.dirname(__file__)
FOLDER_TO_SAVE_IMAGES = "saved"
PATH_TO_SAVE_IMAGES = os.path.join(APPLICATION_DIR, FOLDER_TO_SAVE_IMAGES)

# LAYOUT

# STATIC ELEMENTS
VALUE_BUTTON_SAVE_IMAGE = [
    html.I(className="bi bi-image-fill m-1"),
    "Save",
]
VALUE_BUTTON_SAVED_IMAGE = [
    html.I(className="bi bi-image-fill m-1"),
    "Saved",
]
VALUE_BUTTON_HR_IMAGE = [
    html.I(className="bi bi-image-fill m-1"),
    "Image",
]


def create_layout(cam=cam):
    """Creates layout based on current status of for example the camera
    Function is called when page is loaded
    """

    # Layout of controls
    controls_camera = [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Button(
                            VALUE_BUTTON_HR_IMAGE,
                            id="stream-camera-hr-button",
                            n_clicks=0,
                            className="m-1 d-md-block",
                        ),
                    ],
                ),
            ]
        ),
    ]

    row_hr_image = dbc.Row(
        [
            dbc.Col(
                [],
                id="stream-col-hr-image",
                className="col-sm-9 col-12",
            ),
            dbc.Col(
                [
                    dbc.Button(
                        VALUE_BUTTON_SAVE_IMAGE,
                        id="stream-camera-save-button",
                        className="m-1 d-md-block",
                    ),
                ],
                className="col-12 col-sm-3",
            ),
        ],
        id="stream-row-hr-image",
        style={"display": "none"},
    )

    # Main layout
    layout = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(["Camera-Control"]),
                ]
            ),
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
                        controls_camera,
                        className="col-12 col-sm-3",
                    ),
                ],
            ),
            row_hr_image,
        ]
    )
    return layout


layout = create_layout


@app.callback(
    Output("stream-camera-save-button", "disabled", allow_duplicate=True),
    Output("stream-camera-save-button", "children", allow_duplicate=True),
    Input("stream-camera-save-button", "n_clicks"),
    prevent_initial_call=True,
)
def click_camera_save_button(n_clicks):
    """Save-image-button"""
    filepath = os.path.join(PATH_TO_SAVE_IMAGES, "saved_image.jpg")
    print(" - SAVEFILE:", filepath)
    cam.save_stored_image_to_file(filepath)
    return True, VALUE_BUTTON_SAVED_IMAGE


@app.callback(
    Output("stream-col-hr-image", "children"),
    Output("stream-camera-save-button", "disabled", allow_duplicate=True),
    Output("stream-camera-save-button", "children", allow_duplicate=True),
    Output("stream-row-hr-image", "style"),
    Input("stream-camera-hr-button", "n_clicks"),
    prevent_initial_call=True,
)
def click_hr_button(n_clicks):
    """Take HR-Image"""
    if n_clicks % 2 == 0:
        return [], True, VALUE_BUTTON_SAVE_IMAGE, {"display": "none"}
    else:
        dataURI = encode_frame_as_jpg(cam.get_and_store_last_transformed_frame())
        return (
            html.Img(
                src=dataURI,
                id="image-hr",
                width="100%",
                style={"padding-bottom": "4px"},
            ),
            False,
            VALUE_BUTTON_SAVE_IMAGE,
            {"display": "flex"},
        )
