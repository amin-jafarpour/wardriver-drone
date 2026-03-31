import os
from datetime import datetime
from flask import Flask, request, jsonify, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import werkzeug.utils
import ap

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'txt', 'csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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
    ssid = db.Column(db.String(MAX_STR_LEN), nullable=True)
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
            'ssid': self.ssid,
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

def populate_db(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        ap_str_list = ap.WifiAPRecord.readCSV(content)
        record_list = []
        for ap_str in ap_str_list:
            try:
                record = ap.WifiAPRecord.parse_obj(ap_str)
                record_list.append(record)
            except Exception as e:    
                    continue
        collection = ap.WifiAPRecordCollection(record_list)
        collection.filter_invalid_gps_coords()
        collection.filter_duplicates()
        # collection.trilaterate()
        collection.speard_out()
        filterd_records = collection.wifi_ap_records
        for obj in filterd_records:
            record = Record(
            date=obj.date,
            time=obj.time,
            latitude=obj.latitude,
            longitude=obj.longitude,
            altitude=obj.altitude,
            speed=obj.speed,
            bssid=obj.bssid,
            ssid=obj.ssid,
            primary_channel=obj.primary_channel,
            second_channel=obj.second_channel,
            rssi=obj.rssi,
            authmode=obj.authmode,
            pairwise_cipher=obj.pairwise_cipher,
            group_cipher=obj.group_cipher,
            ant=obj.ant,
            country_code=obj.country_code,
            country_start_channel=obj.country_start_channel,
            country_end_channel=obj.country_end_channel,
            max_tx_power=obj.max_tx_power,
            country_policy=obj.country_policy,
            wifi_AP_HE=obj.wifi_AP_HE,
            bss_color=obj.bss_color,
            partial_bss_color=obj.partial_bss_color,
            bss_color_disabled=obj.bss_color_disabled,
            bssid_index=obj.bssid_index,
            bandwidth=obj.bandwidth,
            vht_ch_freq1=obj.vht_ch_freq1,
            vht_ch_freq2=obj.vht_ch_freq2)
            db.session.add(record)
            db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/page", methods=["POST"])
def get_page():
    min_lat = request.form.get('min_lat', type=float)
    max_lat = request.form.get('max_lat', type=float)
    min_lon = request.form.get('min_lon', type=float)
    max_lon = request.form.get('max_lon', type=float)

    records = Record.query.filter(
        Record.latitude.between(min_lat, max_lat),
        Record.longitude.between(min_lon, max_lon)
    ).all()

    return jsonify([record.to_dict() for record in records]), 200

@app.route("/get", methods=["POST"])
def get_record():
    record_id = request.form.get('record_id')
    record = db.session.get(Record, record_id)
    if not record:
        return jsonify({"message": "record not found"}), 404

    return jsonify(record.to_dict()), 200

@app.route("/remove/<int:record_id>", methods=["DELETE"])
def remove_record(record_id):
    record = db.session.get(Record, record_id)
    if not record:
        return jsonify({"message": "Record not found"}), 404

    db.session.delete(record)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 200

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"
    file = request.files['file']
    if file.filename == '':
        return "No selected file"

    allowed_file = lambda filename: '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    if file and allowed_file(file.filename):
        filename =  werkzeug.utils.secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        populate_db(filepath)
        return f"File uploaded to {filepath}"
    return "Invalid file type"


@app.route("/cleardb", methods=["DELETE"])
def clear_db():
    db.session.query(Record).delete()
    db.session.commit()
    return {"message": "All records deleted"}, 200

# ----------------------
# Entry point
# ----------------------
if __name__ == "__main__":
    app.run(debug=True)

