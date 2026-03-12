from enum import Enum

# https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/network/esp_wifi.html#_CPPv416wifi_ap_record_t

class WifiSecondChan(Enum):
    # The channel width is HT20 
    WIFI_SECOND_CHAN_NONE = "WIFI_SECOND_CHAN_NONE"
    # The channel width is HT40 and the secondary channel is above the primary channel 
    WIFI_SECOND_CHAN_ABOVE = "WIFI_SECOND_CHAN_ABOVE"
    # The channel width is HT40 and the secondary channel is below the primary channel
    WIFI_SECOND_CHAN_BELOW = "WIFI_SECOND_CHAN_BELOW"


