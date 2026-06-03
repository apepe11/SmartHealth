#ifndef PROJECT_CONF_H_
#define PROJECT_CONF_H_

#define NETSTACK_CONF_WITH_IPV6 1
#define COAP_MAX_CHUNK_SIZE            64
#define COAP_MAX_TRANSACTIONS          4

/* Importante per il Solo Project: rimuoviamo gli observees inutilizzati */
#define COAP_MAX_OBSERVEES             0

/* Configurazione Radio: impostala IDENTICA a quella del tuo Border Router fisico */
#define IEEE802154_CONF_DEFAULT_CHANNEL 26     // Tuo canale di rete (11-26)
#define IEEE802154_CONF_PANID           0xABCD   // Tuo PAN ID reale

/* Abilita la stampa dei log seriali tramite la porta USB del dongle */
#define NRF52840_CONF_USB_CDC_LOG       1

#endif /* PROJECT_CONF_H_ */