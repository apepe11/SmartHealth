# 1. Nome dell'eseguibile principale per il sensore (compilerà 'sensor.c')
CONTIKI_PROJECT = sensor
all: $(CONTIKI_PROJECT)

# 2. File sorgenti aggiuntivi che compongono il sensore (le risore CoAP separate)
PROJECT_SOURCEFILES += res_vitals.c res_sampling.c

# 3. Configurazione dello stack di rete IPv6 e Routing RPL per Contiki-NG
MAKE_MAC = MAKE_MAC_CSMA
MAKE_NET = MAKE_NET_IPV6
MAKE_ROUTING = MAKE_ROUTING_RPL_LITE

# 4. Inclusione obbligatoria del modulo CoAP (Erbium) nativo di Contiki-NG
MODULES += os/net/app-layer/coap

# 5. Specifica del file di configurazione locale del progetto
CFLAGS += -DPROJECT_CONF_H=\"project-configuration.h\"
CFLAGS += -Wno-error=discarded-qualifiers

# --------------------------------------------------------------------
# 6. Percorso assoluto di Contiki-NG sul tuo sistema Arch Linux
# --------------------------------------------------------------------
CONTIKI = /home/antoniio/Scrivania/contiki-ng

include $(CONTIKI)/Makefile.include