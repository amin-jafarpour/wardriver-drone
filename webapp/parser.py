from enum import Enum

# https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/network/esp_wifi.html#_CPPv416wifi_ap_record_t

class WifiSecondChan(Enum):
    # The channel width is HT20 
    WIFI_SECOND_CHAN_NONE = "WIFI_SECOND_CHAN_NONE"
    # The channel width is HT40 and the secondary channel is above the primary channel 
    WIFI_SECOND_CHAN_ABOVE = "WIFI_SECOND_CHAN_ABOVE"
    # The channel width is HT40 and the secondary channel is below the primary channel
    WIFI_SECOND_CHAN_BELOW = "WIFI_SECOND_CHAN_BELOW"

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

# Wi-Fi antenna
class Ant(Enum):
    # Wi-Fi antenna 0 
    WIFI_ANT_ANT0 = "WIFI_ANT_ANT0"
    # Wi-Fi antenna 1 
    WIFI_ANT_ANT1 = "WIFI_ANT_ANT1"
    # Invalid Wi-Fi antenna 
    WIFI_ANT_MAX = "WIFI_ANT_MAX"

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
