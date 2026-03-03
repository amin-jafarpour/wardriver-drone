#include <string.h>
#include <sys/unistd.h>
#include <sys/stat.h>
#include "esp_vfs_fat.h"
#include "sdmmc_cmd.h"
#include "driver/sdmmc_host.h"
#include "driver/gpio.h"

#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"
#include "esp_wifi.h"
#include "esp_log.h"
#include "esp_event.h"
#include "nvs_flash.h"
#include "regex.h"



#if SOC_SDMMC_IO_POWER_EXTERNAL
#include "sd_pwr_ctrl_by_on_chip_ldo.h"
#endif

#define DATA_SIZE 500

const char *TAG = "app";

#define MAX_FILE_COUNT 10
#define ALLOCATION_UNIT_SIZE 16 * 1024
#define MOUNT_POINT "/wardriver"
#define IS_UHS1 (CONFIG_SDMMC_SPEED_UHS_I_SDR50 || CONFIG_SDMMC_SPEED_UHS_I_DDR50 || CONFIG_SDMMC_SPEED_UHS_I_SDR104)

#ifdef CONFIG_DEBUG_PIN_CONNECTIONS
const char* names[] = {"CLK", "CMD", "D0", "D1", "D2", "D3"};
const int pins[] = {CONFIG_PIN_CLK,
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
const int adc_channels[] = {CONFIG_ADC_PIN_CLK,
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
    .names = names,
    .pins = pins,
#if CONFIG_ENABLE_ADC_FEATURE
    .adc_channels = adc_channels,
#endif
};
#endif //CONFIG_DEBUG_PIN_CONNECTIONS







#define DEFAULT_SCAN_LIST_SIZE CONFIG_SCAN_LIST_SIZE

#ifdef CONFIG_USE_SCAN_CHANNEL_BITMAP
#define CHANNEL_LIST_SIZE 3
static uint8_t channel_list[CHANNEL_LIST_SIZE] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14}; // {1, 6, 11};
#endif 


extern const char *TAG;

#ifdef CONFIG_USE_SCAN_CHANNEL_BITMAP
static void array_2_channel_bitmap(const uint8_t channel_list[], const uint8_t channel_list_size, wifi_scan_config_t *scan_config) {

    for(uint8_t i = 0; i < channel_list_size; i++) {
        uint8_t channel = channel_list[i];
        scan_config->channel_bitmap.ghz_2_channels |= (1 << channel);
    }
}
#endif

void wifi_scan(sdmmc_card_t *card)
{
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK( ret );

    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_t *sta_netif = esp_netif_create_default_wifi_sta();
    assert(sta_netif);

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));

    uint16_t number = DEFAULT_SCAN_LIST_SIZE;
    wifi_ap_record_t ap_info[DEFAULT_SCAN_LIST_SIZE];
    uint16_t ap_count = 0;
    memset(ap_info, 0, sizeof(ap_info));


    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_start());









 
  
    // char data[DATA_SIZE];
    // snprintf(data, DATA_SIZE, "%s %s!\n", "Hello", card->cid.name);
    // ret = overwrite_file(file_hello, data);
    // if (ret != ESP_OK) {
    //     return;
    // }



    
  
  const char *file_path = "/wardriver.txt";
    while(true)
    {
    FILE *f = fopen(file_path, "a");
    if (f == NULL) {
    perror("fopen");
    return;
    }

    
        #ifdef CONFIG_USE_SCAN_CHANNEL_BITMAP
            wifi_scan_config_t *scan_config = (wifi_scan_config_t *)calloc(1,sizeof(wifi_scan_config_t));
            if (!scan_config) {
                ESP_LOGE(TAG, "Memory Allocation for scan config failed!");
                return;
            }
            array_2_channel_bitmap(channel_list, CHANNEL_LIST_SIZE, scan_config);
            esp_wifi_scan_start(scan_config, true);
            free(scan_config);

        #else
            esp_wifi_scan_start(NULL, true);
        #endif

            ESP_LOGI(TAG, "Max AP number ap_info can hold = %u", number);
            ESP_ERROR_CHECK(esp_wifi_scan_get_ap_num(&ap_count));
            ESP_ERROR_CHECK(esp_wifi_scan_get_ap_records(&number, ap_info));
            ESP_LOGI(TAG, "Total APs scanned = %u, actual AP number ap_info holds = %u", ap_count, number);
            for (int i = 0; i < number; i++) {
                fprintf(f, "Hello log\n");
                ESP_LOGI(TAG, "hi");
            }
        vTaskDelay(pdMS_TO_TICKS(500));
        fclose(f);
    }


}






// static esp_err_t overwrite_file(const char *path, char *data)
// {
//     ESP_LOGI(TAG, "Opening file %s", path);
//     FILE *file = fopen(path, "w");
//     if (file == NULL) {
//         ESP_LOGE(TAG, "Failed to open file for writing");
//         return ESP_FAIL;
//     }
//     fprintf(file, data);
//     fclose(file);
//     ESP_LOGI(TAG, "File written");
//     return ESP_OK;
// }




// static esp_err_t read_file(const char *path)
// {
//     ESP_LOGI(TAG, "Reading file %s", path);
//     FILE *file = fopen(path, "r");
//     if (file == NULL) {
//         ESP_LOGE(TAG, "Failed to open file for reading");
//         return ESP_FAIL;
//     }
//     char line[DATA_SIZE];
//     fgets(line, sizeof(line), file);
//     fclose(file);
//     char *pos = strchr(line, '\n');
//     if (pos) {
//         *pos = '\0';
//     }
//     ESP_LOGI(TAG, "Read from file: '%s'", line);
//     return ESP_OK;
// }

#if CONFIG_PIN_CARD_POWER_RESET
static esp_err_t reset_card_power(void)
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


typedef void (*sdcard_callback)(sdmmc_card_t *card);

void sdcard_setup(sdcard_callback callback)
{
    esp_err_t ret;
    esp_vfs_fat_sdmmc_mount_config_t mount_config = {
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


void app_main(void)
{

    sdcard_setup(wifi_scan);
    // POXIS
    // const char *file_hello = MOUNT_POINT"/hello.txt";
    // char data[DATA_SIZE];
    // snprintf(data, DATA_SIZE, "%s %s!\n", "Hello", card->cid.name);
    // ret = overwrite_file(file_hello, data);
    // if (ret != ESP_OK) {
    //     return;
    // }

//     const char *file_foo = MOUNT_POINT"/foo.txt";
//     struct stat st;
//     if (stat(file_foo, &st) == 0) {
//         unlink(file_foo);
//     }

//     ESP_LOGI(TAG, "Renaming file %s to %s", file_hello, file_foo);
//     if (rename(file_hello, file_foo) != 0) {
//         ESP_LOGE(TAG, "Rename failed");
//         return;
//     }

//     ret = read_file(file_foo);
//     if (ret != ESP_OK) {
//         return;
//     }

// #ifdef CONFIG_FORMAT_SD_CARD
//     ret = esp_vfs_fat_sdcard_format(mount_point, card);
//     if (ret != ESP_OK) {
//         ESP_LOGE(TAG, "Failed to format FATFS (%s)", esp_err_to_name(ret));
//         return;
//     }

//     if (stat(file_foo, &st) == 0) {
//         ESP_LOGI(TAG, "file still exists");
//         return;
//     } else {
//         ESP_LOGI(TAG, "file doesn't exist, formatting done");
//     }
// #endif

//     const char *file_nihao = MOUNT_POINT"/nihao.txt";
//     memset(data, 0, DATA_SIZE);
//     snprintf(data, DATA_SIZE, "%s %s!\n", "Nihao", card->cid.name);
//     ret = overwrite_file(file_nihao, data);
//     if (ret != ESP_OK) {
//         return;
//     }

//     ret = read_file(file_nihao);
//     if (ret != ESP_OK) {
//         return;
//     }

//     esp_vfs_fat_sdcard_unmount(mount_point, card);
//     ESP_LOGI(TAG, "Card unmounted");

// #if CONFIG_SD_PWR_CTRL_LDO_INTERNAL_IO
//     ret = sd_pwr_ctrl_del_on_chip_ldo(pwr_ctrl_handle);
//     if (ret != ESP_OK) {
//         ESP_LOGE(TAG, "Failed to delete the on-chip LDO power control driver");
//         return;
//     }
// #endif
}
