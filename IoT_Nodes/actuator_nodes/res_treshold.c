#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>

#include "contiki.h"
#include "coap-engine.h"
#include "dev/leds.h"


extern int alarm_threshold;
extern int current_risk;
extern void update_leds(void);


//definizione risorse 
//legge valore corrente soglia 
static void threshold_get_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset);
//modifica valore soglia 
static void threshold_put_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset);

//creo macro per risorsa soglia 
RESOURCE(res_threshold,
         "title=\"Alarm Threshold\";rt=\"Control\"",
         threshold_get_handler,
         NULL,
         threshold_put_handler,
         NULL);

// restituisce valore attuale soglia in JSON
static void threshold_get_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset){
    char payload[64];

    snprintf(payload, sizeof(payload), "{\"threshold\": %d}", alarm_threshold);

    coap_set_header_content_format(response, APPLICATION_JSON);
    coap_set_payload(response, (uint8_t *)payload, strlen(payload));
}

// modifico valore soglia 
static void threshold_put_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset){
    const uint8_t *payload;
    int len;
    int new_t_int;

    len = coap_get_payload(request, &payload); //prendo il paylaod 

    if(len > 0) {

        char temp[32];
        if(len >= (int)sizeof(temp)) {
            coap_set_status_code(response, BAD_REQUEST_4_00);
            return;
        }

        memcpy(temp, payload, len);
        temp[len] = '\0';

        char *ptr = strstr(temp, "\"new_t\":");

        if(ptr != NULL) {

            if(sscanf(ptr, "\"new_t\": \"%d\"", &new_t_int) == 1 ||
               sscanf(ptr, "\"new_t\": %d", &new_t_int) == 1) {

                if(new_t_int >= 0 && new_t_int <= 2) {

                    //aggiorno soglia con nuovo valore 
                    alarm_threshold = new_t_int;

                    printf("Nuova threshold=%d\n", alarm_threshold);
                    //aggirono LED
                    update_leds();
                    //notifico che è avvenuto il cambiamento
                    coap_set_status_code(response, CHANGED_2_04);
                    return;
                }
            }
        }
    }
    coap_set_status_code(response, BAD_REQUEST_4_00);
}