#!/bin/bash
dir=pwd
parentdir="$(dirname "$dir")"
flake8 $parentdir/test/*.py $parentdir/src/florence/*.py
