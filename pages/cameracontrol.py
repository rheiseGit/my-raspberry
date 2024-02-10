"""
PAGE: describing the controls of the camera in the app at page cameracontrol
"""

import dash
from dash import html, Output, Input, State, dcc, callback, get_app
import dash_bootstrap_components as dbc
from pys.initialized_camera_connected_to_app import cam
from pys.camera import encode_frame_as_jpg
import os
import plotly.express as px

print("REGISTER", __file__)
dash.register_page(__name__, title="Camera-Control", name="feature-camera-control")
app = dash.get_app()
print("CAMERACONTROL")
print(" - APP-ID", id(app))
print(" - CAM-ID", id(cam))

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
VALUE_BUTTON_STOP = [
    html.I(className="bi bi-stop-fill"),
    "Stop",
]
VALUE_BUTTON_START = [
    html.I(className="bi bi-play-fill"),
    "Start",
]
VALUE_BUTTON_HR_IMAGE = [
    html.I(className="bi bi-image-fill m-1"),
    "Image",
]


def get_figure():
    return {
        "data": [
            {
                "x": list(range(1000)),
                "y": list(cam.get_data_from_simple_motion_detection().get("data")),
                "type": "line",
            }
        ],
        "layout": {
            "title": "Detektor",
            # "range_y": [-1, 60],
            "margin": {"l": "0", "r": "0"},
        },
    }


def get_figure():
    fig = px.line(
        x=list(range(1000)),
        y=list(cam.get_data_from_simple_motion_detection().get("data")),
    )
    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=50),
        title="Detektor",
        showlegend=False,
        plot_bgcolor="white",
        yaxis_range=[0, 30],
    )
    return fig


def get_parameter_setter_component(para: "Parameter", id: str):
    if para.vmin == 0 and para.vmax == 1:
        step = 0.1
    else:
        step = 1
    return dcc.Input(
        placeholder=para.name,
        value=para.value,
        min=para.vmin,
        max=para.vmax,
        step=step,
        type="number",
        id=id,
    )


# Layout is defined as a function the allow the layout to read information from camera
def _create_layout():  # cam=cam):
    """Creates layout based on current status of for example the camera
    Function is called when page is loaded
    """
    # Accordion for control of transformations
    accordion = html.Div(
        dbc.Accordion(
            [
                dbc.AccordionItem(
                    [
                        dbc.Container(
                            [
                                dbc.Checklist(
                                    options=cam.get_keys_of_transformations("basic"),
                                    value=cam.get_active_transformations("basic"),
                                    id="checklist-basic-transformations",
                                    switch=True,
                                ),
                            ]
                        ),
                    ],
                    title="Simple Transformations",
                ),
                dbc.AccordionItem(
                    [
                        dbc.Container(
                            [
                                dbc.Checklist(
                                    options=[transformation],
                                    value=(
                                        [transformation]
                                        if transformation
                                        in cam.get_active_transformations("registered")
                                        else []
                                    ),
                                    id=f"checklist-registered-{transformation}-transformations",
                                    switch=True,
                                ),
                                dbc.Container(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(f"{para.name}"),
                                                dbc.Col(
                                                    get_parameter_setter_component(
                                                        para,
                                                        id=f"input-parameter-{transformation}-{key}",
                                                    )
                                                ),
                                            ]
                                        )
                                        for key, para in cam.get_transformation(
                                            "registered", transformation
                                        ).parameter.items()
                                    ]
                                ),
                            ]
                        )
                        for transformation in cam.get_transformation("registered")
                    ],
                    title="Registered Transformations",
                ),
                dbc.AccordionItem(
                    [
                        dbc.Container(
                            [
                                dbc.Checklist(
                                    options=cam.get_keys_of_transformations("post"),
                                    value=cam.get_active_transformations("post"),
                                    id="checklist-post-transformations",
                                    switch=True,
                                ),
                            ]
                        ),
                    ],
                    title="Post Transformations",
                ),
            ],
        )
    )

    # Offcanvas includes accordion
    offcanvas_transformations = html.Div(
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

    # Layout of controls
    controls_camera = [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Button(
                            VALUE_BUTTON_STOP if cam.running() else VALUE_BUTTON_START,
                            n_clicks=0,
                            id="camera-start-stop-button",
                            className="m-1 d-md-block",
                        ),
                        dbc.Button(
                            VALUE_BUTTON_HR_IMAGE,
                            id="camera-hr-button",
                            n_clicks=0,
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

    row_hr_image = dbc.Row(
        [
            dbc.Col(
                [],
                id="col-hr-image",
                className="col-sm-9 col-12",
            ),
            dbc.Col(
                [
                    dbc.Button(
                        VALUE_BUTTON_SAVE_IMAGE,
                        id="camera-save-button",
                        className="m-1 d-md-block",
                    ),
                ],
                className="col-12 col-sm-3",
            ),
        ],
        id="row-hr-image",
        style={"display": "none"},
    )

    plots = dbc.Row(
        dbc.Col(
            [
                dcc.Graph(
                    figure=get_figure(),
                    id="plot-smd",
                    style={"display": "none", "margin": "0", "padding": "0"},
                ),
                dcc.Interval(id="interval-componente", interval=100),
            ]
        ),
        id="row-plots",
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
            plots,
            row_hr_image,
            offcanvas_transformations,
        ]
    )
    return layout


layout = _create_layout


# CALLBACKS
@app.callback(
    Output("camera-start-stop-button", "children"),
    Output("camera-save-button", "disabled", allow_duplicate=True),
    Input("camera-start-stop-button", "n_clicks"),
    prevent_initial_call=True,
)
def click_camera_start_stop_button(n_clicks):
    """Start-stop-button"""
    print(" - START-STOP-BUTTON:", cam.running)
    if cam.running():
        cam.stop()
        return VALUE_BUTTON_START, False
    else:
        cam.run()
        return VALUE_BUTTON_STOP, True


@app.callback(
    Output("camera-save-button", "disabled", allow_duplicate=True),
    Output("camera-save-button", "children", allow_duplicate=True),
    Input("camera-save-button", "n_clicks"),
    prevent_initial_call=True,
)
def click_camera_save_button(n_clicks):
    """Save-image-button"""
    filepath = os.path.join(PATH_TO_SAVE_IMAGES, "saved_image.jpg")
    print(" - SAVEFILE:", filepath)
    cam.save_stored_image_to_file(filepath)
    return True, VALUE_BUTTON_SAVED_IMAGE


@app.callback(
    Output("col-hr-image", "children"),
    Output("camera-save-button", "disabled", allow_duplicate=True),
    Output("camera-save-button", "children", allow_duplicate=True),
    Output("row-hr-image", "style"),
    Input("camera-hr-button", "n_clicks"),
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


@app.callback(
    Output("placeholder", "children", allow_duplicate=True),
    Input("checklist-basic-transformations", "value"),
    prevent_initial_call=True,
)
def set_basic_transformations(values):
    """Activation of Basic Tranformations"""
    cam.set_active_transformations("basic", values)
    return ""


@app.callback(
    Output("placeholder", "children", allow_duplicate=True),
    Input("checklist-post-transformations", "value"),
    prevent_initial_call=True,
)
def set_post_transformations(values):
    """Activation of Post Tranformations"""
    cam.set_active_transformations("post", values)
    return ""


## LIVE-UPDATES


@app.callback(Output("plot-smd", "figure"), Input("interval-componente", "n_intervals"))
def update_plots(n_intervals):
    print("N", n_intervals)
    return get_figure()


## REGISTERED TRANSFORMATION


def get_callback_for_checklist_of_registered_transformations(transformation):
    """Function factory returns callback-function for toggle switch to activate a transformation"""
    print("-register-")

    def func(values):
        """Activation of Regristered Transformations"""
        currently_active = set(cam.get_active_transformations("registered"))
        print(values)
        print(currently_active)
        if values:
            currently_active.add(transformation)
            style = {"display": "flex"}
        elif transformation in currently_active:
            currently_active.remove(transformation)
            style = {"display": "none"}
        else:
            style = {"display": "none"}
        cam.set_active_transformations("registered", list(currently_active))
        current_transformation = cam.get_transformation("registered", transformation)
        print(cam.get_active_transformations("registered"))
        print(current_transformation)
        return "", style

    return func


def get_callback_for_parameter_of_registered_transformation(transformation, parameter):
    """Function factory returns callback for input field for a parameter of a transformation"""

    def func(value):
        """Allows to set values of parameter of transformations"""
        print(f"- SET PARA {transformation} {parameter} ", value)
        cam.get_transformation("registered", transformation).parameter[
            parameter
        ].value = value

    return func


# For all registerd transformations callback for their activation and parameter are created
for transformation in cam.get_keys_of_transformations("registered"):
    print(" - register callback:", transformation)
    app.callback(
        Output("placeholder", "children", allow_duplicate=True),
        Output("plot-smd", "style", allow_duplicate=True),
        Input(f"checklist-registered-{transformation}-transformations", "value"),
        prevent_initial_call=True,
    )(get_callback_for_checklist_of_registered_transformations(transformation))
    for parameter in cam.get_transformation(
        "registered", transformation
    ).parameter.keys():
        print(" - register callback:", transformation, parameter)
        app.callback(
            Output("placeholder", "children", allow_duplicate=True),
            Input(f"input-parameter-{transformation}-{parameter}", "value"),
            prevent_initial_call=True,
        )(
            get_callback_for_parameter_of_registered_transformation(
                transformation, parameter
            )
        )
