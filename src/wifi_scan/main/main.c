#include <string.h>
#include <assert.h>

#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"

#include "sdkconfig.h"
#include "esp_wifi.h"
#include "esp_log.h"
#include "esp_event.h"
#include "nvs_flash.h"
#include "esp_netif.h"

static const char *TAG = "wifi_scan";

// Prints authentication mode of AP.
static void print_auth_mode(wifi_auth_mode_t authmode)
{
    switch (authmode) {
    case WIFI_AUTH_OPEN:
        ESP_LOGI(TAG, "Authmode: WIFI_AUTH_OPEN");
        break;
    case WIFI_AUTH_OWE:
        ESP_LOGI(TAG, "Authmode: WIFI_AUTH_OWE");
        break;
    case WIFI_AUTH_WEP:
        ESP_LOGI(TAG, "Authmode: WIFI_AUTH_WEP");
        break;
    case WIFI_AUTH_WPA_PSK:
        ESP_LOGI(TAG, "Authmode: WIFI_AUTH_WPA_PSK");
        break;
    case WIFI_AUTH_WPA2_PSK:
        ESP_LOGI(TAG, "Authmode: WIFI_AUTH_WPA2_PSK");
        break;
    case WIFI_AUTH_WPA_WPA2_PSK:
        ESP_LOGI(TAG, "Authmode: WIFI_AUTH_WPA_WPA2_PSK");
        break;
    case WIFI_AUTH_ENTERPRISE:
        ESP_LOGI(TAG, "Authmode: WIFI_AUTH_ENTERPRISE");
        break;
    case WIFI_AUTH_WPA3_PSK:
        ESP_LOGI(TAG, "Authmode: WIFI_AUTH_WPA3_PSK");
        break;
    case WIFI_AUTH_WPA2_WPA3_PSK:
        ESP_LOGI(TAG, "Authmode: WIFI_AUTH_WPA2_WPA3_PSK");
        break;
    case WIFI_AUTH_WPA3_ENTERPRISE:
        ESP_LOGI(TAG, "Authmode: WIFI_AUTH_WPA3_ENTERPRISE");
        break;
    case WIFI_AUTH_WPA2_WPA3_ENTERPRISE:
        ESP_LOGI(TAG, "Authmode: WIFI_AUTH_WPA2_WPA3_ENTERPRISE");
        break;
    case WIFI_AUTH_WPA3_ENT_192:
        ESP_LOGI(TAG, "Authmode: WIFI_AUTH_WPA3_ENT_192");
        break;
    default:
        ESP_LOGI(TAG, "Authmode: WIFI_AUTH_UNKNOWN (%d)", authmode);
        break;
    }
}

// Prints pairwise cipher type of AP.
static void print_pairwise_cipher_type(wifi_cipher_type_t pairwise_cipher)
{
    switch (pairwise_cipher) {
    case WIFI_CIPHER_TYPE_NONE:
        ESP_LOGI(TAG, "Pairwise Cipher: WIFI_CIPHER_TYPE_NONE");
        break;
    case WIFI_CIPHER_TYPE_WEP40:
        ESP_LOGI(TAG, "Pairwise Cipher: WIFI_CIPHER_TYPE_WEP40");
        break;
    case WIFI_CIPHER_TYPE_WEP104:
        ESP_LOGI(TAG, "Pairwise Cipher: WIFI_CIPHER_TYPE_WEP104");
        break;
    case WIFI_CIPHER_TYPE_TKIP:
        ESP_LOGI(TAG, "Pairwise Cipher: WIFI_CIPHER_TYPE_TKIP");
        break;
    case WIFI_CIPHER_TYPE_CCMP:
        ESP_LOGI(TAG, "Pairwise Cipher: WIFI_CIPHER_TYPE_CCMP");
        break;
    case WIFI_CIPHER_TYPE_TKIP_CCMP:
        ESP_LOGI(TAG, "Pairwise Cipher: WIFI_CIPHER_TYPE_TKIP_CCMP");
        break;
    case WIFI_CIPHER_TYPE_AES_CMAC128:
        ESP_LOGI(TAG, "Pairwise Cipher: WIFI_CIPHER_TYPE_AES_CMAC128");
        break;
    case WIFI_CIPHER_TYPE_SMS4:
        ESP_LOGI(TAG, "Pairwise Cipher: WIFI_CIPHER_TYPE_SMS4");
        break;
    case WIFI_CIPHER_TYPE_GCMP:
        ESP_LOGI(TAG, "Pairwise Cipher: WIFI_CIPHER_TYPE_GCMP");
        break;
    case WIFI_CIPHER_TYPE_GCMP256:
        ESP_LOGI(TAG, "Pairwise Cipher: WIFI_CIPHER_TYPE_GCMP256");
        break;
    default:
        ESP_LOGI(TAG, "Pairwise Cipher: WIFI_CIPHER_TYPE_UNKNOWN (%d)", pairwise_cipher);
        break;
    }
}

// Prints group cipher type of AP.
static void print_group_cipher_type(wifi_cipher_type_t group_cipher)
{
    switch (group_cipher) {
    case WIFI_CIPHER_TYPE_NONE:
        ESP_LOGI(TAG, "Group Cipher: WIFI_CIPHER_TYPE_NONE");
        break;
    case WIFI_CIPHER_TYPE_WEP40:
        ESP_LOGI(TAG, "Group Cipher: WIFI_CIPHER_TYPE_WEP40");
        break;
    case WIFI_CIPHER_TYPE_WEP104:
        ESP_LOGI(TAG, "Group Cipher: WIFI_CIPHER_TYPE_WEP104");
        break;
    case WIFI_CIPHER_TYPE_TKIP:
        ESP_LOGI(TAG, "Group Cipher: WIFI_CIPHER_TYPE_TKIP");
        break;
    case WIFI_CIPHER_TYPE_CCMP:
        ESP_LOGI(TAG, "Group Cipher: WIFI_CIPHER_TYPE_CCMP");
        break;
    case WIFI_CIPHER_TYPE_TKIP_CCMP:
        ESP_LOGI(TAG, "Group Cipher: WIFI_CIPHER_TYPE_TKIP_CCMP");
        break;
    case WIFI_CIPHER_TYPE_SMS4:
        ESP_LOGI(TAG, "Group Cipher: WIFI_CIPHER_TYPE_SMS4");
        break;
    case WIFI_CIPHER_TYPE_GCMP:
        ESP_LOGI(TAG, "Group Cipher: WIFI_CIPHER_TYPE_GCMP");
        break;
    case WIFI_CIPHER_TYPE_GCMP256:
        ESP_LOGI(TAG, "Group Cipher: WIFI_CIPHER_TYPE_GCMP256");
        break;
    default:
        ESP_LOGI(TAG, "Group Cipher: WIFI_CIPHER_TYPE_UNKNOWN (%d)", group_cipher);
        break;
    }
}

// Initializes Wi-Fi stack.
void init_wifi()
{
   // Start event loop.
   ESP_ERROR_CHECK(esp_event_loop_create_default());
   // Initialize network interface card.
   ESP_ERROR_CHECK(esp_netif_init());
   // Instantiate network interface object for Wi-Fi station mode. 
   esp_netif_t *netif = esp_netif_create_default_wifi_sta();
   if (netif == NULL) {
     ESP_LOGE(TAG, "Failed to create default Wi-Fi STA netif");
     return;
   }
   // Instantiate Wi-Fi initialization object with default values.
   wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
   ESP_ERROR_CHECK(esp_wifi_init(&cfg));
    wifi_country_t ca_country = {
        .cc = "CA",
        .schan = 1,          
        .nchan = 11,      
        .max_tx_power = 20,  
        .policy = WIFI_COUNTRY_POLICY_MANUAL
    };
    // Set country specification.
    ESP_ERROR_CHECK(esp_wifi_set_country(&ca_country));
    // Set Wi-Fi mode to station mode.
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    // Disable power saving feature.
    ESP_ERROR_CHECK(esp_wifi_set_ps(WIFI_PS_NONE));
    // Start Wi-Fi stack.
    ESP_ERROR_CHECK(esp_wifi_start());
}

// Prints one AP's info.
void print_AP_info(wifi_ap_record_t AP_info)
{
        // Print SSID.
        ESP_LOGI(TAG, "SSID:    %s", (char*)AP_info.ssid);
        // PRint RSSI.
        ESP_LOGI(TAG, "RSSI:    %d dBm", AP_info.rssi);
        // Print BSSID.
        ESP_LOGI(TAG, "BSSID:   %02X:%02X:%02X:%02X:%02X:%02X",
                 AP_info.bssid[0], AP_info.bssid[1], AP_info.bssid[2],
                 AP_info.bssid[3], AP_info.bssid[4], AP_info.bssid[5]);
        // Print primary channel.
        ESP_LOGI(TAG, "Primary Channel: %d", AP_info.primary);
        // Print secondary channel.
        ESP_LOGI(TAG, "Second Channel: %d", AP_info.second);
        // Print authentication mode.
        print_auth_mode(AP_info.authmode);
        // Print group cipher type.
        print_group_cipher_type(AP_info.group_cipher);
        // print pairwise cipher type.
        print_pairwise_cipher_type(AP_info.pairwise_cipher);
        ESP_LOGI(TAG, "*******************************");
}

// Scans at most CONFIG_RF_CHANNEL number of APs.
static void wifi_scan(void){
    wifi_ap_record_t APs_info[CONFIG_SCAN_LIST_SIZE] = {0};
    // Instantiate Wi-Fi scan configuration object.
    wifi_scan_config_t scan_config = {0};
    // Set channel to scan. Set it to zero to scan all possible channels.
    scan_config.channel = CONFIG_RF_CHANNEL; 
    // Enable scanning of hidden networks.
    scan_config.show_hidden = true;      
    // Enable active scanning.        
    scan_config.scan_type = WIFI_SCAN_TYPE_ACTIVE;
    // Set min active dwell time per channel in ms.
    scan_config.scan_time.active.min = 100;  
    // Set max active dwell time per channel in ms.  
    scan_config.scan_time.active.max = 300;   
    // Start scanning.    
    ESP_ERROR_CHECK(esp_wifi_scan_start(&scan_config, true));
            // uint16_t ap_count = 0;
    // Get number of APs scanned.
            // ESP_ERROR_CHECK(esp_wifi_scan_get_ap_num(&ap_count));
    uint16_t AP_count = CONFIG_SCAN_LIST_SIZE;
    // Fetch AP scanning result records.
    ESP_ERROR_CHECK(esp_wifi_scan_get_ap_records(&AP_count, APs_info));
        // ESP_LOGI(TAG, "APs found by hardware: %u, records filled: %u", ap_count, number);
    // Print each AP scanning record.
    for (int i = 0; i < AP_count; i++) {
        print_AP_info(APs_info[i]);
    }
}

void app_main(void)
{
    // Initialize NVS storage.
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);
    // Initialize Wi-Fi stack.
    init_wifi();
    for (int i = 0; i < CONFIG_SCAN_ITERATION_COUNT; i++)
    {
        // Scan.
        wifi_scan();
        ESP_LOGI(TAG, "++++++++++++++++++++++++++++Iteration %d+++++++++++++++++++++++++++++++++++++", i);
        // Wait.
        vTaskDelay(pdMS_TO_TICKS(CONFIG_SCAN_ITERATION_PEROID * 1000));
    }    
}
