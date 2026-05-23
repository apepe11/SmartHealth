#include "contiki.h"
#include "coap-engine.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

extern uint16_t current_sampling_rate;

//modifica rate del sensore 
static void res_put_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset);


//risorsa per modificare il rate 
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
        char temp[64];
        
        if(len >= sizeof(temp)) {
            len = sizeof(temp) - 1;
        }
        
        memcpy(temp, payload, len);
        temp[len] = '\0';
        
        char *ptr = strstr(temp, "\"new_sr\":");
        if(ptr != NULL) {
            if(sscanf(ptr, "\"new_sr\": %d", &new_rate) == 1 || sscanf(ptr, "\"new_sr\": \"%d\"", &new_rate) == 1) {
                if(new_rate > 0) {
                    //aggiorno rate
                    current_sampling_rate = new_rate;
                    
                    printf("Nuovo Sampling Rate: %d sec\n", current_sampling_rate);
                    
                    coap_set_status_code(response, CHANGED_2_04);
                    return;
                }
            }
        }
    }
    coap_set_status_code(response, BAD_REQUEST_4_00);
}