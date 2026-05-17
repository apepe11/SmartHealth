CONTIKI_PROJECT = actuator
all: $(CONTIKI_PROJECT)

PROJECT_SOURCEFILES += res_treshold.c

MAKE_MAC = MAKE_MAC_CSMA
MAKE_NET = MAKE_NET_IPV6
MAKE_ROUTING = MAKE_ROUTING_RPL_CLASSIC

MODULES += os/net/app-layer/coap
CFLAGS += -DPROJECT_CONF_H=\"project_configuration.h\"
CFLAGS += -Wno-error=discarded-qualifiers
CFLAGS += -Wno-error=implicit-function-declaration
CFLAGS += -Wno-error=unused-but-set-variable

# Fondamentale per l'attuatore: abilita la funzionalità Client e Observe
CFLAGS += -DCOAP_OBSERVE_CLIENT=1

CONTIKI = /home/antoniio/Scrivania/contiki-ng
include $(CONTIKI)/Makefile.include