# Minimal Makefile for testing.
#
# Author: Ke Lou, Amittai Siavava

all: test clean

.PHONY: test clean

test: app.py tests.txt
	python3 app.py < tests.txt

clean:
	rm -rf __pycache__
