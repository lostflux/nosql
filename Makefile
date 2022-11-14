# Minimal Makefile for testing.
#
# Author: Ke Lou, Amittai Siavava

all: test clean

.PHONY: test clean

test: app.py tests.in
	python3 app.py < tests.in 

clean:
	rm -rf __pycache__
