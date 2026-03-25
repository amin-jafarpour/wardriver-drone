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
class Record(db.Model):
    __tablename__ = "records"

    MAX_STR_LEN = 50

    # Required fields
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    date = db.Column(db.Date, nullable=False, nullable=False)
    time = db.Column(db.Time, nullable=False, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    altitude = db.Column(db.Float, nullable=False)
    speed = db.Column(db.Float, nullable=False)
    bssid = db.Column(db.String(17), nullable=False)
    # Optional fields
    bssid = db.Column(db.String(32), nullable=True)
    primary_channel = db.Column(db.Integer, nullable=True)
    second_channel = db.Column(db.String(MAX_STR_LEN), nullable=True)
    rssi = db.Column(db.Integer, nullable=True)
    authmode = second_channel = db.Column(db.String(MAX_STR_LEN), nullable=True)
    pairwise_cipher = db.Column(db.String(MAX_STR_LEN), nullable=True)
    group_cipher = db.Column(db.String(MAX_STR_LEN), nullable=True)
    ant = db.Column(db.String(MAX_STR_LEN), nullable=True)
    country_code = db.Column(db.String(MAX_STR_LEN), nullable=True)
    country_start_channel = db.Column(db.Integer, nullable=True)
    country_end_channel = db.Column(db.Integer, nullable=True)
    max_tx_power = db.Column(db.Integer, nullable=True)
    country_policy = db.Column(db.String(MAX_STR_LEN), nullable=True)
    wifi_AP_HE = db.Column(db.Integer, nullable=True)
    bss_color = db.Column(db.Integer, nullable=True)
    partial_bss_color = db.Column(db.Integer, nullable=True)
    bss_color_disabled = db.Column(db.Integer, nullable=True)
    bssid_index = db.Column(db.String(MAX_STR_LEN), nullable=True)
    bandwidth = db.Column(db.String(MAX_STR_LEN), nullable=True)
    vht_ch_freq1 = db.Column(db.Integer, nullable=True)
    vht_ch_freq2 = db.Column(db.Integer, nullable=True)

    def to_dict(self):
        return {
            # Required fields
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,   # YYYY-MM-DD
            'time': self.time.isoformat() if self.time else None    # HH:MM:SS
            'latitude' = latitude
            'longitude' = longitude
            'altitude' = altitude
            'speed' = speed
            'bssid' = bssid
            # Optional fields
            'primary_channel' = primary_channel
            'second_channel' = second_channel
            'rssi' = rssi
            'authmode' = authmode
            'pairwise_cipher' = pairwise_cipher
            'group_cipher' = group_cipher
            'ant' = ant
            'country_code' = country_code
            'country_start_channel' = country_start_channel
            'country_end_channel' = country_end_channel
            'max_tx_power' = max_tx_power
            'country_policy' = country_policy
            'wifi_AP_HE' = wifi_AP_HE
            'bss_color' = bss_color
            'partial_bss_color' = partial_bss_color
            'bss_color_disabled' = bss_color_disabled
            'bssid_index' = bssid_index
            'bandwidth' = bandwidth
            'vht_ch_freq1' = vht_ch_freq1
            'vht_ch_freq2' = vht_ch_freq2
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
@app.route("/text", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/records", methods=["GET"])
def get_items():
    items = Record.query.all()
    return jsonify([item.to_dict() for record in records]), 200


@app.route("/records/<int:record_id>", methods=["GET"])
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