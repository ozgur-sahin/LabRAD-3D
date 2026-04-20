TARGET = QtScript.so
OFILES = sipQtScriptcmodule.o sipQtScriptQList0100QScriptValue.o sipQtScriptQList0100QScriptContextInfo.o sipQtScriptQScriptValueIterator.o sipQtScriptQScriptValuePropertyFlags.o sipQtScriptQScriptValueResolveFlags.o sipQtScriptQScriptValue.o sipQtScriptQScriptString.o sipQtScriptQScriptEngineAgent.o sipQtScriptQScriptSyntaxCheckResult.o sipQtScriptQScriptEngineQObjectWrapOptions.o sipQtScriptQScriptEngine.o sipQtScriptQScriptContextInfo.o sipQtScriptQScriptContext.o sipQtScriptQScriptClassPropertyIterator.o sipQtScriptQScriptClassQueryFlags.o sipQtScriptQScriptClass.o
HFILES = sipAPIQtScript.h 

CC = gcc
CXX = g++
LINK = g++
CPPFLAGS = -DNDEBUG -DSIP_PROTECTED_IS_PUBLIC -Dprotected=public -DQT_NO_DEBUG -DQT_SCRIPT_LIB -DQT_CORE_LIB -I. -I/usr/include/python2.7 -I/usr/mkspecs/linux-g++ -I/usr/include/qt4/QtScript -I/usr/include/qt4/QtCore -I/usr/include/qt4
CFLAGS = -m64 -pipe -fPIC -O2 -Wall -W -D_REENTRANT
CXXFLAGS = -m64 -pipe -fPIC -O2 -Wall -W -D_REENTRANT
LFLAGS = -shared  -Wl,-O1 -Wl,-rpath,/usr/lib/x86_64-linux-gnu -Wl,--version-script=QtScript.exp
LIBS = -L/usr/lib/x86_64-linux-gnu -lQtScript -lQtCore -lpthread
MOC = /usr/lib/x86_64-linux-gnu/qt4/bin/moc
.SUFFIXES: .c .o .cpp .cc .cxx .C


.cpp.o:
	$(CXX) -c $(CXXFLAGS) $(CPPFLAGS) -o $@ $<

.cc.o:
	$(CXX) -c $(CXXFLAGS) $(CPPFLAGS) -o $@ $<

.cxx.o:
	$(CXX) -c $(CXXFLAGS) $(CPPFLAGS) -o $@ $<

.C.o:
	$(CXX) -c $(CXXFLAGS) $(CPPFLAGS) -o $@ $<

.c.o:
	$(CC) -c $(CFLAGS) $(CPPFLAGS) -o $@ $<

all: $(TARGET)

$(OFILES): $(HFILES)

$(TARGET): $(OFILES)
	@echo '{ global: initQtScript; local: *; };' > QtScript.exp
	$(LINK) $(LFLAGS) -o $(TARGET) $(OFILES) $(LIBS)

install: $(TARGET)
	@test -d $(DESTDIR)/home/cct/.virtualenvs/labrad/lib/python2.7/site-packages/PyQt4 || mkdir -p $(DESTDIR)/home/cct/.virtualenvs/labrad/lib/python2.7/site-packages/PyQt4
	cp -f $(TARGET) $(DESTDIR)/home/cct/.virtualenvs/labrad/lib/python2.7/site-packages/PyQt4/$(TARGET)
	strip $(DESTDIR)/home/cct/.virtualenvs/labrad/lib/python2.7/site-packages/PyQt4/$(TARGET)
	@test -d $(DESTDIR)/home/cct/.virtualenvs/labrad/share/sip/PyQt4/QtScript || mkdir -p $(DESTDIR)/home/cct/.virtualenvs/labrad/share/sip/PyQt4/QtScript
	cp -f /home/cct/LabRAD/PyQt-x11-gpl-4.10.4/sip/QtScript/qscriptcontext.sip $(DESTDIR)/home/cct/.virtualenvs/labrad/share/sip/PyQt4/QtScript/qscriptcontext.sip
	cp -f /home/cct/LabRAD/PyQt-x11-gpl-4.10.4/sip/QtScript/qscriptengineagent.sip $(DESTDIR)/home/cct/.virtualenvs/labrad/share/sip/PyQt4/QtScript/qscriptengineagent.sip
	cp -f /home/cct/LabRAD/PyQt-x11-gpl-4.10.4/sip/QtScript/qscriptclasspropertyiterator.sip $(DESTDIR)/home/cct/.virtualenvs/labrad/share/sip/PyQt4/QtScript/qscriptclasspropertyiterator.sip
	cp -f /home/cct/LabRAD/PyQt-x11-gpl-4.10.4/sip/QtScript/QtScriptmod.sip $(DESTDIR)/home/cct/.virtualenvs/labrad/share/sip/PyQt4/QtScript/QtScriptmod.sip
	cp -f /home/cct/LabRAD/PyQt-x11-gpl-4.10.4/sip/QtScript/qscriptengine.sip $(DESTDIR)/home/cct/.virtualenvs/labrad/share/sip/PyQt4/QtScript/qscriptengine.sip
	cp -f /home/cct/LabRAD/PyQt-x11-gpl-4.10.4/sip/QtScript/qscriptclass.sip $(DESTDIR)/home/cct/.virtualenvs/labrad/share/sip/PyQt4/QtScript/qscriptclass.sip
	cp -f /home/cct/LabRAD/PyQt-x11-gpl-4.10.4/sip/QtScript/qscriptvalueiterator.sip $(DESTDIR)/home/cct/.virtualenvs/labrad/share/sip/PyQt4/QtScript/qscriptvalueiterator.sip
	cp -f /home/cct/LabRAD/PyQt-x11-gpl-4.10.4/sip/QtScript/qscriptvalue.sip $(DESTDIR)/home/cct/.virtualenvs/labrad/share/sip/PyQt4/QtScript/qscriptvalue.sip
	cp -f /home/cct/LabRAD/PyQt-x11-gpl-4.10.4/sip/QtScript/qscriptcontextinfo.sip $(DESTDIR)/home/cct/.virtualenvs/labrad/share/sip/PyQt4/QtScript/qscriptcontextinfo.sip
	cp -f /home/cct/LabRAD/PyQt-x11-gpl-4.10.4/sip/QtScript/qscriptstring.sip $(DESTDIR)/home/cct/.virtualenvs/labrad/share/sip/PyQt4/QtScript/qscriptstring.sip

clean:
	-rm -f $(TARGET)
	-rm -f sipQtScriptcmodule.o
	-rm -f sipQtScriptQList0100QScriptValue.o
	-rm -f sipQtScriptQList0100QScriptContextInfo.o
	-rm -f sipQtScriptQScriptValueIterator.o
	-rm -f sipQtScriptQScriptValuePropertyFlags.o
	-rm -f sipQtScriptQScriptValueResolveFlags.o
	-rm -f sipQtScriptQScriptValue.o
	-rm -f sipQtScriptQScriptString.o
	-rm -f sipQtScriptQScriptEngineAgent.o
	-rm -f sipQtScriptQScriptSyntaxCheckResult.o
	-rm -f sipQtScriptQScriptEngineQObjectWrapOptions.o
	-rm -f sipQtScriptQScriptEngine.o
	-rm -f sipQtScriptQScriptContextInfo.o
	-rm -f sipQtScriptQScriptContext.o
	-rm -f sipQtScriptQScriptClassPropertyIterator.o
	-rm -f sipQtScriptQScriptClassQueryFlags.o
	-rm -f sipQtScriptQScriptClass.o
	-rm -f QtScript.exp
