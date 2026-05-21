#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "contiki.h"
#include "coap-engine.h"
#include "coap-blocking-api.h"
#include "coap-observe-client.h"
#include "dev/leds.h"
#include "sys/log.h"
#include "net/routing/routing.h"

#define LOG_MODULE "SmartHealth-Actuator"
#define LOG_LEVEL LOG_LEVEL_INFO

#define SENSOR_EP "coap://[fd00::f6ce:36b9:a760:ecea]:5683"
#define OBSERVE_URI "vitals"

extern coap_resource_t res_threshold;

// Threshold corrente
int alarm_threshold = 1;

// Ultimo rischio ricevuto
int current_risk = 0;

static coap_endpoint_t server_ep;
static coap_observee_t *obs_session = NULL;

PROCESS(actuator_node, "Smart Health Actuator Node");
AUTOSTART_PROCESSES(&actuator_node);

/*---------------------------------------------------------------------------*/
// Funzione centrale aggiornamento LED
/*---------------------------------------------------------------------------*/
void update_leds(void)
{
    leds_off(LEDS_ALL);

    if(alarm_threshold == 0) {

        leds_on(LEDS_GREEN);
        printf("[LED] GREEN (threshold = 0)\n");
    }
    else if(alarm_threshold == 1) {

        leds_on(LEDS_YELLOW);
        printf("[LED] YELLOW (threshold = 1)\n");
    }
    else if(alarm_threshold == 2) {

        leds_on(LEDS_RED);
        printf("[LED] RED (threshold = 2)\n");
    }
    else {

        leds_off(LEDS_ALL);
        printf("[LED] OFF (invalid threshold)\n");
    }
}

/*---------------------------------------------------------------------------*/
// Callback Observe
/*---------------------------------------------------------------------------*/
static void
notification_callback(coap_observee_t *obs,
                      void *notification,
                      coap_notification_flag_t flag)
{
    int len = 0;

    const uint8_t *payload = NULL;

    if(notification != NULL) {
        len = coap_get_payload(notification, &payload);
    }

    if(len > 0) {

        char data[128];

        memcpy(data, payload, len);

        data[len] = '\0';

        LOG_INFO("Dati ricevuti: %s\n", data);

        char *ptr = strstr(data, "\"risk\":");

        if(ptr != NULL) {

            current_risk = atoi(ptr + 7);

            LOG_INFO("Nuovo risk=%d\n", current_risk);

            // Aggiorna subito LED
            update_leds();
        }
    }
}

/*---------------------------------------------------------------------------*/
// Processo principale
/*---------------------------------------------------------------------------*/
PROCESS_THREAD(actuator_node, ev, data)
{
    static struct etimer rpl_timer;

    PROCESS_BEGIN();

    LOG_INFO("Avvio Nodo Attuatore...\n");

    coap_activate_resource(&res_threshold, "threshold");

    LOG_INFO("Risorsa /threshold attivata.\n");

    // Stato iniziale
    leds_off(LEDS_ALL);

    leds_single_on(LEDS_GREEN);

    etimer_set(&rpl_timer, CLOCK_SECOND * 5);

    while(!NETSTACK_ROUTING.node_is_reachable()) {

        LOG_INFO("Attesa rete RPL...\n");

        PROCESS_WAIT_EVENT_UNTIL(ev == PROCESS_EVENT_TIMER &&
                                 data == &rpl_timer);

        etimer_reset(&rpl_timer);
    }

    LOG_INFO("Rete RPL connessa!\n");

    if(coap_endpoint_parse(SENSOR_EP,
                           strlen(SENSOR_EP),
                           &server_ep) == 0) {

        LOG_ERR("Errore parsing endpoint!\n");

        PROCESS_EXIT();
    }

    LOG_INFO("Observe -> %s/%s\n",
             SENSOR_EP,
             OBSERVE_URI);

    obs_session =
        coap_obs_request_registration(&server_ep,
                                      OBSERVE_URI,
                                      notification_callback,
                                      NULL);

    if(obs_session == NULL) {

        LOG_ERR("Observe fallita!\n");

    } else {

        LOG_INFO("Observe avviata!\n");
    }

    while(1) {
        PROCESS_YIELD();
    }

    PROCESS_END();
}