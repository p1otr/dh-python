#!/usr/bin/make -f

clean:
	rm -rf cache
	#rm -f dist_fallback
	rm -f README.PyDist.html

dist_fallback:
	python3 ./generate_fallback_list.py --skip-sensible-names

README.PyDist.html: README.PyDist
	rst2html $< $@

.PHONY: clean
