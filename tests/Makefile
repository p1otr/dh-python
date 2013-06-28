#!/usr/bin/make -f

# enable or disable tests here:
TESTS := test201 test202 test203 test204 test205 test206 test207 test301 test302 test303 test304

all: $(TESTS)

test%:
	make -C t$* run
	make -C t$* check

clean-test%:
	make -C t$* clean

clean: $(TESTS:%=clean-%)
	rm -f *\.dsc *\.tar\.gz *\.build *\.changes *\.deb
	@find . -prune -name '*.egg-info' -exec rm -rf '{}' ';' || true

.PHONY: clean
