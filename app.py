import secrets
import sys
from pathlib import Path

from flask import (
    Flask,
    Response,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from automation import run_login_in_thread
from storage import add_credential, get_credential, load_credentials, remove_credential
from importer import build_template, parse_import
from tools import TOOLS, get_tool

_BASE_DIR = (
    Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    if getattr(sys, "frozen", False)
    else Path(__file__).parent
)

app = Flask(__name__, template_folder=str(_BASE_DIR / "templates"))
app.secret_key = secrets.token_hex(16)


@app.route("/template")
def download_template():
    return Response(
        build_template(),
        mimetype=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": "attachment; "
            "filename=credentials_template.xlsx"
        },
    )


@app.route("/import", methods=["POST"])
def import_credentials():
    file = request.files.get("file")

    if not file or not file.filename:
        flash("Please choose an .xlsx file to import.", "error")
        return redirect(url_for("manage_credentials"))

    try:
        created, errors = parse_import(file.stream)
    except ValueError as e:
        flash(str(e), "error")
        return redirect(url_for("manage_credentials"))

    for tool_key, username, password in created:
        add_credential(tool_key, username, password)

    if created:
        flash(f"Imported {len(created)} credential(s).", "success")

    for row, message in errors:
        flash(f"Row {row}: {message}", "error")

    if not created and not errors:
        flash("The file contains no data to import.", "error")

    return redirect(url_for("manage_credentials"))


@app.context_processor
def inject_tools():
    return {"TOOLS": TOOLS}


@app.route("/")
def index():
    credentials = load_credentials()

    accents = {
        "gst": "#ff9800",
        "incometax": "#1971c2",
        "tds": "#0c8599",
    }

    tools = []
    for key, tool in TOOLS.items():
        account_count = len(credentials.get(key, []))
        tools.append(
            {
                **tool,
                "account_count": account_count,
                "accent": accents.get(key, "#1b6a50"),
            }
        )

    return render_template("index.html", tools=tools, active=None)


@app.route("/manage")
def manage_credentials():
    credentials = load_credentials()

    groups = [
        (tool, credentials.get(tool["key"], []))
        for tool in TOOLS.values()
    ]

    return render_template(
        "manage.html",
        groups=groups,
        active="manage",
    )


@app.route("/tool/<tool_key>")
def tool_page(tool_key):
    tool = get_tool(tool_key)
    if not tool:
        abort(404)

    accounts = load_credentials().get(tool_key, [])

    accents = {
        "gst": "#ff9800",
        "incometax": "#1971c2",
        "tds": "#0c8599",
    }

    return render_template(
        "tool_detail.html",
        tool=tool,
        accounts=accounts,
        active=tool_key,
        accent=accents.get(tool_key, "#1b6a50"),
    )


@app.route("/save", methods=["POST"])
def save_credential():
    tool_key = request.form["tool"]

    if not get_tool(tool_key):
        abort(404)

    add_credential(
        tool_key,
        request.form["username"],
        request.form["password"],
    )

    return redirect(url_for("manage_credentials"))


@app.route("/delete", methods=["POST"])
def delete_credential():
    tool_key = request.form["tool"]

    if not get_tool(tool_key):
        abort(404)

    remove_credential(tool_key, request.form["username"])

    return redirect(url_for("manage_credentials"))


@app.route("/tool/<tool_key>/login", methods=["POST"])
def login_run(tool_key):
    tool = get_tool(tool_key)
    if not tool:
        abort(404)

    username = request.form["username"]

    config = tool

    if tool.get("subtypes"):
        subtype_key = request.form.get("subtype") or tool["subtypes"][0]["key"]
        subtype = next(
            (s for s in tool["subtypes"] if s["key"] == subtype_key),
            None,
        )

        if not subtype:
            abort(404)

        config = {**tool, **subtype}

    credentials = get_credential(tool_key, username)

    if credentials:
        run_login_in_thread(config, *credentials)

    return redirect(url_for("tool_page", tool_key=tool_key))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)