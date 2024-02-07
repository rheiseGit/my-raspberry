"""
This module describes the basic structure of the application.
    - dash-multipage-features
    - navbar
"""

import dash
from dash import Dash, Output, State, Input, html, dcc, clientside_callback
import dash_bootstrap_components as dbc
from flask import Flask, redirect


# FLASK: used to redirect and set up videostream
server = Flask(__name__)


@server.route("/")
def root_redirect():
    return redirect("/welcome")


""" to be tested
dash.register_page(
    __name__,
    path="/welcome",
    redirect_from=["/"]
)
"""

# DASH: main framework used
# usage of multi-page feature (partially)
print("START")

app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[
        dbc.themes.FLATLY,
        dbc.icons.FONT_AWESOME,
        dbc.icons.BOOTSTRAP,
    ],
    suppress_callback_exceptions=True,
    server=server,
)

# ELEMENTS

# THEME SWITCH
color_mode_switch = [
    dbc.Label(className="fa fa-moon", html_for="switch"),
    dbc.Switch(
        id="switch-theme",
        value=True,
        className="d-inline-block ms-1",
        persistence=True,
    ),
    dbc.Label(className="fa fa-sun", html_for="switch"),
]


clientside_callback(
    """
    (switchOn) => {
       switchOn
         ? document.documentElement.setAttribute('data-bs-theme', 'light')
         : document.documentElement.setAttribute('data-bs-theme', 'dark')
       return window.dash_clientside.no_update
    }
    """,
    Output("switch-theme", "id"),
    Input("switch-theme", "value"),
)

# NAVBAR
# The Creation of navbar including the pages defined in folder pages
# Pages with the prefix "feature" in there will appear in the section features
# else in seaction onformation

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
                "Videostream",
                href="/stream",
            )
        ),
        dbc.DropdownMenu(
            dropdown_menu_item_list,
            nav=True,
            in_navbar=True,
            label="Content",
        ),
        dbc.DropdownMenu(
            [dbc.DropdownMenuItem(color_mode_switch, header=True)],
            nav=True,
            in_navbar=True,
            label=dbc.Label(className="bi bi-gear-fill"),
        ),
        dbc.NavItem(
            dbc.NavLink(
                dbc.Label(className="bi bi-github"),
                href="https://github.com/rheiseGit/my-raspberry",
            ),
        ),
    ],
    brand="MyRaspberry",
    brand_href="/welcome",
    color="primary",
    dark=True,
    sticky="top",
    className="py-1",
)

# LAYOUT
app.layout = html.Div(
    [
        dcc.Location(id="url"),
        navbar,
        dbc.Container(dash.page_container, style={"margin-top": 10}),
        html.Div(id="placeholder"),  # empty placeholder for callbacks without output
    ]
)


# CALLBACKS
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    """toggle bar collapse"""
    if n:
        return not is_open
    return is_open
