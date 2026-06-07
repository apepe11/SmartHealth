CONTIKI_PROJECT = sensor
all: $(CONTIKI_PROJECT)


PROJECT_SOURCEFILES += res_vitals.c res_sampling.c


MAKE_MAC = MAKE_MAC_CSMA
MAKE_NET = MAKE_NET_IPV6
MAKE_ROUTING = MAKE_ROUTING_RPL_LITE


MODULES += os/net/app-layer/coap


CFLAGS += -DPROJECT_CONF_H=\"project-configuration.h\"
CFLAGS += -Wno-error=discarded-qualifiers


CONTIKI = /home/antonio/contiki-ng

include $(CONTIKI)/Makefile.include