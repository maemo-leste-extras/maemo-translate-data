all:
	/bin/true

install:
	install -d $(DESTDIR)/usr/share/kotki/
	cp -a model/* $(DESTDIR)/usr/share/kotki/
