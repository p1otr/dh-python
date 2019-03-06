#!/usr/bin/make -f

# hardcode default/supported Python versions to make tests more reliable
# Note that all these packages have to be installed during tests
export DEBPYTHON_DEFAULT=2.7
export DEBPYTHON_SUPPORTED=2.7
export DEBPYTHON3_DEFAULT=3.7
export DEBPYTHON3_SUPPORTED=3.5,3.7

# enable or disable tests here:
TESTS := test101 test201 test202 test203 test204 test205 test206 test207 test301 test302 test303 test304

all: $(TESTS)

test%:
	make -C t$* run
	make -C t$* check

clean-test%:
	make -C t$* clean

clean: $(TESTS:%=clean-%)
	rm -f *\.dsc *\.tar\.gz *\.build *\.changes *\.deb *\.buildinfo
	@find . -prune -name '*.egg-info' -exec rm -rf '{}' ';' || true

.PHONY: clean
