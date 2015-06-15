#!/bin/bash
dir="$(dirname "$pwd")"
flake8 $dir/test/*.py $dir/src/florence/*.py $dir/script/*.py
