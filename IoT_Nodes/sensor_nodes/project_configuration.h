#ifndef PROJECT_CONF_H_
#define PROJECT_CONF_H_

/* Abilita lo stack IPv6 */
#define NETSTACK_CONF_WITH_IPV6 1

/* Dimensione massima del buffer per i messaggi CoAP (64 byte bastano per il nostro JSON statico) */
#define COAP_MAX_CHUNK_SIZE            64

/* Numero massimo di transazioni CoAP contemporanee gestibili dal sensore */
#define COAP_MAX_TRANSACTIONS          4

#endif /* PROJECT_CONF_H_ */