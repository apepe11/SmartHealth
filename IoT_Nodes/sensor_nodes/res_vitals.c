#include "contiki.h"
#include "coap-engine.h"
#include <stdio.h>
#include "vitals_classifier.h"

static void res_get_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset);

RESOURCE(res_vitals,
         "title=\"Patient Vitals\";rt=\"Health\"",
         res_get_handler,
         NULL,
         NULL,
         NULL);

static void res_get_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset) {
    
    // Valori statici di base (Paziente sano)
    int hr = 75;
    int spo2 = 98;
    int body_temperature = 36;

    // Trucco per i test: usiamo una variabile statica per contare le richieste.
    static int request_counter = 0;
    request_counter++;
    
    if(request_counter % 5 == 0) {
        hr = 120;                  // Tachicardia
        spo2 = 88;                 // Ipossia
        body_temperature = 39;     // Febbre
    }

    int16_t features[3] = {hr, body_temperature, spo2};
    
    // Predizione: usiamo _predict invece di _predict_proba per ottenere direttamente la CLASSE (0, 1, 2)
    int predicted_class = vitals_rf_model_predict(features, 3);

    // Formattiamo il JSON passando direttamente l'intero della classe
    int length = snprintf((char *)buffer, preferred_size, 
        "{\"hr\": %d, \"body_temperature\": %d, \"spo2\": %d, \"risk\": %d}", 
        hr, body_temperature, spo2, predicted_class);
        
    coap_set_header_content_format(response, APPLICATION_JSON);
    coap_set_payload(response, buffer, length);
}