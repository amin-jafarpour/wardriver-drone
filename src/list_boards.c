#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <sys/stat.h>
#include <limits.h>
#include <errno.h>

static int is_real_usb_serial(const char *name) {
    if (strncmp(name, "ttyACM", 6) == 0) return 1;  // CDC ACM (Arduino, ESP32-S3, etc.)
    if (strncmp(name, "ttyUSB", 6) == 0) return 1;  // USB-UART (CH340, CP2102, FTDI)
    return 0;
}

static void read_sysfs_string(const char *path, char *buf, size_t size) {
    FILE *f = fopen(path, "r");
    if (!f) {
        buf[0] = 0;
        return;
    }
    if (!fgets(buf, size, f)) {
        buf[0] = 0;
    }
    buf[strcspn(buf, "\n")] = 0;  // strip newline
    fclose(f);
}

int main(void) {
    DIR *d = opendir("/dev");
    if (!d) {
        perror("opendir");
        return 1;
    }

    printf("Detected USB boards:\n\n");

    struct dirent *ent;
    int found = 0;

    while ((ent = readdir(d)) != NULL) {
        if (!is_real_usb_serial(ent->d_name))
            continue;

        char devpath[PATH_MAX];
        if (snprintf(devpath, sizeof(devpath), "/dev/%s", ent->d_name)
            >= (int)sizeof(devpath)) {
            // Path truncated, skip this entry
            continue;
        }

        char vid_path[PATH_MAX];
        char pid_path[PATH_MAX];
        char prod_path[PATH_MAX];
        char manu_path[PATH_MAX];

        if (snprintf(vid_path, sizeof(vid_path),
                     "/sys/class/tty/%s/device/../idVendor",
                     ent->d_name) >= (int)sizeof(vid_path)) {
            continue;
        }

        if (snprintf(pid_path, sizeof(pid_path),
                     "/sys/class/tty/%s/device/../idProduct",
                     ent->d_name) >= (int)sizeof(pid_path)) {
            continue;
        }

        if (snprintf(prod_path, sizeof(prod_path),
                     "/sys/class/tty/%s/device/../product",
                     ent->d_name) >= (int)sizeof(prod_path)) {
            continue;
        }

        if (snprintf(manu_path, sizeof(manu_path),
                     "/sys/class/tty/%s/device/../manufacturer",
                     ent->d_name) >= (int)sizeof(manu_path)) {
            continue;
        }

        char vid[32];
        char pid[32];
        char product[256];
        char manu[256];

        read_sysfs_string(vid_path, vid, sizeof(vid));
        read_sysfs_string(pid_path, pid, sizeof(pid));
        read_sysfs_string(prod_path, product, sizeof(product));
        read_sysfs_string(manu_path, manu, sizeof(manu));

        found = 1;
        printf("Port: %s\n", devpath);
        printf("  VID:PID     %s:%s\n", *vid ? vid : "??", *pid ? pid : "??");
        printf("  Manufacturer: %s\n", *manu ? manu : "(unknown)");
        printf("  Product:      %s\n\n", *product ? product : "(unknown)");
    }

    closedir(d);

    if (!found)
        printf("No USB boards detected.\n");

    return 0;
}