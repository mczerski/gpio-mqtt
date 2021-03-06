PREFIX ?= /usr/local
INITDIR_SYSTEMD = /etc/systemd/system
BINDIR = $(PREFIX)/bin

RM = rm
INSTALL = install -p
INSTALL_PROGRAM = $(INSTALL) -m755
INSTALL_SCRIPT = $(INSTALL) -m755
INSTALL_DATA = $(INSTALL) -m644
INSTALL_DIR = $(INSTALL) -d

Q = @

help:
	$(Q)echo "install - install scripts"
	$(Q)echo "uninstall - uninstall scripts"

install:
	$(Q)echo -e '\033[1;32mInstalling main scripts...\033[0m'
	$(INSTALL_DIR) "$(BINDIR)"
	$(INSTALL_PROGRAM) gpio-mqtt.py "$(BINDIR)/gpio-mqtt"
	$(INSTALL_DATA) gpio-mqtt.service "$(INITDIR_SYSTEMD)/gpio-mqtt.service"

uninstall:
	$(RM) "$(BINDIR)/gpio-mqtt
	$(RM) "$(INITDIR_SYSTEMD)/gpio-mqtt.service

.PHONY: install uninstall

