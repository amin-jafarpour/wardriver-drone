from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///records.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Record(db.Model):
    __tablename__ = "records"
    MAX_STR_LEN = 50
    MAC_ADDR_STR_LEN = 17

    # Required fields
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    altitude = db.Column(db.Float, nullable=False)
    speed = db.Column(db.Float, nullable=False)
    bssid = db.Column(db.String(MAC_ADDR_STR_LEN), nullable=False)
    # Optional fields
    primary_channel = db.Column(db.Integer, nullable=True)
    second_channel = db.Column(db.String(MAX_STR_LEN), nullable=True)
    rssi = db.Column(db.Integer, nullable=True)
    authmode = db.Column(db.String(MAX_STR_LEN), nullable=True)
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
            'time': self.time.isoformat() if self.time else None,   # HH:MM:SS
            'latitude': self.latitude, 
            'longitude': self.longitude, 
            'altitude': self.altitude, 
            'speed': self.speed, 
            'bssid':self.bssid, 
            # Optional fields
            'primary_channel': self.primary_channel, 
            'second_channel':self.second_channel, 
            'rssi': self.rssi, 
            'authmode': self.authmode, 
            'pairwise_cipher': self.pairwise_cipher, 
            'group_cipher': self.group_cipher, 
            'ant': self.ant, 
            'country_code': self.country_code, 
            'country_start_channel': self.country_start_channel, 
            'country_end_channel': self.country_end_channel, 
            'max_tx_power': self.max_tx_power, 
            'country_policy' : self.country_policy, 
            'wifi_AP_HE': self.wifi_AP_HE, 
            'bss_color': self.bss_color, 
            'partial_bss_color': self.partial_bss_color, 
            'bss_color_disabled': self.bss_color_disabled, 
            'bssid_index': self.bssid_index, 
            'bandwidth': self.bandwidth, 
            'vht_ch_freq1': self.vht_ch_freq1, 
            'vht_ch_freq2': self.vht_ch_freq2, 
        }

def validate_payload(data, require_name=True):
    return None

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok"}), 200

@app.route("/coords", methods=["GET"])
def get_coords():
    # records = Record.query.all()
    records = db.session.query(
        Record.id,
        Record.date,
        Record.time,
        Record.latitude,
        Record.longitude,
        Record.altitude,
        Record.speed,
        Record.bssid
    ).all()

    return jsonify([
        {
            'id': record.id,
            'date': record.date.isoformat() if record.date else None,
            'time': record.time.isoformat() if record.time else None,
            'latitude': record.latitude,
            'longitude': record.longitude,
            'altitude': record.altitude,
            'speed': record.speed,
            'bssid': record.bssid
        }
        for record in records
    ]), 200

@app.route("/get/<int:record_id>", methods=["GET"])
def get_record(record_id):
    record = db.session.get(Record, record_id)
    if not record:
        return jsonify({"message": "record not found"}), 404

    return jsonify(record.to_dict()), 200

@app.route("/add", methods=["POST"])
def add_record():
    data = request.get_json()
    error = validate_payload(data)
    if error:
        return jsonify({"message": error}), 400

    record = Record(
        date = datetime.strptime(data.get('date'), "%Y-%m-%d").date(),
        time = datetime.strptime(data.get('time'), "%H:%M:%S").time(),
        latitude = data.get('latitude'),
        longitude = data.get('longitude'),
        altitude = data.get('altitude'),
        speed = data.get('speed'),
        bssid = data.get('bssid'),
        primary_channel = data.get('primary_channel'),
        second_channel = data.get('second_channel'),
        rssi = data.get('rssi'),
        authmode = data.get('authmode'),
        pairwise_cipher = data.get('pairwise_cipher'),
        group_cipher = data.get('group_cipher'),
        ant = data.get('ant'),
        country_code = data.get('country_code'),
        country_start_channel = data.get('country_start_channel'),
        country_end_channel = data.get('country_end_channel'),
        max_tx_power = data.get('max_tx_power'),
        country_policy = data.get('country_policy'),
        wifi_AP_HE = data.get('wifi_AP_HE'),
        bss_color = data.get('bss_color'),
        partial_bss_color = data.get('partial_bss_color'),
        bss_color_disabled = data.get('bss_color_disabled'),
        bssid_index = data.get('bssid_index'),
        bandwidth = data.get('bandwidth'),
        vht_ch_freq1 = data.get('vht_ch_freq1'),
        vht_ch_freq2 = data.get('vht_ch_freq2'),
    )

    db.session.add(record)
    db.session.commit()

    return jsonify(record.to_dict()), 201


@app.route("/update/<int:record_id>", methods=["PUT"])
def update_record(record_id):
    record = db.session.get(Record, record_id)
    if not record:
        return jsonify({"message": "Record not found"}), 404

    data = request.get_json()
    error = validate_payload(data, require_name=False)
    if error:
        return jsonify({"message": error}), 400
    record.latitude = data.get("latitude", record.latitude)

    db.session.commit()
    return jsonify(record.to_dict()), 200


@app.route("/remove/<int:record_id>", methods=["DELETE"])
def remove_record(record_id):
    record = db.session.get(Record, record_id)
    if not record:
        return jsonify({"message": "Record not found"}), 404

    db.session.delete(record)
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