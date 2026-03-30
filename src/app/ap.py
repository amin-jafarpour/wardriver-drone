from enum import Enum
from datetime import datetime
import csv
import io

# https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/network/esp_wifi.html#_CPPv416wifi_ap_record_t

class WifiSecondChan(Enum): 
    # The channel width is HT20 
    WIFI_SECOND_CHAN_NONE = "WIFI_SECOND_CHAN_NONE"
    # The channel width is HT40 and the secondary channel is above the primary channel 
    WIFI_SECOND_CHAN_ABOVE = "WIFI_SECOND_CHAN_ABOVE"
    # The channel width is HT40 and the secondary channel is below the primary channel
    WIFI_SECOND_CHAN_BELOW = "WIFI_SECOND_CHAN_BELOW"
    # Placeholder for the default option and unexpected values
    WIFI_SECOND_CHAN_ERROR = "WIFI_SECOND_CHAN_ERROR"

class WifiAuthMode(Enum):
    # Personal Networks: OPEN < WEP < WPA_PSK < OWE < WPA2_PSK = WPA_WPA2_PSK < WAPI_PSK < WPA3_PSK = WPA2_WPA3_PSK.
    # Enterprise Networks: WIFI_AUTH_WPA_ENTERPRISE < WIFI_AUTH_WPA2_ENTERPRISE < WIFI_AUTH_WPA3_ENTERPRISE/WIFI_AUTH_WPA2_WPA3_ENT    # ERPRISE < WIFI_AUTH_WPA3_ENT_192. 
    WIFI_AUTH_OPEN = "WIFI_AUTH_OPEN"
    WIFI_AUTH_WEP = "WIFI_AUTH_WEP"
    WIFI_AUTH_WPA_PSK = "WIFI_AUTH_WPA_PSK"
    WIFI_AUTH_WPA2_PSK = "WIFI_AUTH_WPA2_PSK"
    WIFI_AUTH_WPA_WPA2_PSK = "WIFI_AUTH_WPA_WPA2_PSK"
    # Wi-Fi EAP security is treated the same as WIFI_AUTH_WPA2_ENTERPRISE 
    WIFI_AUTH_ENTERPRISE = "WIFI_AUTH_ENTERPRISE"
    WIFI_AUTH_WPA2_ENTERPRISE = "WIFI_AUTH_WPA2_ENTERPRISE"
    WIFI_AUTH_WPA3_PSK = "WIFI_AUTH_WPA3_PSK"
    WIFI_AUTH_WPA2_WPA3_PSK = "WIFI_AUTH_WPA2_WPA3_PSK"
    WIFI_AUTH_WAPI_PSK = "WIFI_AUTH_WAPI_PSK"
    WIFI_AUTH_OWE = "WIFI_AUTH_OWE"
    WIFI_AUTH_WPA3_ENT_192 = "WIFI_AUTH_WPA3_ENT_192"
    # Same as WIFI_AUTH_WPA3_PSK but deprecated
    WIFI_AUTH_WPA3_EXT_PSK = "WIFI_AUTH_WPA3_EXT_PSK"
    # Same as WIFI_AUTH_WPA3_PSK but deprecated
    WIFI_AUTH_WPA3_EXT_PSK_MIXED_MODE = "WIFI_AUTH_WPA3_EXT_PSK_MIXED_MODE"
    WIFI_AUTH_DPP = "WIFI_AUTH_DPP"
    # WPA3-Enterprise Only Mode 
    WIFI_AUTH_WPA3_ENTERPRISE = "WIFI_AUTH_WPA3_ENTERPRISE"
    # WPA3-Enterprise Transition Mode 
    WIFI_AUTH_WPA2_WPA3_ENTERPRISE = "WIFI_AUTH_WPA2_WPA3_ENTERPRISE"
    WIFI_AUTH_WPA_ENTERPRISE = "WIFI_AUTH_WPA_ENTERPRISE"
    # Invalid authmode
    WIFI_AUTH_MAX = "WIFI_AUTH_MAX" 
    # Placeholder for the default option and unexpected values
    UNKNOWN_AUTH_ERROR = "UNKNOWN_AUTH_ERROR"

class PairwiseCipherType(Enum):
    WIFI_CIPHER_TYPE_NONE = "WIFI_CIPHER_TYPE_NONE"
    WIFI_CIPHER_TYPE_WEP40 = "WIFI_CIPHER_TYPE_WEP40"
    WIFI_CIPHER_TYPE_WEP104 = "WIFI_CIPHER_TYPE_WEP104"
    WIFI_CIPHER_TYPE_TKIP = "WIFI_CIPHER_TYPE_TKIP"
    WIFI_CIPHER_TYPE_CCMP = "WIFI_CIPHER_TYPE_CCMP"
    WIFI_CIPHER_TYPE_TKIP_CCMP = "WIFI_CIPHER_TYPE_TKIP_CCMP"
    WIFI_CIPHER_TYPE_AES_CMAC128 = "WIFI_CIPHER_TYPE_AES_CMAC128"
    WIFI_CIPHER_TYPE_SMS4 = "WIFI_CIPHER_TYPE_SMS4"
    WIFI_CIPHER_TYPE_GCMP = "WIFI_CIPHER_TYPE_GCMP"
    WIFI_CIPHER_TYPE_GCMP256 = "WIFI_CIPHER_TYPE_GCMP256"
    WIFI_CIPHER_TYPE_AES_GMAC128 = "WIFI_CIPHER_TYPE_AES_GMAC128"
    WIFI_CIPHER_TYPE_AES_GMAC256 = "WIFI_CIPHER_TYPE_AES_GMAC256"
    WIFI_CIPHER_TYPE_UNKNOWN = "WIFI_CIPHER_TYPE_UNKNOWN"
    # Placeholder for the default option and unexpected values
    WIFI_CIPHER_TYPE_ERROR = "WIFI_CIPHER_TYPE_ERROR"

class GroupCipherType(Enum):
    WIFI_CIPHER_TYPE_NONE = "WIFI_CIPHER_TYPE_NONE"
    WIFI_CIPHER_TYPE_WEP40 = "WIFI_CIPHER_TYPE_WEP40"
    WIFI_CIPHER_TYPE_WEP104 = "WIFI_CIPHER_TYPE_WEP104"
    WIFI_CIPHER_TYPE_TKIP = "WIFI_CIPHER_TYPE_TKIP"
    WIFI_CIPHER_TYPE_CCMP = "WIFI_CIPHER_TYPE_CCMP"
    WIFI_CIPHER_TYPE_TKIP_CCMP = "WIFI_CIPHER_TYPE_TKIP_CCMP"
    WIFI_CIPHER_TYPE_AES_CMAC128 = "WIFI_CIPHER_TYPE_AES_CMAC128"
    WIFI_CIPHER_TYPE_SMS4 = "WIFI_CIPHER_TYPE_SMS4"
    WIFI_CIPHER_TYPE_GCMP = "WIFI_CIPHER_TYPE_GCMP"
    WIFI_CIPHER_TYPE_GCMP256 = "WIFI_CIPHER_TYPE_GCMP256"
    WIFI_CIPHER_TYPE_AES_GMAC128 = "WIFI_CIPHER_TYPE_AES_GMAC128"
    WIFI_CIPHER_TYPE_AES_GMAC256 = "WIFI_CIPHER_TYPE_AES_GMAC256"
    WIFI_CIPHER_TYPE_UNKNOWN = "WIFI_CIPHER_TYPE_UNKNOWN"
    # Placeholder for the default option and unexpected values
    WIFI_CIPHER_TYPE_ERROR = "WIFI_CIPHER_TYPE_ERROR"

# Wi-Fi antenna
class Ant(Enum):
    # Wi-Fi antenna 0 
    WIFI_ANT_ANT0 = "WIFI_ANT_ANT0"
    # Wi-Fi antenna 1 
    WIFI_ANT_ANT1 = "WIFI_ANT_ANT1"
    # Invalid Wi-Fi antenna 
    WIFI_ANT_MAX = "WIFI_ANT_MAX"
    # Placeholder for the default option and unexpected values
    WIFI_ANT_ERROR = "WIFI_ANT_ERROR"

class WiFiCountryCode(Enum):
    AT = "AT"
    AU = "AU"
    BE = "BE"
    BG = "BG"
    BR = "BR"
    CA = "CA"
    CH = "CH"
    CN = "CN"
    CY = "CY"
    CZ = "CZ"
    DE = "DE"
    DK = "DK"
    EE = "EE"
    ES = "ES"
    FI = "FI"
    FR = "FR"
    GB = "GB"
    GR = "GR"
    HK = "HK"
    HR = "HR"
    HU = "HU"
    IE = "IE"
    IN = "IN"
    IS = "IS"
    IT = "IT"
    JP = "JP"
    KR = "KR"
    LI = "LI"
    LT = "LT"
    LU = "LU"
    LV = "LV"
    MT = "MT"
    MX = "MX"
    NL = "NL"
    NO = "NO"
    NZ = "NZ"
    PL = "PL"
    PT = "PT"
    RO = "RO"
    SE = "SE"
    SI = "SI"
    SK = "SK"
    TW = "TW"
    US = "US"
    _01 = "01"

country_code_mapping = {
    WiFiCountryCode.AT: "Austria",
    WiFiCountryCode.AU: "Australia",
    WiFiCountryCode.BE: "Belgium",
    WiFiCountryCode.BG: "Bulgaria",
    WiFiCountryCode.BR: "Brazil",
    WiFiCountryCode.CA: "Canada",
    WiFiCountryCode.CH: "Switzerland",
    WiFiCountryCode.CN: "China",
    WiFiCountryCode.CY: "Cyprus",
    WiFiCountryCode.CZ: "Czech Republic",
    WiFiCountryCode.DE: "Germany",
    WiFiCountryCode.DK: "Denmark",
    WiFiCountryCode.EE: "Estonia",
    WiFiCountryCode.ES: "Spain",
    WiFiCountryCode.FI: "Finland",
    WiFiCountryCode.FR: "France",
    WiFiCountryCode.GB: "United Kingdom",
    WiFiCountryCode.GR: "Greece",
    WiFiCountryCode.HK: "Hong Kong",
    WiFiCountryCode.HR: "Croatia",
    WiFiCountryCode.HU: "Hungary",
    WiFiCountryCode.IE: "Ireland",
    WiFiCountryCode.IN: "India",
    WiFiCountryCode.IS: "Iceland",
    WiFiCountryCode.IT: "Italy",
    WiFiCountryCode.JP: "Japan",
    WiFiCountryCode.KR: "South Korea",
    WiFiCountryCode.LI: "Liechtenstein",
    WiFiCountryCode.LT: "Lithuania",
    WiFiCountryCode.LU: "Luxembourg",
    WiFiCountryCode.LV: "Latvia",
    WiFiCountryCode.MT: "Malta",
    WiFiCountryCode.MX: "Mexico",
    WiFiCountryCode.NL: "Netherlands",
    WiFiCountryCode.NO: "Norway",
    WiFiCountryCode.NZ: "New Zealand",
    WiFiCountryCode.PL: "Poland",
    WiFiCountryCode.PT: "Portugal",
    WiFiCountryCode.RO: "Romania",
    WiFiCountryCode.SE: "Sweden",
    WiFiCountryCode.SI: "Slovenia",
    WiFiCountryCode.SK: "Slovakia",
    WiFiCountryCode.TW: "Taiwan",
    WiFiCountryCode.US: "United States",
    WiFiCountryCode._01: "World Safe Mode"
}

class WifiCountryPolicy(Enum):
    # Country policy is auto, use the country info of AP to which the station is connected 
    WIFI_COUNTRY_POLICY_AUTO = "WIFI_COUNTRY_POLICY_AUTO"
    # Country policy is manual, always use the configured country info 
    WIFI_COUNTRY_POLICY_MANUAL = "WIFI_COUNTRY_POLICY_MANUAL"
    # Placeholder for the default option and unexpected value
    WIFI_COUNTRY_POLICY_ERROR = "WIFI_COUNTRY_POLICY_ERROR"

class WifiBandwidth(Enum): 
    # Bandwidth is HT20 
    WIFI_BW_HT20 = "WIFI_BW_HT20"
    # Bandwidth is 20 MHz 
    WIFI_BW20 = "WIFI_BW20"
    # Bandwidth is HT40 
    WIFI_BW_HT40 = "WIFI_BW_HT40"
    # Bandwidth is 40 MHz 
    WIFI_BW40 = "WIFI_BW40"
    # Bandwidth is 80 MHz 
    WIFI_BW80 = "WIFI_BW80"
    # Bandwidth is 160 MHz 
    WIFI_BW160 = "WIFI_BW160"
    # Bandwidth is 80 + 80 MHz 
    WIFI_BW80_BW80 = "WIFI_BW80_BW80"
    # Placeholder for the default option and unexpected value    
    WIFI_BW_ERROR = "WIFI_BW_ERROR"

"""
date, time, latitude, longitude, altitude, speed, bssid,
ssid,
primary-channel,
second-channel,
rssi,authmode,
pairwise-cipher,
group-cipher,
ant,
Country-code,
country-start-channel,
country-end-channel,
max-tx-power,
country-policy,
wifi-AP-HE,
bss-color,
partial-bss-color,
bss-color-disabled,
bssid-index,
bandwidth,
vht_ch_freq1,
vht_ch_freq2,
flags
"""
class WifiAPRecord(): 
    _FIELD_COUNT = 28
    def __init__(self, date, time, latitude, longitude, altitude, speed, bssid):
        # Required fields
        self._date = datetime.strptime(date, "%Y/%m/%d")
        self._time = datetime.strptime(time, "%H:%M:%S").time()
        self._latitude = float(latitude)
        self._longitude = float(longitude)
        self._altitude = float(altitude)
        self._speed = float(speed)
        self._bssid = bssid
        # Optional fields
        self._ssid = ""
        self._primary_channel = 0
        self._second_channel = WifiSecondChan.WIFI_SECOND_CHAN_ERROR
        self._rssi = 0
        self._authmode = WifiAuthMode.UNKNOWN_AUTH_ERROR
        self._pairwise_cipher = PairwiseCipherType.WIFI_CIPHER_TYPE_ERROR
        self._group_cipher = GroupCipherType.WIFI_CIPHER_TYPE_ERROR
        self._ant = Ant.WIFI_ANT_ERROR
        self._country_code = ""
        self._country_start_channel = 0
        self._country_end_channel = 0
        self._max_tx_power = 0
        self._country_policy = WifiCountryPolicy.WIFI_COUNTRY_POLICY_ERROR
        self._wifi_AP_HE = 0
        self._bss_color = 0
        self._partial_bss_color = 0
        self._bss_color_disabled = 0
        self._bssid_index = ""
        self._bandwidth = WifiBandwidth.WIFI_BW_ERROR
        self._vht_ch_freq1 = 0
        self._vht_ch_freq2 = 0

    # getters
    @property
    def date(self):
       return self._date

    @property
    def time(self):
        return self._time

    @property
    def latitude(self):
        return self._latitude

    @property
    def longitude(self):
        return self._longitude

    @property 
    def altitude(self):
        return self._altitude

    @property
    def speed(self):
        self._speed

    @property
    def bssid(self):
        return self._bssid

    @property
    def ssid(self):
        return self._ssid

    @property
    def primary_channel(self):
        return self._primary_channel

    @property 
    def second_channel(self):
        return self._second_channel

    @property
    def rssi(self):
        return self._rssi

    @property
    def authmode(self):
        return self._authmode

    @property
    def pairwise_cipher(self):
        return self._pairwise_cipher
    
    @property
    def group_cipher(self):
        return self._group_cipher

    @property
    def ant(self):
        return self._ant
    
    @property
    def country_code(self):
        return self._country_code

    @property
    def country_start_channel(self):
        return self._country_start_channel

    @property
    def country_end_channel(self):
        return self._country_end_channel

    @property
    def max_tx_power(self):
        return self._max_tx_power

    @property
    def country_policy(self):
        return self._country_policy

    @property
    def wifi_AP_HE(self):
        return self._wifi_AP_HE

    @property
    def bss_color(self):
        return self._bss_color

    @property
    def partial_bss_color(self):
        return self._partial_bss_color

    @property
    def bss_color_disabled(self):
        return self._bss_color_disabled

    @property
    def bssid_index(self):
        return self._bssid_index

    @property
    def bandwidth(self):
        return self._bandwidth

    @property
    def vht_ch_freq1(self):
        return self._vht_ch_freq1
    
    @property
    def vht_ch_freq2(self):
        return self._vht_ch_freq2

    # setters
    @date.setter
    def date(self, val):
        self._date = datetime.strptime(val)

    @time.setter
    def time(self, val):
        self._time = datetime.strptime(val, "%H:%M:%S").time()

    @latitude.setter
    def latitude(self, val):
        self._latitude = float(val)

    @longitude.setter
    def longitude(self, val):
        self._longitude = float(val)

    @altitude.setter 
    def altitude(self, val):
        self._altitude = float(val)

    @speed.setter
    def speed(self, val):
        self._speed = float(val)

    @bssid.setter
    def bssid(self, val):
        self._bssid = val 

    @ssid.setter
    def ssid(self, val):
        self._ssid = val

    @primary_channel.setter
    def primary_channel(self, val):
        self._primary_channel = int(val)

    @second_channel.setter 
    def second_channel(self, val):
        self._second_channel = val

    @rssi.setter
    def rssi(self, val):
        self._rssi = val

    @authmode.setter
    def authmode(self, val):
        self._authmode = val

    @pairwise_cipher.setter
    def pairwise_cipher(self, val):
        self._pairwise_cipher = val
    
    @group_cipher.setter
    def group_cipher(self, val):
        self._group_cipher = val

    @ant.setter
    def ant(self, val):
        self._ant = val
    
    @country_code.setter
    def country_code(self, val):
        self._country_code = val

    @country_start_channel.setter
    def country_start_channel(self, val):
        self._country_start_channel = val

    @country_end_channel.setter
    def country_end_channel(self, val):
        self._country_end_channel = val

    @max_tx_power.setter
    def max_tx_power(self, val):
        self._max_tx_power = val

    @country_policy.setter
    def country_policy(self, val):
        self._country_policy = val

    @wifi_AP_HE.setter
    def wifi_AP_HE(self, val):
        self._wifi_AP_HE = val

    @bss_color.setter
    def bss_color(self, val):
        self._bss_color = val

    @partial_bss_color.setter
    def partial_bss_color(self, val):
        self._partial_bss_color = val

    @bss_color_disabled.setter
    def bss_color_disabled(self, val):
        self._bss_color_disabled = val

    @bssid_index.setter
    def bssid_index(self, val):
        self._bssid_index = val

    @bandwidth.setter
    def bandwidth(self, val):
        self._bandwidth = val

    @vht_ch_freq1.setter
    def vht_ch_freq1(self, val):
        self._vht_ch_freq1 = val
    
    @vht_ch_freq2.setter
    def vht_ch_freq2(self, val):
        self._vht_ch_freq2 = val

    @staticmethod
    def readCSV(content):
        file = io.StringIO(content)
        reader = csv.reader(file)
        return [row for row in reader]

    @staticmethod
    def parse_obj(ap_str):
        obj = WifiAPRecord(ap_str[0], ap_str[1], ap_str[2], ap_str[3], ap_str[4], ap_str[5], ap_str[6])
        obj.ssid = ap_str[7]
        obj.primary_channel = int(ap_str[8])
        obj.second_channel = ap_str[9]
        obj.rssi = int(ap_str[10])
        obj.authmode = ap_str[11]
        obj.pairwise_cipher = ap_str[12]
        obj.group_cipher = ap_str[13]
        obj._ant = ap_str[14]
        obj.country_code = ap_str[15]
        obj.country_start_channel = int(ap_str[16])
        obj.country_end_channel = int(ap_str[17])
        obj.max_tx_power = int(ap_str[18])
        obj.country_policy = ap_str[19]
        obj.wifi_AP_HE = int(ap_str[20])
        obj.bss_color = int(ap_str[21])
        obj.partial_bss_color = int(ap_str[22])
        obj.bss_color_disabled = int(ap_str[23])
        obj.bssid_index = ap_str[24]
        obj.bandwidth = ap_str[25]
        obj.vht_ch_freq1 = int(ap_str[26])
        obj.vht_ch_freq2 = int(ap_str[27])
        return obj


    @property
    def FIELD_COUNT(self):
        return self._FIELD_COUNT

    def __str__(self):
        str_form = ""
        str_form+= str(self._date) 
        str_form+= str(self._time)
        str_form+= str(self._latitude)
        str_form+= str(self._longitude) 
        str_form+= str(self._altitude) 
        str_form+= str(self._speed) 
        str_form+= str(self._bssid)
        # Optional fields
        str_form+= str(self._ssid)
        str_form+= str(self._primary_channel)
        str_form+= str(self._second_channel)
        str_form+= str(self._rssi) 
        str_form+= str(self._authmode) 
        str_form+= str(self._pairwise_cipher) 
        str_form+= str(self._group_cipher) 
        str_form+= str(self._ant) 
        str_form+= str(self._country_code) 
        str_form+= str(self._country_start_channel) 
        str_form+= str(self._country_end_channel) 
        str_form+= str(self._max_tx_power) 
        str_form+= str(self._country_policy) 
        str_form+= str(self._wifi_AP_HE)
        str_form+= str(self._bss_color) 
        str_form+= str(self._partial_bss_color) 
        str_form+= str(self._bss_color_disabled) 
        str_form+= str(self._bssid_index)
        str_form+= str(self._bandwidth) 
        str_form+= str(self._vht_ch_freq1)
        str_form+= str(self._vht_ch_freq2)
        return str_form

    def __eq__(self, other):
        return isinstance(other, WifiAPRecord) and str(self) == str(other)

    def __hash__(self):
        return hash(str(self))

    def to_html(self):
        snippet = f"""
        date: {str(self._date) }
        time: {str(self._time)}
        latitude: {str(self._latitude)}
        longitude: {str(self._longitude)}
        altitude: {str(self._altitude)}
        speed: {str(self._speed)}
        bssid: {str(self._bssid)}
        ssid: {str(self._ssid)}
        primary_channel: {str(self._primary_channel)}
        second_channel: {str(self._second_channel)}
        rssi: {str(self._rssi)}
        authmode: {str(self._authmode)}
        pairwise_cipher: {str(self._pairwise_cipher)}
        group_cipher: {str(self._group_cipher)}
        ant: {str(self._ant)}
        country_code: {str(self._country_code)} 
        country_start_channel: {str(self._country_start_channel)} 
        country_end_channel: {str(self._country_end_channel)}
        max_tx_power: {str(self._max_tx_power)}
        country_policy: {str(self._country_policy)}
        wifi_AP_HE: {str(self._wifi_AP_HE)}
        bss_color: {str(self._bss_color)}
        partial_bss_color: {str(self._partial_bss_color)}
        bss_color_disabled: {str(self._bss_color_disabled)}
        bssid_index: {str(self._bssid_index)}
        bandwidth: {str(self._bandwidth)}
        vht_ch_freq1: {str(self._vht_ch_freq1)}
        vht_ch_freq2: {str(self._vht_ch_freq2)}
        """
        return snippet

    def to_dict(self):
        return {
            'date': self._date.strftime("%Y-%m-%d"),
            'time': self._time.strftime("%H:%M:%S"),
            'latitude': self._latitude,
            'longitude': self._longitude,
            'altitude': self._altitude,
            'speed': self._speed,
            'bssid': self._bssid,
            'ssid': self._ssid,
            'primary_channel': self._primary_channel,
            'second_channel': self._second_channel.value if isinstance(self._second_channel, Enum) else self._second_channel,
            'rssi': self._rssi,
            'authmode': self._authmode.value if isinstance(self._authmode, Enum) else self._authmode,
            'pairwise_cipher': self._pairwise_cipher.value if isinstance(self._pairwise_cipher, Enum) else self._pairwise_cipher,
            'group_cipher': self._group_cipher.value if isinstance(self._group_cipher, Enum) else self._group_cipher,
            'ant': self._ant.value if isinstance(self._ant, Enum) else self._ant,
            'country_code': self._country_code,
            'country_start_channel': self._country_start_channel,
            'country_end_channel': self._country_end_channel,
            'max_tx_power': self._max_tx_power,
            'country_policy': self._country_policy.value if isinstance(self._country_policy, Enum) else self._country_policy,
            'wifi_AP_HE': self._wifi_AP_HE,
            'bss_color': self._bss_color,
            'partial_bss_color': self._partial_bss_color,
            'bss_color_disabled': self._bss_color_disabled,
            'bssid_index': self._bssid_index,
            'bandwidth': self._bandwidth.value if isinstance(self._bandwidth, Enum) else self._bandwidth,
            'vht_ch_freq1': self._vht_ch_freq1,
            'vht_ch_freq2': self._vht_ch_freq2,
        }
                    
class WifiAPRecordCollection:
    def __init__(self, wifi_ap_records):
        self._wifi_ap_records = wifi_ap_records

    def filter_invalid_gps_coords(self):
        self._wifi_ap_records = [ap for ap in self._wifi_ap_records if ap.latitude != 0.0 and ap.longitude != 0.0]

    def filter_duplicates(self):
        self._wifi_ap_records = list(set(self._wifi_ap_records))

    def speard_out(self):
        pass

    @property
    def wifi_ap_records(self):
        return self._wifi_ap_records