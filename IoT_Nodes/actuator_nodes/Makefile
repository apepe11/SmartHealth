CONTIKI_PROJECT = actuator
all: $(CONTIKI_PROJECT)

TARGET = nrf52840
BOARD = dongle

MAKE_MAC = MAKE_MAC_CSMA
MAKE_NET = MAKE_NET_IPV6
MAKE_ROUTING = MAKE_ROUTING_RPL_LITE

MODULES += os/net/app-layer/coap

CFLAGS += -DCOAP_OBSERVE_CLIENT=1

CFLAGS += -DPROJECT_CONF_H=\"project_configuration.h\"
CFLAGS += -Wno-error=discarded-qualifiers
CFLAGS += -Wno-error=implicit-function-declaration
CFLAGS += -Wno-error=unused-but-set-variable

CONTIKI = /home/antonio/contiki-ng
include $(CONTIKI)/Makefile.include