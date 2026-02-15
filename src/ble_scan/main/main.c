#include <stdio.h>
#include <string.h>
#include <stdbool.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "esp_log.h"
#include "nvs_flash.h"
#include "esp_bt.h"
#include "esp_bt_main.h"
#include "esp_gap_ble_api.h"
#include "sdkconfig.h"

#define STR_MAC_LEN 18

static const char *TAG = "BLE_SCANNER";

// Set BLE scan parameters.
static esp_ble_scan_params_t ble_scan_params = {
    .scan_type              = BLE_SCAN_TYPE_ACTIVE,
    .own_addr_type          = BLE_ADDR_TYPE_PUBLIC,
    .scan_filter_policy     = BLE_SCAN_FILTER_ALLOW_ALL,
    .scan_interval          = 0x50,
    .scan_window            = 0x30,
    .scan_duplicate         = BLE_SCAN_DUPLICATE_DISABLE
};

// Converts uint8_t array representing MAC addr to string.
static void bd_addr_to_str(const uint8_t bda[6], char *str, size_t size)
{
    snprintf(str, size, "%02X:%02X:%02X:%02X:%02X:%02X",
             bda[0], bda[1], bda[2], bda[3], bda[4], bda[5]);
}

// Prints unit8_t array in hex format.
static void print_hex(const uint8_t *data, size_t len)
{
    for (size_t i = 0; i < len; ++i) {
        printf("%02X", data[i]);
        if (i + 1 < len) {
            printf(" ");
        }
    }
}

// Prints BLE advertisement info obtained.
void print_ble_adv_info(const esp_ble_gap_cb_param_t* param, const char* addr_str, const char* name_buf, 
    uint8_t *manuf_data, uint8_t manuf_len, uint8_t *service16, 
    uint8_t service16_len, uint8_t *service128,uint8_t service128_len)
{
    // Print device name.
    printf("  Name: %s\n", name_buf);
    // Print physical address.
    printf("  Device: %s\n", addr_str);
    // Print RSSI.
    printf("  RSSI: %d dBm\n", param->scan_rst.rssi);
    // Print device Type
    printf("  Device type: %d\n", param->scan_rst.dev_type);
    // Print address type.
    printf("  Address type: %d\n", param->scan_rst.ble_addr_type);
    // Print BLE GAP event type.
    printf("  Event type: %d\n", param->scan_rst.ble_evt_type);
    // If manufacture data exist. 
    if (manuf_data && manuf_len > 0) {
        // Print manufacture data.
        printf("  Manufacturer data (%u bytes): ", manuf_len);
        print_hex(manuf_data, manuf_len);
        printf("\n");
    }
    // If 16-bit service UUID exist.
    if (service16 && service16_len >= 2) {
        // Print 16-bit service UUID
        printf("  16-bit Service UUIDs: ");
        for (int i = 0; i < service16_len; i += 2) {
            uint16_t uuid = service16[i] | (service16[i + 1] << 8);
            printf("0x%04X", uuid);
            if (i + 2 < service16_len) {
                printf(", ");
            }
        }
        printf("\n");
    }
    // If 128-bit service UUID exist.
    if (service128 && service128_len >= 16) {
        // Print 18-bit service UUID
        int num_uuid = service128_len / 16;
        for (int i = 0; i < num_uuid; ++i) {
            printf("  128-bit Service UUID %d: ", i + 1);
            // UUIDs are transmitted little‑endian. 
            // Print them in canonical big‑endian form by reversing the byte order.
            const uint8_t *u = service128 + (i * 16);
            for (int j = 15; j >= 0; --j) {
                printf("%02X", u[j]);
                if (j == 15 || j == 13 || j == 11 || j == 9) {
                    printf("-");
                }
            }
            printf("\n");
        }
    }
    printf("\n");
}


static void handle_adv_report(const esp_ble_gap_cb_param_t* param)
{
    char addr_str[STR_MAC_LEN] = {0};
    bd_addr_to_str(param->scan_rst.bda, addr_str, sizeof(addr_str));
    uint16_t adv_len_total = param->scan_rst.adv_data_len + param->scan_rst.scan_rsp_len;
    uint8_t name_len = 0;
    uint8_t *name = esp_ble_resolve_adv_data_by_type((uint8_t *)param->scan_rst.ble_adv,
    adv_len_total, ESP_BLE_AD_TYPE_NAME_CMPL, &name_len);
    if (name == NULL || name_len == 0) {
        name = esp_ble_resolve_adv_data_by_type((uint8_t *)param->scan_rst.ble_adv, 
        adv_len_total, ESP_BLE_AD_TYPE_NAME_SHORT, &name_len);
    }
    char name_buf[32] = {0};
    if (name && name_len > 0) {
        size_t copy_len = name_len < sizeof(name_buf) - 1 ? name_len : sizeof(name_buf) - 1;
        memcpy(name_buf, name, copy_len);
        name_buf[copy_len] = '\0';
    } else {
        strcpy(name_buf, "<unknown>");
    }
    uint8_t manuf_len = 0;
    uint8_t *manuf_data = esp_ble_resolve_adv_data_by_type((uint8_t *)param->scan_rst.ble_adv, 
    adv_len_total, ESP_BLE_AD_MANUFACTURER_SPECIFIC_TYPE, &manuf_len);
    uint8_t service16_len = 0;
    uint8_t *service16 = esp_ble_resolve_adv_data_by_type((uint8_t *)param->scan_rst.ble_adv, 
    adv_len_total, ESP_BLE_AD_TYPE_16SRV_CMPL, &service16_len);
    if (service16 == NULL || service16_len == 0) {
        service16 = esp_ble_resolve_adv_data_by_type((uint8_t *)param->scan_rst.ble_adv, 
        adv_len_total, ESP_BLE_AD_TYPE_16SRV_PART, &service16_len);
    }
    uint8_t service128_len = 0;
    uint8_t *service128 = esp_ble_resolve_adv_data_by_type((uint8_t *)param->scan_rst.ble_adv, 
    adv_len_total, ESP_BLE_AD_TYPE_128SRV_CMPL, &service128_len);
    if (service128 == NULL || service128_len == 0) {
        service128 = esp_ble_resolve_adv_data_by_type((uint8_t *)param->scan_rst.ble_adv, 
        adv_len_total, ESP_BLE_AD_TYPE_128SRV_PART, &service128_len);
    }
    print_ble_adv_info(param, addr_str, name_buf, manuf_data, manuf_len, 
        service16, service16_len, service128, service128_len);
}

// Callback called when one BLE event occurs.
static void gap_event_handler(esp_gap_ble_cb_event_t event, esp_ble_gap_cb_param_t *param)
{
    switch (event) {
    // BLE scan parameters are set.
    case ESP_GAP_BLE_SCAN_PARAM_SET_COMPLETE_EVT:
        ESP_LOGI(TAG, "Scan parameters set, starting scan");
        // Start scanning. Set it to zero to scan forever.
        esp_ble_gap_start_scanning(CONFIG_SCAN_DURATION); 
        break;
    // BLE scanning has started.
    case ESP_GAP_BLE_SCAN_START_COMPLETE_EVT:
        // If failed to start BLE scanning.
        if (param->scan_start_cmpl.status != ESP_BT_STATUS_SUCCESS) {
            ESP_LOGE(TAG, "Failed to start scanning, error code = %x", param->scan_start_cmpl.status);
        } else {
            ESP_LOGI(TAG, "Scanning started");
        }
        break;
    // Obtained one BLE scan record.
    case ESP_GAP_BLE_SCAN_RESULT_EVT:
        if (param->scan_rst.search_evt == ESP_GAP_SEARCH_INQ_RES_EVT) {
            handle_adv_report(param);
        } else{
            ESP_LOGI(TAG, "Not ESP_GAP_SEARCH_INQ_RES_EVT");
        }
        break;
    // Stopped BLE scanning.
    case ESP_GAP_BLE_SCAN_STOP_COMPLETE_EVT:
        if (param->scan_stop_cmpl.status != ESP_BT_STATUS_SUCCESS) {
            ESP_LOGE(TAG, "Failed to stop scanning, error code = %x", param->scan_stop_cmpl.status);
        } else {
            ESP_LOGI(TAG, "Scanning stopped");
        }
        break;
    // Unsupported event. 
    default:
        break;
    }
}

void app_main(void)
{
    // Set up  NVS.
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);
    // Classic BT is not used. Free memory occupied by classic BT.
    ESP_ERROR_CHECK(esp_bt_controller_mem_release(ESP_BT_MODE_CLASSIC_BT));
    // Instantiate BT controller configuration object.
    esp_bt_controller_config_t bt_cfg = BT_CONTROLLER_INIT_CONFIG_DEFAULT();
    // Initialize BT controller with BT controller configuration object.
    ret = esp_bt_controller_init(&bt_cfg);
    if (ret) {
        ESP_LOGE(TAG, "Bluetooth controller initialization failed: %s", esp_err_to_name(ret));
        return;
    }
    // Set BT mode to BLE.
    ret = esp_bt_controller_enable(ESP_BT_MODE_BLE);
    if (ret) {
        ESP_LOGE(TAG, "Bluetooth controller enable failed: %s", esp_err_to_name(ret));
        return;
    }
    // Initialize Bluedroid BT stack.
    ret = esp_bluedroid_init();
    if (ret) {
        ESP_LOGE(TAG, "Bluedroid stack initialization failed: %s", esp_err_to_name(ret));
        return;
    }
    // Enable Bluedroid stack.
    ret = esp_bluedroid_enable();
    if (ret) {
        ESP_LOGE(TAG, "Bluedroid stack enable failed: %s", esp_err_to_name(ret));
        return;
    }
    // Register BLE GAP event handler function.
    ESP_ERROR_CHECK(esp_ble_gap_register_callback(gap_event_handler));
    // Set BLE GAP scan parameters.
    ESP_ERROR_CHECK(esp_ble_gap_set_scan_params(&ble_scan_params));
}