#include "contiki.h"
#include "coap-engine.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

extern uint16_t current_sampling_rate;

static void res_put_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset);

RESOURCE(res_sampling,
         "title=\"Sampling Rate\";rt=\"Control\"",
         NULL,
         NULL,
         res_put_handler,
         NULL);

static void res_put_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset) {
    const uint8_t *payload = NULL;
    int new_rate;
    int len = coap_get_payload(request, &payload);
    
    if(len > 0) {
        char temp[64]; // Aumentato leggermente per sicurezza
        
        // Protezione da Buffer Overflow (fondamentale nei microcontrollori!)
        if(len >= sizeof(temp)) {
            len = sizeof(temp) - 1;
        }
        
        memcpy(temp, payload, len);
        temp[len] = '\0';
        
        // Estrazione sicura e flessibile del valore JSON {"new_sr": X}
        char *ptr = strstr(temp, "\"new_sr\":");
        if(ptr != NULL) {
            // sscanf è immune agli spazi extra e legge il numero in modo intelligente
            if(sscanf(ptr, "\"new_sr\": %d", &new_rate) == 1 || sscanf(ptr, "\"new_sr\": \"%d\"", &new_rate) == 1) {
                if(new_rate > 0) {
                    current_sampling_rate = new_rate;
                    
                    printf("[Sensore] Comando Cloud ricevuto! Nuovo Sampling Rate: %d sec\n", current_sampling_rate);
                    
                    coap_set_status_code(response, CHANGED_2_04);
                    return;
                }
            }
        }
    }
    coap_set_status_code(response, BAD_REQUEST_4_00);
}