#ifndef PROJECT_CONF_H_
#define PROJECT_CONF_H_

#define NETSTACK_CONF_WITH_IPV6 1

#define ROUTING_CONF_RPL_LITE           1

#define NETSTACK_CONF_ROUTING           rpl_lite_driver
#define COAP_MAX_CHUNK_SIZE            256
#define COAP_MAX_TRANSACTIONS          4

#endif 