#include <string.h>
#include <sys/unistd.h>
#include <sys/stat.h>
#include "esp_vfs_fat.h"
#include "sdmmc_cmd.h"
#include "driver/sdmmc_host.h"
#include "driver/gpio.h"
#if SOC_SDMMC_IO_POWER_EXTERNAL
#include "sd_pwr_ctrl_by_on_chip_ldo.h"
#endif

#define DATA_SIZE 500

static const char *TAG = "example";

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

static esp_err_t overwrite_file(const char *path, char *data)
{
    ESP_LOGI(TAG, "Opening file %s", path);
    FILE *file = fopen(path, "w");
    if (file == NULL) {
        ESP_LOGE(TAG, "Failed to open file for writing");
        return ESP_FAIL;
    }
    fprintf(file, data);
    fclose(file);
    ESP_LOGI(TAG, "File written");
    return ESP_OK;
}

static esp_err_t read_file(const char *path)
{
    ESP_LOGI(TAG, "Reading file %s", path);
    FILE *file = fopen(path, "r");
    if (file == NULL) {
        ESP_LOGE(TAG, "Failed to open file for reading");
        return ESP_FAIL;
    }
    char line[DATA_SIZE];
    fgets(line, sizeof(line), file);
    fclose(file);
    char *pos = strchr(line, '\n');
    if (pos) {
        *pos = '\0';
    }
    ESP_LOGI(TAG, "Read from file: '%s'", line);
    return ESP_OK;
}

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

void app_main(void)
{
    esp_err_t ret;
    esp_vfs_fat_sdmmc_mount_config_t mount_config = {
#ifdef CONFIG_FORMAT_IF_MOUNT_FAILED
        .format_if_mount_failed = true,
#else
        .format_if_mount_failed = false,
#endif
        .max_files = 5,
        .allocation_unit_size = 16 * 1024
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
   
    // POXIS
    const char *file_hello = MOUNT_POINT"/hello.txt";
    char data[DATA_SIZE];
    snprintf(data, DATA_SIZE, "%s %s!\n", "Hello", card->cid.name);
    ret = overwrite_file(file_hello, data);
    if (ret != ESP_OK) {
        return;
    }

    const char *file_foo = MOUNT_POINT"/foo.txt";
    struct stat st;
    if (stat(file_foo, &st) == 0) {
        unlink(file_foo);
    }

    ESP_LOGI(TAG, "Renaming file %s to %s", file_hello, file_foo);
    if (rename(file_hello, file_foo) != 0) {
        ESP_LOGE(TAG, "Rename failed");
        return;
    }

    ret = read_file(file_foo);
    if (ret != ESP_OK) {
        return;
    }

#ifdef CONFIG_FORMAT_SD_CARD
    ret = esp_vfs_fat_sdcard_format(mount_point, card);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to format FATFS (%s)", esp_err_to_name(ret));
        return;
    }

    if (stat(file_foo, &st) == 0) {
        ESP_LOGI(TAG, "file still exists");
        return;
    } else {
        ESP_LOGI(TAG, "file doesn't exist, formatting done");
    }
#endif

    const char *file_nihao = MOUNT_POINT"/nihao.txt";
    memset(data, 0, DATA_SIZE);
    snprintf(data, DATA_SIZE, "%s %s!\n", "Nihao", card->cid.name);
    ret = overwrite_file(file_nihao, data);
    if (ret != ESP_OK) {
        return;
    }

    ret = read_file(file_nihao);
    if (ret != ESP_OK) {
        return;
    }

    esp_vfs_fat_sdcard_unmount(mount_point, card);
    ESP_LOGI(TAG, "Card unmounted");

#if CONFIG_SD_PWR_CTRL_LDO_INTERNAL_IO
    ret = sd_pwr_ctrl_del_on_chip_ldo(pwr_ctrl_handle);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to delete the on-chip LDO power control driver");
        return;
    }
#endif
}
