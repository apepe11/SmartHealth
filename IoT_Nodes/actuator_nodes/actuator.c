// actuator.c

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "contiki.h"
#include "coap-engine.h"
#include "coap-observe-client.h"
#include "dev/leds.h"
#include "sys/log.h"
#include "net/routing/routing.h"
#include "net/ipv6/uip-ds6.h"

#define LOG_MODULE "SmartHealth-Actuator"
#define LOG_LEVEL LOG_LEVEL_INFO

#define SENSOR_IP "fd00::f6ce:36b9:a760:ecea"


int alarm_threshold = 0;
int current_risk = 0;
static coap_observee_t *vitals_observation = NULL;


#include "res_threshold.c"

PROCESS(actuator_node, "Smart Health Actuator Node");
AUTOSTART_PROCESSES(&actuator_node);

void update_leds_by_threshold(int risk)
{
    current_risk = risk;
    leds_off(LEDS_ALL);
    
    if(risk == 0) {
        leds_on(LEDS_GREEN);
        LOG_INFO("VERDE - Rischio %d (Normale) | Soglia attiva: %d\n", risk, alarm_threshold);
    }
    else if(risk == 1) {
        leds_on(LEDS_BLUE);
        LOG_INFO("BLU - Rischio %d (Attenzione) | Soglia attiva: %d\n", risk, alarm_threshold);
    }
    else if(risk >= 2) {
        leds_on(LEDS_RED);
        LOG_INFO("ROSSO - Rischio %d (ALLARME EMERGENZA!) | Soglia attiva: %d\n", risk, alarm_threshold);
    }
}


static void vitals_notification_handler(coap_observee_t *obs,
                                        void *notification,
                                        coap_notification_flag_t flag)
{
    const uint8_t *payload;
    int len;
    int hr, temp, spo2, risk;

    if(notification == NULL) {
        printf("Timeout o errore nell'observe\n");
        return;
    }

    len = coap_get_payload(notification, &payload);

    if(len > 0) {
        char buffer[128];
        memcpy(buffer, payload, len);
        buffer[len] = '\0';

        if(sscanf(buffer,
                  "{\"hr\": %d, \"body_temperature\": %d, \"spo2\": %d, \"risk\": %d}",
                  &hr, &temp, &spo2, &risk) == 4) {

            printf("NOTIFICA RICEVUTA DAL SENSORE:\n");
            printf("   HR=%d bpm | Temp=%d C | SpO2=%d%% | Rischio=%d\n",
                   hr, temp, spo2, risk);

            // Aggiorna lo stato dei LED
            update_leds_by_threshold(risk);
        } else {
            LOG_WARN("Errore nel parsing del payload ricevuto: %s\n", buffer);
        }
    }
}

PROCESS_THREAD(actuator_node, ev, data)
{
    static struct etimer rpl_timer;

    PROCESS_BEGIN();
    LOG_INFO("Avvio Attuatore...\n");

    leds_off(LEDS_ALL);
    leds_on(LEDS_GREEN);

    etimer_set(&rpl_timer, CLOCK_SECOND * 5);

    while(!NETSTACK_ROUTING.node_is_reachable()) {
        LOG_INFO("Attendo prefisso IPv6 dal Border Router...\n");
        PROCESS_WAIT_EVENT_UNTIL(ev == PROCESS_EVENT_TIMER && data == &rpl_timer);
        etimer_reset(&rpl_timer);
    }

    LOG_INFO("Rete RPL connessa.\n");
    
    printf("IP Locale: ");
    LOG_INFO_6ADDR(&uip_ds6_get_global(0)->ipaddr); 
    printf("\n");
    
    
    threshold_resource_init();
    
    alarm_threshold = 0;
    update_leds_by_threshold(0);

    static coap_endpoint_t sensor_ep;
    coap_endpoint_parse(SENSOR_IP, strlen(SENSOR_IP), &sensor_ep);
    sensor_ep.port = UIP_HTONS(COAP_DEFAULT_PORT);

    printf("Avvio CoAP Client \n");
    
    vitals_observation = coap_obs_request_registration(&sensor_ep, "vitals", 
                                                       vitals_notification_handler, NULL);

    if(vitals_observation == NULL) {
        printf("ERRORE: impossibile osservare il sensore!\n");
    } else {
        printf("Observe registrato! In attesa di notifiche dal sensore...\n");
    }

    while(1) {
        PROCESS_WAIT_EVENT();
    }

    PROCESS_END();
}