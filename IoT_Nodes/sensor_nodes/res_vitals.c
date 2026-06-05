#include "contiki.h"
#include "coap-engine.h"
#include <stdio.h>


extern int current_hr;
extern int current_spo2;
extern int current_temp;
extern int current_risk;



static void res_get_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset);

// risorsa per i dati del paziente
EVENT_RESOURCE(res_vitals,
         "title=\"Patient Vitals\";rt=\"Health\";obs",
         res_get_handler,
         NULL,
         NULL,
         NULL,
         NULL);


//funziona per ottenere i paramentri del paziente 
static void res_get_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset) {
    
    //crea payload in formanto JSON con i parametri 
    int length = snprintf((char *)buffer, preferred_size, 
        "{\"hr\": %d, \"body_temperature\": %d, \"spo2\": %d, \"risk\": %d}", 
        current_hr, current_temp, current_spo2, current_risk);
        
    coap_set_header_content_format(response, APPLICATION_JSON);
    coap_set_payload(response, buffer, length);
}