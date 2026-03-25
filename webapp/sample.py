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