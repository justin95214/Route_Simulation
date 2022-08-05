import dash
from dash import html

dash.register_page(__name__, path_template="/<location>/<report_id>")


def layout(report_id=None, location=None):
    return html.Div(
        f"The user requested report ID: {location} {report_id}."
    )

