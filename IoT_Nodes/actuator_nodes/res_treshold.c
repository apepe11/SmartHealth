#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "contiki.h"
#include "coap-engine.h"

// Variabile globale definita nel main dell'attuatore
extern float alarm_threshold; 

static void threshold_get_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset);
static void threshold_put_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset);

RESOURCE(res_threshold,
         "title=\"Alarm Threshold\";rt=\"Control\"",
         threshold_get_handler,
         NULL,
         threshold_put_handler,
         NULL);

static void threshold_get_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset) {    
    int length;
    char payload[60];
    
    // Converte la soglia (es. 0.85) in intero percentuale (es. 85) per semplicità
    snprintf(payload, sizeof(payload), "{\"threshold\": %d}", (int)(alarm_threshold * 100));
    length = strlen(payload);
        
    coap_set_header_content_format(response, APPLICATION_JSON);
    coap_set_payload(response, (uint8_t *)payload, length);
}

static void threshold_put_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset) {
    const uint8_t *payload;
    int new_t_int;
    
    int len = coap_get_payload(request, &payload);
    if(len > 0) {
        char temp[32];
        memcpy(temp, payload, len);
        temp[len] = '\0';
        
        // Estrazione del valore JSON {"new_t": "85"}
        char *ptr = strstr(temp, "\"new_t\":");
        if(ptr != NULL) {
            // Estrae il numero saltando i caratteri extra
            if(sscanf(ptr, "\"new_t\": \"%d\"", &new_t_int) == 1 || sscanf(ptr, "\"new_t\": %d", &new_t_int) == 1) {
                if(new_t_int >= 0 && new_t_int <= 100) {
                    alarm_threshold = (float)new_t_int / 100.0;
                    printf("[Attuatore] Nuova soglia impostata: %.2f\n", alarm_threshold);
                    coap_set_status_code(response, CHANGED_2_04);
                    return;
                }
            }
        }
    }
    coap_set_status_code(response, BAD_REQUEST_4_00);
}