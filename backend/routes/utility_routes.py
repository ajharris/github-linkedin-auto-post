from flask import Blueprint, jsonify, current_app

utility_routes = Blueprint("utility_routes", __name__)

@utility_routes.route("/routes")
def list_routes():
    from flask import url_for

    output = []
    for rule in current_app.url_map.iter_rules():
        output.append(f"{rule.endpoint}: {rule.rule}")
    return jsonify(sorted(output))