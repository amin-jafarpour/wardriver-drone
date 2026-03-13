from enum import Enum
from datetime import datetime


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
        self._flags = 0