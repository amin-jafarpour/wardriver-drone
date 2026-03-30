from datetime import datetime
import os
from flask import Flask, request, jsonify, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///records.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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

@app.route("/home", methods=["GET"])
def home():
    return jsonify({"status": "ok"}), 200

@app.route("/coords", methods=["GET"])
def get_coords():
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
    # if error:
    #     return jsonify({"message": error}), 400

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

@app.route("/remove/<int:record_id>", methods=["DELETE"])
def remove_record(record_id):
    record = db.session.get(Record, record_id)
    if not record:
        return jsonify({"message": "Record not found"}), 404

    db.session.delete(record)
    db.session.commit()

    return jsonify({"message": "Deleted"}), 200


######################################


def populate():
    with open(filePath, 'r') as file:
        content = file.read()
        ap_str_list = ap.WifiAPRecord.readCSV(content)
        record_list = []
        for ap_str in ap_str_list:
            try:
                record = WifiAPRecord.parse_obj(ap_str)
                record_list.append(record)
            except:
                    continue
        collection = ap.WifiAPRecordCollection(record_list)
        collection.filter_invalid_gps_coords()
        collection.filter_duplicates()
        filterd_records = collection.wifi_ap_records
        for record in filterd_records:
            record = app.Record(
            date=obj.date,
            time=obj.time,
            latitude=obj.latitude,
            longitude=obj.longitude,
            altitude=obj.altitude,
            speed=obj.speed,
            bssid=obj.bssid,
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
            app.db.session.add(record)
            app.db.session.commit()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']

    if file.filename == '':
        return "No selected file"

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        populate(filepath)
        return f"File uploaded to {filepath}"
    return "Invalid file type"

if __name__ == '__main__':
    app.run(debug=True)


# ----------------------
# Entry point
# ----------------------
if __name__ == "__main__":
    app.run(debug=True)

