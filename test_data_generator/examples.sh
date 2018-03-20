#!/bin/bash

# generate 4 files with constant time periods between speech 5s and SNR 2dB
./generate.sh speech wav noise wav 4 5 2

# generate 6 files with time periods between speech generated from normal distribution and SNR 5dB
# ./generate.sh speech wav noise wav 6 rnorm 2 3 5

# generate 12 files with constant time periods between speech 7.5s and SNR -5dB
# ./generate.sh speech wav noise wav 12 7.5 -5
