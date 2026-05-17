#include "contiki.h"
#include "coap-engine.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

extern uint16_t current_sampling_rate; // Variabile globale definita nel main

static void res_put_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset);

RESOURCE(res_sampling,
         "title=\"Sampling Rate\";rt=\"Control\"",
         NULL,
         NULL,
         res_put_handler,
         NULL);

static void res_put_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset) {
    const uint8_t *payload = NULL;
    int len = coap_get_payload(request, &payload);
    
    if(len > 0) {
        // Estrazione brutale del valore JSON {"new_sr": X}
        // Nota: In produzione si userebbe una libreria JSON, ma per simulazione va bene
        char temp[32];
        memcpy(temp, payload, len);
        temp[len] = '\0';
        
        char *ptr = strstr(temp, "\"new_sr\":");
        if(ptr != NULL) {
            int new_rate = atoi(ptr + 9);
            if(new_rate > 0) {
                current_sampling_rate = new_rate;
                coap_set_status_code(response, CHANGED_2_04);
                return;
            }
        }
    }
    coap_set_status_code(response, BAD_REQUEST_4_00);
}