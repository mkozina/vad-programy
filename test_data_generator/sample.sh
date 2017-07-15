#!/bin/bash

# generuje 4 pliki z przerwami w mowie 5s i SNR 2dB
./generate.sh speech wav noise wav 4 5 2

# generuje 6 plikow z przerwami w mowie wygenerowanymi zgodnie z rozkladem normalnym i SNR 5dB
# ./generate.sh speech wav noise wav 6 rnorm 2 3 5

# generuje 12 plikow z przerwami w mowie 7.5s i SNR -5dB
# ./generate.sh speech wav noise wav 12 7.5 -5
