from flask import Flask, request, jsonify

from configloader import config

app = Flask(__name__)

@app.route("/", methods=["GET"])
def get_index_file():
    index_file_dir = "web/index.html"
    with open(index_file_dir, "rb") as f:
        return f.read()

@app.route("/favicon.ico", methods=["GET"])
def get_favicon():
    favicon_file_dir = "web/favicon.ico"
    with open(favicon_file_dir, "rb") as f:
        return f.read()



@app.route("/api", methods=["GET"])
def api_index():
    return "No API QUERY specifiedd"

@app.route("/api/service", methods=["GET"])
def api_service_index():
    return "No API Service QUERY specified"

@app.route("/api/hardware", methods=["GET"])
def api_config_index():
    return "No API config QUERY specified"

@app.route("/api/hardware/fan", methods=["GET"])
def api_config_index():
    return "No API config QUERY specified"

@app.route("/api/hardware/fan", methods=["POST"])
def api_config_index():
    return "No API config QUERY specified"

@app.route("/api/hardware/screen", methods=["GET"])
def api_config_index():
    return "No API config QUERY specified"


@app.route("/api/config", methods=["GET"])
def api_config_index():
    return "No API config QUERY specified"

@app.route("/api/config/get", methods=["GET"])
def api_config_get():
    return "Not Complete"


if __name__ == '__main__':
    app.run(debug=True, port=config["WebServer"]["port"])