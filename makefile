SCRIPT=runner.py
BIN=/usr/bin/
REMOTE=$(BIN)$(SCRIPT)

install: $(SCRIPT)
	cp $(SCRIPT) $(REMOTE)

uninstall:
	rm -vf $(REMOTE)
	
.PHONY: install uninstall
