#!/usr/bin/make -f

FALLBACK_FLAGS = $(shell dpkg-vendor --is ubuntu && echo '--ubuntu')

clean:
	rm -rf cache
	#rm -f dist_fallback
	rm -f README.PyDist.html

dist_fallback:
	python3 ./generate_fallback_list.py $(FALLBACK_FLAGS)

README.PyDist.html: README.PyDist
	rst2html $< $@

.PHONY: clean
