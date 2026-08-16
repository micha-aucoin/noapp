#!/usr/bin/env bash

python3 -m unittest discover \
	--start-directory tests \
	--pattern "test_*.py" \
	--verbose \
	--failfast

