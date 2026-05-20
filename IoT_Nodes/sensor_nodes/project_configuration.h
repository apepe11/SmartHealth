#ifndef PROJECT_CONF_H_
#define PROJECT_CONF_H_

/* Abilita lo stack IPv6 e il modulo di routing */
#define NETSTACK_CONF_WITH_IPV6 1

// =================================================================
// FIX 1: ABILITARE ESPLICITAMENTE RPL
// =================================================================
/* Forza l'uso di RPL-Lite (lo standard in Contiki-NG) */
#define ROUTING_CONF_RPL_LITE           1

/* Forza l'uso dello stack di rete standard con routing */
#define NETSTACK_CONF_ROUTING           rpl_lite_driver

// =================================================================
// FIX 2: DIMENSIONE BUFFER COAP E IPV6
// =================================================================
/* ATTENZIONE: 64 byte sono troppo pochi! Lo stack IPv6 di Contiki ha bisogno 
   di buffer più grandi per gestire gli header IPv6 + UDP + CoAP + Opzioni RPL.
   Se scendi sotto i 128/256 byte, i pacchetti grandi vengono scartati silenziosamente. */
#define COAP_MAX_CHUNK_SIZE            256

/* Numero massimo di transazioni CoAP contemporanee gestibili dal sensore */
#define COAP_MAX_TRANSACTIONS          4

#endif /* PROJECT_CONF_H_ */