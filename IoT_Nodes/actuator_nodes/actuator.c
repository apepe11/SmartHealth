#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "contiki.h"
#include "coap-engine.h"
#include "dev/leds.h"
#include "sys/log.h"
#include "net/routing/routing.h"

#define LOG_MODULE "SmartHealth-Actuator"
#define LOG_LEVEL LOG_LEVEL_INFO

extern coap_resource_t res_threshold;

// threshold corrente comandata dalla Cloud Application
int alarm_threshold = 1;

PROCESS(actuator_node, "Smart Health Actuator Node");
AUTOSTART_PROCESSES(&actuator_node);

// funzione per aggiornamento LED
void update_leds(void)
{
    leds_off(LEDS_ALL);

    if(alarm_threshold == 0) {
        leds_on(LEDS_GREEN);
        printf("[LED] GREEN (threshold = 0) - Stato Normale\n");
    }
    else if(alarm_threshold == 1) {
        leds_on(LEDS_RED | LEDS_GREEN);
        printf("[LED] EMULATED YELLOW (threshold = 1) - Stato di Attenzione\n");
    }
    else if(alarm_threshold == 2) {
        leds_on(LEDS_RED);
        printf("[LED] RED (threshold = 2) - Stato di Allarme\n");
    }
    else {
        leds_off(LEDS_ALL);
        printf("[LED] OFF (invalid threshold)\n");
    }
}

PROCESS_THREAD(actuator_node, ev, data)
{
    static struct etimer rpl_timer;

    PROCESS_BEGIN();
    LOG_INFO("Avvio Nodo Attuatore Fisico...\n");

    // attivo risorsa
    coap_activate_resource(&res_threshold, "threshold");
    LOG_INFO("Risorsa /threshold attivata come CoAP Server.\n");

    // inizializzo LED 
    leds_off(LEDS_ALL);
    leds_on(LEDS_GREEN);

    etimer_set(&rpl_timer, CLOCK_SECOND * 5);


    while(!NETSTACK_ROUTING.node_is_reachable()) {
        LOG_INFO("Attendo prefisso IPv6 dal Border Router...\n");
        PROCESS_WAIT_EVENT_UNTIL(ev == PROCESS_EVENT_TIMER && data == &rpl_timer);
        etimer_reset(&rpl_timer);
    }

    LOG_INFO("Rete RPL connessa.\n");
    update_leds();

    while(1) {
        PROCESS_YIELD();
    }

    PROCESS_END();
}