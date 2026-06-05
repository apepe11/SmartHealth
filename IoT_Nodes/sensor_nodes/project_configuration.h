#ifndef PROJECT_CONF_H_
#define PROJECT_CONF_H_

/* Abilita lo stack IPv6 e il modulo di routing */
#define NETSTACK_CONF_WITH_IPV6 1


/* Forza l'uso di RPL-Lite (lo standard in Contiki-NG) */
#define ROUTING_CONF_RPL_LITE           1

/* Forza l'uso dello stack di rete standard con routing */
#define NETSTACK_CONF_ROUTING           rpl_lite_driver
#define COAP_MAX_CHUNK_SIZE            256
#define COAP_MAX_TRANSACTIONS          4

#endif 