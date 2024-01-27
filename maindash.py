# defines app, server
import dash
from dash import Dash, Output, Input, html, dcc, clientside_callback
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeChangerAIO, ThemeSwitchAIO, template_from_url
from flask import Flask, redirect

# FLASK: used to redirect and set up videostream
server = Flask(__name__)


@server.route("/")
def root_redirect():
    return redirect("/welcome")


# DASH: main framework used
# usage of multi-page feature (partially)
print("START")

dbc_css = (
    "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.1/dbc.min.css"
)

template_theme1 = "flatly"
template_theme2 = "darkly"
url_theme1 = dbc.themes.FLATLY
# url_theme1 = dbc.themes.MINTY
url_theme2 = dbc.themes.DARKLY
# url_theme2 = dbc.themes.SLATE

app = Dash(
    __name__,
    use_pages=True,
    # external_stylesheets=[dbc.themes.DARKLY, dbc_css],
    external_stylesheets=[
        dbc.themes.FLATLY,
        dbc.icons.FONT_AWESOME,
        dbc.icons.BOOTSTRAP,
        dbc_css,
    ],
    suppress_callback_exceptions=True,
    server=server,
)

# THEME SWITCH
color_mode_switch = [
    # dbc.Label(className="fa fa-moon", html_for="switch"),
    dbc.Switch(
        id="switch-theme",
        value=True,
        className="d-inline-block ms-1",
        persistence=True,
    ),
    # dbc.Label(className="fa fa-sun", html_for="switch"),
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
    # + [dbc.DropdownMenuItem(dbc.Container(ThemeSwitchAIO(aio_id="theme", themes=[url_theme1, url_theme2])),)]
)

navbar = dbc.NavbarSimple(
    children=[
        dbc.DropdownMenu(
            dropdown_menu_item_list,
            nav=True,
            in_navbar=True,
            label="Content",
        ),
        dbc.NavItem(
            dbc.NavLink(
                dbc.Label(className="bi bi-gear"),
            )
        ),
        dbc.NavItem(
            dbc.NavLink(
                dbc.Label(className="bi bi-github"),
                href="https://github.com/rheiseGit/my-raspberry",
            )
        ),
        dbc.NavItem(
            color_mode_switch,
            style={"margin": "auto"},
        ),
        # dbc.NavItem(
        #    dbc.NavLink(
        #        html.Img(
        #            src=dash.get_asset_url("github-mark.svg"),
        #            style={"height": "25px"},
        #        ),
        #        href="https://github.com/rheiseGit/my-raspberry",
        #    )
        # ),
        # dbc.NavItem(
        #    dbc.NavLink("GitHub", href="https://github.com/rheiseGit/my-raspberry")
        # ),
    ],
    brand="MyRaspberry",
    brand_href="/welcome",
    color="primary",
    dark=True,
    sticky="top",
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

offcanvas = dbc.Offcanvas(
    html.P(
        "This is the content of the Offcanvas. "
        "Close it by clicking on the close button, or "
        "the backdrop."
    ),
    id="offcanvas",
    title="Title",
    is_open=False,
)

app.layout = html.Div(
    [
        dcc.Location(id="url"),
        navbar,
        offcanvas,
        dbc.Container(dash.page_container, style={"margin-top": 20}),
        html.Div(id="placeholder"),  # empty placeholder for callbacks without output
    ]
)
