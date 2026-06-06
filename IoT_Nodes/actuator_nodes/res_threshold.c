#include "coap-engine.h"


extern int alarm_threshold;
extern int current_risk;

void update_leds_by_threshold(int risk);

static void threshold_get_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset);
static void threshold_put_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset);


RESOURCE(res_threshold,
         "title=\"Alarm Threshold\";rt=\"Control\"",
         threshold_get_handler,
         NULL,
         threshold_put_handler,
         NULL);


static void threshold_get_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset)
{
    char payload[64];
    snprintf(payload, sizeof(payload), "{\"threshold\": %d, \"current_risk\": %d}", alarm_threshold, current_risk);
    
    coap_set_header_content_format(response, APPLICATION_JSON);
    coap_set_payload(response, (uint8_t *)payload, strlen(payload));
    printf("[Server CoAP] Ricevuto GET /threshold\n");
}

static void threshold_put_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset)
{
    const uint8_t *payload;
    int len = coap_get_payload(request, &payload);
    int new_threshold;
    
    if(len > 0) {
        char temp[64];
        if(len < (int)sizeof(temp)) {
            memcpy(temp, payload, len);
            temp[len] = '\0';
            
            if(sscanf(temp, "{\"threshold\":%d}", &new_threshold) == 1 ||
               sscanf(temp, "{\"threshold\": %d}", &new_threshold) == 1) {
                
                if(new_threshold >= 0 && new_threshold <= 2) {
                    printf("[Server CoAP] Cambio soglia da Cloud: %d -> %d\n", alarm_threshold, new_threshold);
                    alarm_threshold = new_threshold;
                    
                    update_leds_by_threshold(current_risk);
                    
                    coap_set_status_code(response, CHANGED_2_04);
                    return;
                }
            }
        }
    }
    coap_set_status_code(response, BAD_REQUEST_4_00);
}

void threshold_resource_init(void)
{
    coap_activate_resource(&res_threshold, "threshold");
    printf("[Server CoAP] Risorsa /threshold attivata con successo.\n");
}