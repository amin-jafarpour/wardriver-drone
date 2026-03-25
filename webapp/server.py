from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException

app = Flask(__name__)

# Simple in-memory storage
items = {}
next_id = 1


def validate_item_payload(data, require_all_fields=True):
    """
    Validate incoming JSON payload for an item.
    Expected shape:
    {
        "name": "example",
        "description": "optional text"
    }
    """
    if not isinstance(data, dict):
        return "Request body must be a JSON object."

    if require_all_fields and "name" not in data:
        return "Field 'name' is required."

    if "name" in data and not isinstance(data["name"], str):
        return "Field 'name' must be a string."

    if "name" in data and not data["name"].strip():
        return "Field 'name' cannot be empty."

    if "description" in data and not isinstance(data["description"], str):
        return "Field 'description' must be a string."

    return None


@app.errorhandler(HTTPException)
def handle_http_exception(e):
    return jsonify({
        "error": e.name,
        "message": e.description,
        "status": e.code
    }), e.code


@app.errorhandler(Exception)
def handle_general_exception(e):
    return jsonify({
        "error": "Internal Server Error",
        "message": str(e),
        "status": 500
    }), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "message": "API is running"
    }), 200


@app.route("/items", methods=["GET"])
def get_items():
    return jsonify({
        "items": list(items.values()),
        "count": len(items)
    }), 200


@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = items.get(item_id)
    if not item:
        return jsonify({"message": "Item not found"}), 404

    return jsonify(item), 200


@app.route("/items", methods=["POST"])
def create_item():
    global next_id

    data = request.get_json(silent=True)
    error = validate_item_payload(data, require_all_fields=True)
    if error:
        return jsonify({"message": error}), 400

    item = {
        "id": next_id,
        "name": data["name"].strip(),
        "description": data.get("description", "").strip()
    }

    items[next_id] = item
    next_id += 1

    return jsonify(item), 201


@app.route("/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    item = items.get(item_id)
    if not item:
        return jsonify({"message": "Item not found"}), 404

    data = request.get_json(silent=True)
    error = validate_item_payload(data, require_all_fields=False)
    if error:
        return jsonify({"message": error}), 400

    if "name" in data:
        item["name"] = data["name"].strip()

    if "description" in data:
        item["description"] = data["description"].strip()

    return jsonify(item), 200


@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = items.pop(item_id, None)
    if not item:
        return jsonify({"message": "Item not found"}), 404

    return jsonify({
        "message": "Item deleted successfully",
        "deleted_item": item
    }), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

#########################

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

app = Flask(__name__)

# SQLite configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///items.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


# ----------------------
# Database Model
# ----------------------
class Item(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat()
        }


# ----------------------
# Validation
# ----------------------
def validate_payload(data, require_name=True):
    if not data:
        return "Invalid JSON body"

    if require_name and "name" not in data:
        return "Field 'name' is required"

    if "name" in data:
        if not isinstance(data["name"], str) or not data["name"].strip():
            return "Field 'name' must be a non-empty string"

    if "description" in data and not isinstance(data["description"], str):
        return "Field 'description' must be a string"

    return None


# ----------------------
# Routes
# ----------------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/items", methods=["GET"])
def get_items():
    items = Item.query.all()
    return jsonify([item.to_dict() for item in items]), 200


@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"message": "Item not found"}), 404

    return jsonify(item.to_dict()), 200


@app.route("/items", methods=["POST"])
def create_item():
    data = request.get_json()
    error = validate_payload(data)
    if error:
        return jsonify({"message": error}), 400

    item = Item(
        name=data["name"].strip(),
        description=data.get("description", "").strip()
    )

    db.session.add(item)
    db.session.commit()

    return jsonify(item.to_dict()), 201


@app.route("/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"message": "Item not found"}), 404

    data = request.get_json()
    error = validate_payload(data, require_name=False)
    if error:
        return jsonify({"message": error}), 400

    if "name" in data:
        item.name = data["name"].strip()

    if "description" in data:
        item.description = data["description"].strip()

    db.session.commit()

    return jsonify(item.to_dict()), 200


@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"message": "Item not found"}), 404

    db.session.delete(item)
    db.session.commit()

    return jsonify({"message": "Deleted"}), 200


# ----------------------
# Entry point
# ----------------------
if __name__ == "__main__":
    app.run(debug=True)


# flask db init
# flask db migrate -m "Initial migration"
# flask db upgrade
# export FLASK_APP=app.py
