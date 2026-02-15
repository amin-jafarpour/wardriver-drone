idf_component_register(SRCS "scan.c" "main.c"
                    PRIV_REQUIRES esp_wifi nvs_flash
                    INCLUDE_DIRS ".")