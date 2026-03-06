#include <string.h>
#include <sys/unistd.h>
#include <sys/stat.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"
#include "freertos/semphr.h"

#include "driver/gpio.h"
#include "esp_log.h"
#include "esp_event.h"
#include "esp_wifi.h"
#include "nvs_flash.h"
#include "regex.h"
#include "esp_err.h"

#include "esp_vfs_fat.h"
#include "sdmmc_cmd.h"
#include "driver/sdmmc_host.h"

#include "nmea_parser.h"

#if SOC_SDMMC_IO_POWER_EXTERNAL
    #include "sd_pwr_ctrl_by_on_chip_ldo.h"
#endif

#define IS_UHS1 (CONFIG_SDMMC_SPEED_UHS_I_SDR50 || CONFIG_SDMMC_SPEED_UHS_I_DDR50 || CONFIG_SDMMC_SPEED_UHS_I_SDR104)

#ifdef CONFIG_DEBUG_PIN_CONNECTIONS
    const char* pin_names[] = {"CLK", "CMD", "D0", "D1", "D2", "D3"};
    const int pins[] = {
                            CONFIG_PIN_CLK,
                            CONFIG_PIN_CMD,
                            CONFIG_PIN_D0
                            #ifdef CONFIG_SDMMC_BUS_WIDTH_4
                                ,CONFIG_PIN_D1,
                                 CONFIG_PIN_D2,
                                 CONFIG_PIN_D3
                            #endif
                        };

    const int pin_count = sizeof(pins)/sizeof(pins[0]);

    #if CONFIG_ENABLE_ADC_FEATURE
        const int adc_channels[] = {
                                    CONFIG_ADC_PIN_CLK,
                                    CONFIG_ADC_PIN_CMD,
                                    CONFIG_ADC_PIN_D0
                                    #ifdef CONFIG_SDMMC_BUS_WIDTH_4
                                        ,CONFIG_ADC_PIN_D1,
                                         CONFIG_ADC_PIN_D2,
                                         CONFIG_ADC_PIN_D3
                                    #endif
                                    };
    #endif 

    pin_configuration_t config = {
        .names = pin_names,
        .pins = pins,
        #if CONFIG_ENABLE_ADC_FEATURE
            .adc_channels = adc_channels,
        #endif
    };
#endif 

#define DATA_SIZE 500
#define MAX_FILE_COUNT 10
#define ALLOCATION_UNIT_SIZE 16 * 1024
#define MOUNT_POINT "/wardriver"

#define TIME_ZONE (-8)   //Vancouver Time
#define YEAR_BASE (2000) //date in GPS starts from 2000

#ifdef CONFIG_USE_SCAN_CHANNEL_BITMAP
    #define CHANNEL_LIST_SIZE 14
    static uint8_t channel_list[CHANNEL_LIST_SIZE] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14}; // {1, 6, 11};
#endif

static const char *TAG = "app";
SemaphoreHandle_t gps_ready_sem;
static gps_t gps;

#ifdef CONFIG_USE_SCAN_CHANNEL_BITMAP
    static void array_2_channel_bitmap(const uint8_t channel_list[], const uint8_t channel_list_size, wifi_scan_config_t *scan_config) {

        for(uint8_t i = 0; i < channel_list_size; i++) {
            uint8_t channel = channel_list[i];
            scan_config->channel_bitmap.ghz_2_channels |= (1 << channel);
        }
    }
#endif


#if CONFIG_PIN_CARD_POWER_RESET
    static esp_err_t reset_card_power()
    {
        esp_err_t ret = ESP_FAIL;
        gpio_config_t io_conf = {
            .mode = GPIO_MODE_OUTPUT,
            .pin_bit_mask = (1ULL<<CONFIG_PIN_CARD_POWER_RESET),
        };
        ret = gpio_config(&io_conf);
        if (ret != ESP_OK) {
            ESP_LOGE(TAG, "Failed to config GPIO");
            return ret;
        }

        ret = gpio_set_level(CONFIG_PIN_CARD_POWER_RESET, 1);
        if (ret != ESP_OK) {
            ESP_LOGE(TAG, "Failed to set GPIO level");
            return ret;
        }

        vTaskDelay(100 / portTICK_PERIOD_MS);

        ret = gpio_set_level(CONFIG_PIN_CARD_POWER_RESET, 0);
        if (ret != ESP_OK) {
            ESP_LOGE(TAG, "Failed to set GPIO level");
            return ret;
        }

        return ESP_OK;
    }
#endif

void setup_nvs()
{
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK( ret );
}

void setup_wifi_stack()
{
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_t *sta_netif = esp_netif_create_default_wifi_sta();
    assert(sta_netif);
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_start());
}

void wifi_scan(sdmmc_card_t *card)
{

    setup_nvs();
    setup_wifi_stack();


    uint16_t number = CONFIG_SCAN_LIST_SIZE;
    wifi_ap_record_t ap_info[CONFIG_SCAN_LIST_SIZE];
    wifi_scan_config_t scan_config;
    uint16_t ap_count;

    const char *file_path = MOUNT_POINT"/file.txt";

    while(true)
    {
        memset(ap_info, 0, sizeof(ap_info));// xx
        memset(&scan_config, 0, sizeof(wifi_scan_config_t));
        ap_count = 0;
        
        
        FILE *f = fopen(file_path, "a");
        if (f == NULL) 
        {
            perror("fopen");
            ESP_ERROR_CHECK(ESP_FAIL);
        }

        #ifdef CONFIG_USE_SCAN_CHANNEL_BITMAP
            array_2_channel_bitmap(channel_list, CHANNEL_LIST_SIZE, &scan_config);
            esp_wifi_scan_start(scan_config, true);
        #else
            esp_wifi_scan_start(NULL, true);
        #endif

        ESP_ERROR_CHECK(esp_wifi_scan_get_ap_num(&ap_count));
        ESP_ERROR_CHECK(esp_wifi_scan_get_ap_records(&number, ap_info));
        ESP_LOGI(TAG, "Total APs scanned = %u, actual AP number ap_info holds = %u", ap_count, number);

        if(xSemaphoreTake(gps_ready_sem, pdMS_TO_TICKS(2000))) // portMAX_DELAY
        {
            fprintf(f,"%d/%d/%d %d:%d:%d => \r\n"
                "\t\t\t\t\t\tlatitude   = %.05f°N\r\n"
                "\t\t\t\t\t\tlongitude = %.05f°E\r\n"
                "\t\t\t\t\t\taltitude   = %.02fm\r\n"
                "\t\t\t\t\t\tspeed      = %fm/s",
                gps.date.year + YEAR_BASE, gps.date.month, gps.date.day,
                gps.tim.hour + TIME_ZONE, gps.tim.minute, gps.tim.second,
                gps.latitude, gps.longitude, gps.altitude, gps.speed);

            for (int i = 0; i < number; i++) 
            {
                uint8_t *mac = ap_info[i].bssid;
                fprintf(f, "%02X:%02X:%02X:%02X:%02X:%02X\n",
                    mac[0], mac[1], mac[2],
                    mac[3], mac[4], mac[5]);

            }
        }

        vTaskDelay(pdMS_TO_TICKS(1000));
        fflush(f);
        fclose(f);
    }    
}

typedef void (*sdcard_callback)(sdmmc_card_t *card);

void sdcard_setup(sdcard_callback callback)
{
    esp_err_t ret;
    esp_vfs_fat_sdmmc_mount_config_t mount_config = 
    {
        #ifdef CONFIG_FORMAT_IF_MOUNT_FAILED
            .format_if_mount_failed = true,
        #else
            .format_if_mount_failed = false,
        #endif
            .max_files = MAX_FILE_COUNT,
            .allocation_unit_size = ALLOCATION_UNIT_SIZE 
    };
    sdmmc_card_t *card;
    const char mount_point[] = MOUNT_POINT;
    ESP_LOGI(TAG, "Initializing SD card");
    ESP_LOGI(TAG, "Using SDMMC peripheral");
    sdmmc_host_t host = SDMMC_HOST_DEFAULT();
    #if CONFIG_SDMMC_SPEED_HS
        host.max_freq_khz = SDMMC_FREQ_HIGHSPEED;
    #elif CONFIG_SDMMC_SPEED_UHS_I_SDR50
        host.slot = SDMMC_HOST_SLOT_0;
        host.max_freq_khz = SDMMC_FREQ_SDR50;
        host.flags &= ~SDMMC_HOST_FLAG_DDR;
    #elif CONFIG_SDMMC_SPEED_UHS_I_DDR50
        host.slot = SDMMC_HOST_SLOT_0;
        host.max_freq_khz = SDMMC_FREQ_DDR50;
    #elif CONFIG_SDMMC_SPEED_UHS_I_SDR104
        host.slot = SDMMC_HOST_SLOT_0;
        host.max_freq_khz = SDMMC_FREQ_SDR104;
        host.flags &= ~SDMMC_HOST_FLAG_DDR;
    #endif

    #if CONFIG_SD_PWR_CTRL_LDO_INTERNAL_IO
        sd_pwr_ctrl_ldo_config_t ldo_config = {
            .ldo_chan_id = CONFIG_SD_PWR_CTRL_LDO_IO_ID,
        };
        sd_pwr_ctrl_handle_t pwr_ctrl_handle = NULL;

        ret = sd_pwr_ctrl_new_on_chip_ldo(&ldo_config, &pwr_ctrl_handle);
        if (ret != ESP_OK) {
            ESP_LOGE(TAG, "Failed to create a new on-chip LDO power control driver");
            return;
        }
        host.pwr_ctrl_handle = pwr_ctrl_handle;
    #endif

    #if CONFIG_PIN_CARD_POWER_RESET
        ESP_ERROR_CHECK(reset_card_power());
    #endif

    // Modify slot_config.gpio_cd and slot_config.gpio_wp if your board has these signals.
    sdmmc_slot_config_t slot_config = SDMMC_SLOT_CONFIG_DEFAULT();
    #if IS_UHS1
        slot_config.flags |= SDMMC_SLOT_FLAG_UHS1;
    #endif

    #ifdef CONFIG_SDMMC_BUS_WIDTH_4
        slot_config.width = 4;
    #else
        slot_config.width = 1;
    #endif

    #ifdef CONFIG_SOC_SDMMC_USE_GPIO_MATRIX
        slot_config.clk = CONFIG_PIN_CLK;
        slot_config.cmd = CONFIG_PIN_CMD;
        slot_config.d0 = CONFIG_PIN_D0;
        #ifdef CONFIG_SDMMC_BUS_WIDTH_4
            slot_config.d1 = CONFIG_PIN_D1;
            slot_config.d2 = CONFIG_PIN_D2;
            slot_config.d3 = CONFIG_PIN_D3;
        #endif
    #endif

    slot_config.flags |= SDMMC_SLOT_FLAG_INTERNAL_PULLUP;
    ESP_LOGI(TAG, "Mounting filesystem");
    ret = esp_vfs_fat_sdmmc_mount(mount_point, &host, &slot_config, &mount_config, &card);

    if (ret != ESP_OK) {
        if (ret == ESP_FAIL) {
            ESP_LOGE(TAG, "Failed to mount filesystem. "
                     "If you want the card to be formatted, set the FORMAT_IF_MOUNT_FAILED menuconfig option.");
        } else {
            ESP_LOGE(TAG, "Failed to initialize the card (%s). "
                     "Make sure SD card lines have pull-up resistors in place.", esp_err_to_name(ret));
    #ifdef CONFIG_DEBUG_PIN_CONNECTIONS
                check_sd_card_pins(&config, pin_count);
    #endif
            }
            return;
        }
    ESP_LOGI(TAG, "Filesystem mounted");
    sdmmc_card_print_info(stdout, card);
    callback(card);
}

static void gps_event_handler(void *event_handler_arg, esp_event_base_t event_base, int32_t event_id, void *event_data)
{
    xSemaphoreGive(gps_ready_sem);
    switch (event_id) {
    case GPS_UPDATE:
        gps = *((gps_t *)event_data);
        break;
    case GPS_UNKNOWN:
        // ESP_LOGW(TAG, "Unknown statement:%s", (char *)event_data);
        break;
    default:
        break;
    }
}

void app_main(void)
{
    gps_ready_sem = xSemaphoreCreateBinary();
    nmea_parser_config_t config = NMEA_PARSER_CONFIG_DEFAULT();
    nmea_parser_handle_t nmea_hdl = nmea_parser_init(&config);
    nmea_parser_add_handler(nmea_hdl, gps_event_handler, NULL);
    sdcard_setup(wifi_scan);

}

// void deinit()
// {
//     vTaskDelay(10000 / portTICK_PERIOD_MS);
//     nmea_parser_remove_handler(nmea_hdl, gps_event_handler);
//     nmea_parser_deinit(nmea_hdl);
// }
