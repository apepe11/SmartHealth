#ifndef PROJECT_CONF_H_
#define PROJECT_CONF_H_

#define NETSTACK_CONF_WITH_IPV6 1
#define COAP_MAX_CHUNK_SIZE            64

#define COAP_MAX_TRANSACTIONS          8
#define COAP_MAX_CLIENT_RESPONSES      4

#define COAP_MAX_OBSERVEES             1

#define IEEE802154_CONF_DEFAULT_CHANNEL 26     
#define IEEE802154_CONF_PANID           0xABCD   

#define NRF52840_CONF_USB_CDC_LOG       1

#endif