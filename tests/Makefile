#!/usr/bin/make -f

# enable or disable tests here:
#TESTS := test101 test201 test202 test203 test204 test205 test206 test207 test301 test302 test303 test304 test305 test306 testpb01 testpb02 testpb03 testpb04 testpb05
TESTS := test101 test301 test302 test303 test304 test305 test306

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
