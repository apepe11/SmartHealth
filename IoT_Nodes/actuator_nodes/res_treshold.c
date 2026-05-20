#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "contiki.h"
#include "coap-engine.h"
#include "os/dev/leds.h" // Aggiunto controllo hardware LED

extern int alarm_threshold; 

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
    
    snprintf(payload, sizeof(payload), "{\"threshold\": %d}", alarm_threshold);
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
        
        char *ptr = strstr(temp, "\"new_t\":");
        if(ptr != NULL) {
            if(sscanf(ptr, "\"new_t\": \"%d\"", &new_t_int) == 1 || sscanf(ptr, "\"new_t\": %d", &new_t_int) == 1) {
                if(new_t_int >= 0 && new_t_int <= 2) {
                    alarm_threshold = new_t_int;
                    printf("[Attuatore] Nuova soglia ricevuta dal Python: %d\n", alarm_threshold);
                    
                    // --- LA SOLUZIONE: CONTROLLO DIRETTO DEI LED ---
                    if(alarm_threshold == 2) {
                        leds_on(LEDS_RED);
                        leds_off(LEDS_GREEN);
                        printf("[Attuatore] ALLARME MASSIMO! LED Rosso Acceso.\n");
                    } else {
                        leds_off(LEDS_RED);
                        leds_on(LEDS_GREEN);
                        printf("[Attuatore] Rischio rientrato. LED Verde.\n");
                    }
                    // -----------------------------------------------

                    coap_set_status_code(response, CHANGED_2_04);
                    return;
                }
            }
        }
    }
    coap_set_status_code(response, BAD_REQUEST_4_00);
}