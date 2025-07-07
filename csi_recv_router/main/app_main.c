/*
 * =================================================================================
 * CSI RECEIVER NODE FIRMWARE
 * =================================================================================
 *
 * Objective:
 * To function as an advanced Wi-Fi client for collecting Channel State Information (CSI) data.
 * The firmware supports flexible provisioning for open, WPA2-Personal, and WPA2-Enterprise
 * (PEAP) networks and is designed for low-power operation through a deep sleep cycle.
 *
 * Core Functionalities:
 * 1.  Flexible Provisioning: Listens for UDP packets to configure network credentials
 * and server details.
 * 2.  Multi-Authentication Support: Connects to various network types based on
 * the provisioned configuration.
 * 3.  Traffic Generation: Pings the network gateway to generate CSI data.
 * 4.  Data Transmission: Forwards collected CSI data to a designated server via UDP.
 * 5.  Power Management: Enters a deep sleep cycle to conserve energy between
 * acquisition sessions.
 * 6.  IP Discovery: Broadcasts its IP address upon connection to facilitate discovery.
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"
#include "freertos/semphr.h"
#include "nvs_flash.h"
#include "esp_mac.h"
#include "rom/ets_sys.h"
#include "esp_log.h"
#include "esp_wifi.h"
#include "esp_wpa2.h"
#include "esp_netif.h"
#include "lwip/inet.h"
#include "lwip/netdb.h"
#include "lwip/sockets.h"
#include "ping/ping_sock.h"
#include "esp_system.h"
#include "esp_event.h"
#include "nvs.h"
#include "driver/gpio.h"
#include "esp_sleep.h"

// --- System Definitions ---
#define CONFIG_SEND_FREQUENCY      100
#define WIFI_PROV_AP_SSID          "ESP_PROV"
#define WIFI_PROV_AP_PASS          "12345678"
#define WIFI_PROV_UDP_PORT         50000
#define WIFI_PROV_NAMESPACE        "wifi_prov"
#define WIFI_PROV_KEY_SSID         "ssid"
#define WIFI_PROV_KEY_PASS         "pass"
#define WIFI_PROV_KEY_IDENTITY     "identity"
#define WIFI_PROV_KEY_AUTH         "auth_type"
#define WIFI_PROV_KEY_SRV_IP       "server_ip"
#define WIFI_PROV_KEY_SRV_PORT     "server_port"
#define WIFI_PROV_MAX_LEN          128
#define WIFI_CONNECTED_BIT         BIT0
#define BOOT_BUTTON_GPIO           0
#define DEEP_SLEEP_INTERVAL_S      5
#define UDP_LISTEN_WINDOW_S        10
#define UDP_LISTEN_PORT            50000
#define IP_BROADCAST_PORT          50002

static const char *TAG = "csi_receiver_node";

// Global variables for the server IP and Port, loaded from NVS
static char g_csi_server_ip[16] = "127.0.0.1";
static int  g_csi_server_port = 50000;
static EventGroupHandle_t s_wifi_event_group;
static int wifi_fail_count = 0;

// Function Prototypes
static void erase_wifi_creds_and_restart(void);
static void wifi_event_handler(void* arg, esp_event_base_t event_base, int32_t event_id, void* event_data);

typedef struct {
    unsigned : 32; unsigned : 32; unsigned : 32; unsigned : 32; unsigned : 32;
#if CONFIG_IDF_TARGET_ESP32S3 || CONFIG_IDF_TARGET_ESP32C3 || CONFIG_IDF_TARGET_ESP32C5 ||CONFIG_IDF_TARGET_ESP32C6
    unsigned : 16; unsigned fft_gain : 8; unsigned agc_gain : 8; unsigned : 32;
#endif
    unsigned : 32;
#if CONFIG_IDF_TARGET_ESP32S3 || CONFIG_IDF_TARGET_ESP32C3 || CONFIG_IDF_TARGET_ESP32C5
    unsigned : 32; unsigned : 32; unsigned : 32;
#endif
    unsigned : 32;
} wifi_pkt_rx_ctrl_phy_t;

#define CONFIG_FORCE_GAIN 1
#if CONFIG_FORCE_GAIN
    extern void phy_fft_scale_force(bool force_en, uint8_t force_value);
    extern void phy_force_rx_gain(int force_en, int force_value);
#endif

static void send_csi_udp(const char *data, size_t len) {
    static int sock = -1;
    static struct sockaddr_in dest_addr;
    static char last_ip[16] = {0};
    static int last_port = 0;

    if (sock < 0 || strcmp(last_ip, g_csi_server_ip) != 0 || last_port != g_csi_server_port) {
        if (sock >= 0) {
            close(sock);
        }
        sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_IP);
        if (sock < 0) {
            ESP_LOGE(TAG, "Failed to create UDP socket for CSI");
            return;
        }
        dest_addr.sin_addr.s_addr = inet_addr(g_csi_server_ip);
        dest_addr.sin_family = AF_INET;
        dest_addr.sin_port = htons(g_csi_server_port);
        
        strlcpy(last_ip, g_csi_server_ip, sizeof(last_ip));
        last_port = g_csi_server_port;
        
        ESP_LOGI(TAG, "Configured to send CSI data to %s:%d", g_csi_server_ip, g_csi_server_port);
    }
    sendto(sock, data, len, 0, (struct sockaddr *)&dest_addr, sizeof(dest_addr));
}

static void wifi_csi_rx_cb(void *ctx, wifi_csi_info_t *info)
{
    if (!info || !info->buf) {
        return;
    }
    if (memcmp(info->mac, ctx, 6)) {
        return;
    }
    static int s_count = 0;
    const wifi_pkt_rx_ctrl_t *rx_ctrl = &info->rx_ctrl;
    char csi_msg[1024];
    int offset = 0;

    offset += snprintf(csi_msg + offset, sizeof(csi_msg) - offset, "CSI_DATA,%d," MACSTR,
                       s_count++, MAC2STR(info->mac));

    offset += snprintf(csi_msg + offset, sizeof(csi_msg) - offset,
                       ",%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%u,%d,%d,%d",
                       rx_ctrl->rssi, rx_ctrl->rate, rx_ctrl->sig_mode,
                       rx_ctrl->mcs, rx_ctrl->cwb, rx_ctrl->smoothing, rx_ctrl->not_sounding,
                       rx_ctrl->aggregation, rx_ctrl->stbc, rx_ctrl->fec_coding, rx_ctrl->sgi,
                       rx_ctrl->noise_floor, rx_ctrl->ampdu_cnt, rx_ctrl->channel, rx_ctrl->secondary_channel,
                       rx_ctrl->timestamp, rx_ctrl->ant, rx_ctrl->sig_len, rx_ctrl->rx_state);

    offset += snprintf(csi_msg + offset, sizeof(csi_msg) - offset, ",%d,%d,\"[%d", 
                       info->len, info->first_word_invalid, info->buf[0]);

    for (int i = 1; i < info->len; i++) {
        offset += snprintf(csi_msg + offset, sizeof(csi_msg) - offset, ",%d", info->buf[i]);
    }
    
    snprintf(csi_msg + offset, sizeof(csi_msg) - offset, "]\"\n");

    send_csi_udp(csi_msg, strlen(csi_msg));
}

static void wifi_csi_init()
{
    wifi_csi_config_t csi_config = {
        .lltf_en           = true,
        .htltf_en          = false,
        .stbc_htltf2_en    = false,
        .ltf_merge_en      = true,
        .channel_filter_en = true,
        .manu_scale        = true,
        .shift             = true,
    };
    static wifi_ap_record_t s_ap_info = {0};
    ESP_ERROR_CHECK(esp_wifi_sta_get_ap_info(&s_ap_info));
    ESP_ERROR_CHECK(esp_wifi_set_csi_config(&csi_config));
    ESP_ERROR_CHECK(esp_wifi_set_csi_rx_cb(wifi_csi_rx_cb, s_ap_info.bssid));
    ESP_ERROR_CHECK(esp_wifi_set_csi(true));
}

static esp_err_t wifi_ping_router_start()
{
    static esp_ping_handle_t ping_handle = NULL;
    esp_ping_config_t ping_config = ESP_PING_DEFAULT_CONFIG();
    ping_config.count             = 0;
    ping_config.interval_ms       = 1000 / CONFIG_SEND_FREQUENCY;
    ping_config.task_stack_size   = 3072;
    ping_config.data_size         = 1;
    esp_netif_ip_info_t local_ip;
    esp_netif_get_ip_info(esp_netif_get_handle_from_ifkey("WIFI_STA_DEF"), &local_ip);
    ESP_LOGI(TAG, "Obtained IP:" IPSTR ", Gateway: " IPSTR, IP2STR(&local_ip.ip), IP2STR(&local_ip.gw));
    ping_config.target_addr.u_addr.ip4.addr = ip4_addr_get_u32(&local_ip.gw);
    ping_config.target_addr.type = ESP_IPADDR_TYPE_V4;
    esp_ping_callbacks_t cbs = { 0 };
    esp_ping_new_session(&ping_config, &cbs, &ping_handle);
    esp_ping_start(ping_handle);
    return ESP_OK;
}

static void start_wifi_ap(void) {
    esp_netif_create_default_wifi_ap();
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));
    wifi_config_t ap_config = {
        .ap = {
            .ssid = WIFI_PROV_AP_SSID,
            .ssid_len = strlen(WIFI_PROV_AP_SSID),
            .password = WIFI_PROV_AP_PASS,
            .max_connection = 4,
            .authmode = WIFI_AUTH_WPA_WPA2_PSK
        }
    };
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_AP));
    ESP_ERROR_CHECK(esp_wifi_set_config(ESP_IF_WIFI_AP, &ap_config));
    ESP_ERROR_CHECK(esp_wifi_start());
    ESP_LOGI(TAG, "Provisioning AP started: SSID: %s, password: %s", WIFI_PROV_AP_SSID, WIFI_PROV_AP_PASS);
}

static esp_err_t save_wifi_creds(const char *ssid, const char *pass, const char *identity, const char *auth_type, const char *ip, int port) {
    nvs_handle_t nvs;
    esp_err_t err = nvs_open(WIFI_PROV_NAMESPACE, NVS_READWRITE, &nvs);
    if (err != ESP_OK) return err;
    err = nvs_set_str(nvs, WIFI_PROV_KEY_SSID, ssid);
    if (err == ESP_OK) err = nvs_set_str(nvs, WIFI_PROV_KEY_PASS, pass);
    if (err == ESP_OK) err = nvs_set_str(nvs, WIFI_PROV_KEY_IDENTITY, identity);
    if (err == ESP_OK) err = nvs_set_str(nvs, WIFI_PROV_KEY_AUTH, auth_type);
    if (err == ESP_OK) err = nvs_set_str(nvs, WIFI_PROV_KEY_SRV_IP, ip);
    if (err == ESP_OK) err = nvs_set_i32(nvs, WIFI_PROV_KEY_SRV_PORT, port);
    if (err == ESP_OK) err = nvs_commit(nvs);
    nvs_close(nvs);
    return err;
}

static esp_err_t load_wifi_creds(char *ssid, char *pass, char *identity, char *auth_type, char *ip, int *port) {
    nvs_handle_t nvs;
    esp_err_t err = nvs_open(WIFI_PROV_NAMESPACE, NVS_READONLY, &nvs);
    if (err != ESP_OK) return err;
    size_t len;

    len = WIFI_PROV_MAX_LEN; err = nvs_get_str(nvs, WIFI_PROV_KEY_SSID, ssid, &len); if (err != ESP_OK) goto exit;
    len = WIFI_PROV_MAX_LEN; err = nvs_get_str(nvs, WIFI_PROV_KEY_PASS, pass, &len); if (err != ESP_OK) goto exit;
    len = 16;                err = nvs_get_str(nvs, WIFI_PROV_KEY_AUTH, auth_type, &len); if (err != ESP_OK) goto exit;
    len = 16;                err = nvs_get_str(nvs, WIFI_PROV_KEY_SRV_IP, ip, &len); if (err != ESP_OK) goto exit;
    err = nvs_get_i32(nvs, WIFI_PROV_KEY_SRV_PORT, port); if (err != ESP_OK) goto exit;
    
    len = WIFI_PROV_MAX_LEN;
    if (nvs_get_str(nvs, WIFI_PROV_KEY_IDENTITY, identity, &len) != ESP_OK) {
        identity[0] = '\0';
    }

exit:
    nvs_close(nvs);
    return err;
}

static void udp_prov_task(void *pvParameter) {
    int sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_IP);
    struct sockaddr_in server_addr, source_addr;
    socklen_t socklen = sizeof(source_addr);
    char rx_buffer[256];
    char ssid[WIFI_PROV_MAX_LEN] = {0}, pass[WIFI_PROV_MAX_LEN] = {0}, identity[WIFI_PROV_MAX_LEN] = {0},
         auth_type[16] = {0}, server_ip[16] = {0};
    int server_port = 0;
    
    if (sock < 0) {
        ESP_LOGE(TAG, "Failed to create UDP socket");
        vTaskDelete(NULL);
        return;
    }

    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(WIFI_PROV_UDP_PORT);
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    bind(sock, (struct sockaddr *)&server_addr, sizeof(server_addr));

    ESP_LOGI(TAG, "Awaiting credentials via UDP on port %d...", WIFI_PROV_UDP_PORT);
    int len = recvfrom(sock, rx_buffer, sizeof(rx_buffer) - 1, 0, (struct sockaddr *)&source_addr, &socklen);

    if (len > 0) {
        rx_buffer[len] = 0;
        
        char *p = rx_buffer;
        char *token;
        int field_count = 0;
        
        while ((token = strtok_r(p, ",", &p)) != NULL) {
            switch(field_count) {
                case 0: strlcpy(auth_type, token, sizeof(auth_type)); break;
                case 1: strlcpy(ssid, token, sizeof(ssid)); break;
                case 2:
                    if (strcmp(auth_type, "peap") == 0) { strlcpy(identity, token, sizeof(identity)); }
                    else { strlcpy(pass, token, sizeof(pass)); }
                    break;
                case 3:
                    if (strcmp(auth_type, "peap") == 0) { strlcpy(pass, token, sizeof(pass)); }
                    else { strlcpy(server_ip, token, sizeof(server_ip)); }
                    break;
                case 4:
                    if (strcmp(auth_type, "peap") == 0) { strlcpy(server_ip, token, sizeof(server_ip)); }
                    else server_port = atoi(token);
                    break;
                case 5:
                    if (strcmp(auth_type, "peap") == 0) server_port = atoi(token);
                    break;
            }
            field_count++;
        }

        ESP_LOGI(TAG, "Provisioning received: Auth=%s, SSID=%s, ID=%s, Pass=%s, IP=%s, Port=%d", 
                 auth_type, ssid, identity, pass, server_ip, server_port);
        
        if (strlen(auth_type) > 0 && strlen(ssid) > 0) {
            if (save_wifi_creds(ssid, pass, identity, auth_type, server_ip, server_port) == ESP_OK) {
                ESP_LOGI(TAG, "Credentials saved. Restarting...");
                vTaskDelay(1000 / portTICK_PERIOD_MS);
                esp_restart();
            }
        } else {
            ESP_LOGE(TAG, "Invalid provisioning format.");
        }
    }
    close(sock);
    vTaskDelete(NULL);
}

static void start_wifi_sta(const char *ssid, const char *pass, const char *identity, const char *auth_type) {
    esp_netif_create_default_wifi_sta();
    
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));
    
    wifi_config_t sta_config;
    memset(&sta_config, 0, sizeof(sta_config));
    
    strlcpy((char *)sta_config.sta.ssid, ssid, sizeof(sta_config.sta.ssid));

    if (strcmp(auth_type, "peap") == 0) {
        ESP_LOGI(TAG, "Configuring for WPA2-Enterprise (PEAP) network.");
        esp_wifi_sta_wpa2_ent_set_identity((const uint8_t *)identity, strlen(identity));
        esp_wifi_sta_wpa2_ent_set_username((const uint8_t *)identity, strlen(identity));
        esp_wifi_sta_wpa2_ent_set_password((const uint8_t *)pass, strlen(pass));
        ESP_ERROR_CHECK(esp_wifi_sta_wpa2_ent_enable());
    } else if (strcmp(auth_type, "wpa2psk") == 0) {
        ESP_LOGI(TAG, "Configuring for WPA2-Personal network.");
        strlcpy((char *)sta_config.sta.password, pass, sizeof(sta_config.sta.password));
        sta_config.sta.threshold.authmode = WIFI_AUTH_WPA2_PSK;
    } else {
        ESP_LOGI(TAG, "Configuring for open network.");
        sta_config.sta.threshold.authmode = WIFI_AUTH_OPEN;
    }
    
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_set_config(ESP_IF_WIFI_STA, &sta_config));
    ESP_ERROR_CHECK(esp_wifi_start());
    ESP_LOGI(TAG, "Connecting to Wi-Fi: %s", ssid);
}

static void wifi_event_handler(void* arg, esp_event_base_t event_base, int32_t event_id, void* event_data) {
    if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_START) {
        esp_wifi_connect();
    } else if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_CONNECTED) {
        ESP_LOGI(TAG, "Wi-Fi connected to AP");
        wifi_fail_count = 0;
    } else if (event_base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP) {
        ESP_LOGI(TAG, "Wi-Fi obtained IP address");
        xEventGroupSetBits(s_wifi_event_group, WIFI_CONNECTED_BIT);
    } else if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_DISCONNECTED) {
        ESP_LOGI(TAG, "Wi-Fi disconnected, attempting to reconnect...");
        wifi_fail_count++;
        if (wifi_fail_count >= 15) {
            ESP_LOGW(TAG, "15 failed connection attempts. Erasing credentials...");
            erase_wifi_creds_and_restart();
        }
        esp_wifi_connect();
    }
}

static void erase_wifi_creds_and_restart(void) {
    esp_wifi_stop();
    nvs_handle_t nvs;
    if (nvs_open(WIFI_PROV_NAMESPACE, NVS_READWRITE, &nvs) == ESP_OK) {
        nvs_erase_key(nvs, WIFI_PROV_KEY_SSID);
        nvs_erase_key(nvs, WIFI_PROV_KEY_PASS);
        nvs_erase_key(nvs, WIFI_PROV_KEY_IDENTITY);
        nvs_erase_key(nvs, WIFI_PROV_KEY_AUTH);
        nvs_erase_key(nvs, WIFI_PROV_KEY_SRV_IP);
        nvs_erase_key(nvs, WIFI_PROV_KEY_SRV_PORT);
        nvs_commit(nvs);
        nvs_close(nvs);
    }
    ESP_LOGI(TAG, "Wi-Fi credentials erased! Restarting...");
    vTaskDelay(1000 / portTICK_PERIOD_MS);
    esp_restart();
}

static void enter_deep_sleep(uint64_t sleep_time_s) {
    ESP_LOGI(TAG, "Entering deep sleep for %llu seconds...", sleep_time_s);
    vTaskDelay(100 / portTICK_PERIOD_MS);
    esp_deep_sleep(sleep_time_s * 1000000ULL);
}

static int udp_listen_for_start() {
    int sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_IP);
    struct sockaddr_in server_addr, source_addr;
    socklen_t socklen = sizeof(source_addr);
    char rx_buffer[64];
    int csi_time = 0;
    if (sock < 0) {
        ESP_LOGE(TAG, "Failed to create UDP socket for start command listener");
        return 0;
    }
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(UDP_LISTEN_PORT);
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    bind(sock, (struct sockaddr *)&server_addr, sizeof(server_addr));
    ESP_LOGI(TAG, "Awaiting 'start' command via UDP on port %d for %d seconds...", UDP_LISTEN_PORT, UDP_LISTEN_WINDOW_S);
    struct timeval timeout = { .tv_sec = 1, .tv_usec = 0 };
    setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
    int listen_time = 0;
    while (listen_time < UDP_LISTEN_WINDOW_S) {
        int len = recvfrom(sock, rx_buffer, sizeof(rx_buffer) - 1, 0, (struct sockaddr *)&source_addr, &socklen);
        if (len > 0) {
            rx_buffer[len] = 0;
            if (strncmp(rx_buffer, "start,", 6) == 0) {
                csi_time = atoi(rx_buffer + 6);
                ESP_LOGI(TAG, "'start' command received: %d seconds", csi_time);
                break;
            }
        }
        listen_time++;
    }
    close(sock);
    return csi_time;
}

static void check_for_factory_reset_request(void) {
    gpio_config_t io_conf;
    io_conf.pin_bit_mask = (1ULL << BOOT_BUTTON_GPIO);
    io_conf.mode = GPIO_MODE_INPUT;
    io_conf.pull_up_en = 1;
    io_conf.pull_down_en = 0;
    io_conf.intr_type = GPIO_INTR_DISABLE;
    gpio_config(&io_conf);

    ESP_LOGI(TAG, "Checking for factory reset request via boot button...");
    vTaskDelay(50 / portTICK_PERIOD_MS);

    if (gpio_get_level(BOOT_BUTTON_GPIO) == 0) {
        ESP_LOGW(TAG, "Boot button pressed at startup. Waiting 3 seconds to confirm factory reset...");
        int press_time_ms = 0;
        while(gpio_get_level(BOOT_BUTTON_GPIO) == 0 && press_time_ms < 3000) {
            vTaskDelay(100 / portTICK_PERIOD_MS);
            press_time_ms += 100;
        }

        if (press_time_ms >= 3000) {
            ESP_LOGE(TAG, "Factory reset confirmed! Erasing credentials...");
            erase_wifi_creds_and_restart();
        } else {
            ESP_LOGI(TAG, "Button released prematurely. Normal operation.");
        }
    } else {
        ESP_LOGI(TAG, "No reset request detected.");
    }
}

void send_ip_broadcast_task(void *pvParameters) {
    xEventGroupWaitBits(s_wifi_event_group, WIFI_CONNECTED_BIT, pdFALSE, pdTRUE, portMAX_DELAY);

    esp_netif_ip_info_t ip_info;
    esp_netif_t *netif = esp_netif_get_handle_from_ifkey("WIFI_STA_DEF");
    esp_netif_get_ip_info(netif, &ip_info);
    char ip_addr_str[16];
    inet_ntoa_r(ip_info.ip, ip_addr_str, sizeof(ip_addr_str) - 1);

    ESP_LOGI(TAG, "Starting IP broadcast task. Announcing IP: %s", ip_addr_str);

    int sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_IP);
    if (sock < 0) {
        ESP_LOGE(TAG, "Failed to create broadcast socket");
        vTaskDelete(NULL);
        return;
    }

    int broadcast = 1;
    if (setsockopt(sock, SOL_SOCKET, SO_BROADCAST, &broadcast, sizeof(broadcast)) < 0) {
        ESP_LOGE(TAG, "Failed to set socket for broadcast");
        close(sock);
        vTaskDelete(NULL);
        return;
    }

    struct sockaddr_in dest_addr;
    dest_addr.sin_family = AF_INET;
    dest_addr.sin_port = htons(IP_BROADCAST_PORT);
    dest_addr.sin_addr.s_addr = inet_addr("255.255.255.255");

    char message[32];
    snprintf(message, sizeof(message), "CSI_IP,%s", ip_addr_str);

    for (int i = 0; i < 10; i++) {
        sendto(sock, message, strlen(message), 0, (struct sockaddr *)&dest_addr, sizeof(dest_addr));
        ESP_LOGI(TAG, "Broadcast packet sent: %s", message);
        vTaskDelay(2000 / portTICK_PERIOD_MS);
    }

    ESP_LOGI(TAG, "IP broadcast task finished.");
    close(sock);
    vTaskDelete(NULL);
}


void app_main()
{
    ESP_ERROR_CHECK(nvs_flash_init());
    
    check_for_factory_reset_request();
    
    char ssid[WIFI_PROV_MAX_LEN] = {0}, pass[WIFI_PROV_MAX_LEN] = {0}, 
         identity[WIFI_PROV_MAX_LEN] = {0}, auth_type[16] = {0}, 
         server_ip[16] = {0};
    int server_port = 0;
    
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    
    s_wifi_event_group = xEventGroupCreate();
    ESP_ERROR_CHECK(esp_event_handler_instance_register(WIFI_EVENT, ESP_EVENT_ANY_ID, &wifi_event_handler, NULL, NULL));
    ESP_ERROR_CHECK(esp_event_handler_instance_register(IP_EVENT, IP_EVENT_STA_GOT_IP, &wifi_event_handler, NULL, NULL));

    if (load_wifi_creds(ssid, pass, identity, auth_type, server_ip, &server_port) == ESP_OK) {
        strlcpy(g_csi_server_ip, server_ip, sizeof(g_csi_server_ip));
        g_csi_server_port = server_port;

        xTaskCreate(send_ip_broadcast_task, "ip_broadcast_task", 4096, NULL, 5, NULL);

        while (1) {
            start_wifi_sta(ssid, pass, identity, auth_type);
            xEventGroupWaitBits(s_wifi_event_group, WIFI_CONNECTED_BIT, pdFALSE, pdTRUE, portMAX_DELAY);
            int csi_time = udp_listen_for_start();
            if (csi_time > 0) {
                ESP_LOGI(TAG, "Initiating CSI acquisition for %d seconds", csi_time);
                wifi_csi_init();
                wifi_ping_router_start();
                vTaskDelay(csi_time * 1000 / portTICK_PERIOD_MS);
                ESP_LOGI(TAG, "CSI acquisition finished. Entering deep sleep.");
                esp_wifi_stop();
                enter_deep_sleep(DEEP_SLEEP_INTERVAL_S);
            } else {
                ESP_LOGI(TAG, "No 'start' command received. Entering deep sleep.");
                esp_wifi_stop();
                enter_deep_sleep(DEEP_SLEEP_INTERVAL_S);
            }
        }
    } else {
        ESP_LOGI(TAG, "No credentials found. Starting provisioning mode.");
        start_wifi_ap();
        xTaskCreate(udp_prov_task, "udp_prov_task", 4096, NULL, 5, NULL);
    }
}
