Voice Activity Detection
========================

Test Data Generator
-------------------

Requirements:
* Python 3.5.2
* R 3.4.4
* rpy2 2.9.2

Run `generate.sh` in `test_data_generator/`

Parameters:
1. Folder with speech files and alignments
2. Filename extension of speech files
3. Folder with noise files
4. Filename extension of noise files
5. Number of files to generate
6. Time periods between speech:
    * Constant: `x`
    * Generated from distribution: `rbeta|rgamma|rnorm|runif x y`
7. SNR in dB

Example commands with descriptions in `test_data_generator/examples.sh`

Geometrically Adaptive Energy Threshold Method
----------------------------------------------

Requirements:
* Python 3.5.2
* NumPy 1.13.1
* SciPy 0.19.1
* Matplotlib 2.0.2

Run `python3 gaet.py audiofile.wav` in `vads/gaet/`

To see plot of MAPD and GAET of specific analysis block run `python3 plot_block.py plotfile.block.txt` in `vads/gaet/`

To see plots of signal, noise level estimation and voice-active decision run `python3 plot_detection.py audiofile.wav plotfile.detection.txt plotfile.frame.txt` in `vads/gaet/`

To see plot of clear speech signal run `python3 plot_speech.py clearspeechfile.wav` in `vads/gaet/`

Energy Threshold Method
----------------------------------------------

Requirements:
* Python 3.5.2
* NumPy 1.13.1
* SciPy 0.19.1
* Matplotlib 2.0.2

Run `python3 et.py samplenoise.wav audiofile.wav` in `vads/et/`

To see plot of signal and voice-active decision run `python3 plot_detection.py audiofile.wav plotfile.detection.txt` in `vads/et/`
