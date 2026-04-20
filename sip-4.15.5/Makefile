
all:
	@(cd sipgen; $(MAKE))
	@(cd siplib; $(MAKE))

install:
	@(cd sipgen; $(MAKE) install)
	@(cd siplib; $(MAKE) install)
	@test -d $(DESTDIR)/home/cct/.virtualenvs/labrad/lib/python2.7/site-packages || mkdir -p $(DESTDIR)/home/cct/.virtualenvs/labrad/lib/python2.7/site-packages
	cp -f sipconfig.py $(DESTDIR)/home/cct/.virtualenvs/labrad/lib/python2.7/site-packages/sipconfig.py
	cp -f /home/cct/LabRAD/sip-4.15.5/sipdistutils.py $(DESTDIR)/home/cct/.virtualenvs/labrad/lib/python2.7/site-packages/sipdistutils.py

clean:
	@(cd sipgen; $(MAKE) clean)
	@(cd siplib; $(MAKE) clean)
