#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>

#include "contiki.h"
#include "coap-engine.h"
#include "dev/leds.h"

/* GLOBALI */
extern int alarm_threshold;
extern int current_risk;

/* FUNZIONE ESTERNA */
extern void update_leds(void);

/* PROTOTIPI */
static void threshold_get_handler(coap_message_t *request,
                                  coap_message_t *response,
                                  uint8_t *buffer,
                                  uint16_t preferred_size,
                                  int32_t *offset);

static void threshold_put_handler(coap_message_t *request,
                                  coap_message_t *response,
                                  uint8_t *buffer,
                                  uint16_t preferred_size,
                                  int32_t *offset);

/*---------------------------------------------------------------------------*/
RESOURCE(res_threshold,
         "title=\"Alarm Threshold\";rt=\"Control\"",
         threshold_get_handler,
         NULL,
         threshold_put_handler,
         NULL);

/*---------------------------------------------------------------------------*/
// GET
/*---------------------------------------------------------------------------*/
static void
threshold_get_handler(coap_message_t *request,
                      coap_message_t *response,
                      uint8_t *buffer,
                      uint16_t preferred_size,
                      int32_t *offset)
{
    char payload[64];

    snprintf(payload,
             sizeof(payload),
             "{\"threshold\": %d}",
             alarm_threshold);

    coap_set_header_content_format(response, APPLICATION_JSON);
    coap_set_payload(response,
                     (uint8_t *)payload,
                     strlen(payload));
}

/*---------------------------------------------------------------------------*/
// PUT
/*---------------------------------------------------------------------------*/
static void
threshold_put_handler(coap_message_t *request,
                      coap_message_t *response,
                      uint8_t *buffer,
                      uint16_t preferred_size,
                      int32_t *offset)
{
    const uint8_t *payload;
    int len;
    int new_t_int;

    len = coap_get_payload(request, &payload);

    if(len > 0) {

        char temp[32];

        if(len >= (int)sizeof(temp)) {
            coap_set_status_code(response, BAD_REQUEST_4_00);
            return;
        }

        memcpy(temp, payload, len);
        temp[len] = '\0';

        printf("[DEBUG] Payload RAW: %s\n", temp);

        char *ptr = strstr(temp, "\"new_t\":");

        if(ptr != NULL) {

            if(sscanf(ptr, "\"new_t\": \"%d\"", &new_t_int) == 1 ||
               sscanf(ptr, "\"new_t\": %d", &new_t_int) == 1) {

                if(new_t_int >= 0 && new_t_int <= 2) {

                    alarm_threshold = new_t_int;

                    printf("[Attuatore] Nuova threshold=%d\n",
                           alarm_threshold);

                    update_leds();

                    coap_set_status_code(response, CHANGED_2_04);
                    return;
                }
            }
        }
    }

    coap_set_status_code(response, BAD_REQUEST_4_00);
}