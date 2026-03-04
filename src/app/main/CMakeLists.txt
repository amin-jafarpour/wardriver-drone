set(srcs "main.c" "nmea_parser.c")

idf_component_register(SRCS ${srcs}
                       INCLUDE_DIRS "."
                       REQUIRES esp_event esp_driver_uart fatfs  
                       PRIV_REQUIRES esp_wifi nvs_flash
                       WHOLE_ARCHIVE)

if(NOT CONFIG_SOC_SDMMC_HOST_SUPPORTED)
    fail_at_build_time(sdcard ""
                             "Only ESP32 and ESP32-S3 targets are supported."
                             "Please refer README.md for more details")
endif()
