import sys
from array import *
import numpy as np
from scipy.io.wavfile import read

if len(sys.argv) == 3:

	# open noise file 
	filename = sys.argv[1]
	noise = read(filename)
	print("\nsampling rate:", noise[0])
	print("no of audio samples:", len(noise[1]), "\n")
	# array of samples
	noise_samples = noise[1]
	noise_samples = noise_samples.astype(np.int64)

	# open audio file 
	filename = sys.argv[2]
	signal = read(filename)
	print("\nsampling rate:", signal[0])
	print("no of audio samples:", len(signal[1]), "\n")
	# array of samples
	signal_samples = signal[1]
	signal_samples = signal_samples.astype(np.int64)

	filename2 = filename+".detection.txt"
	vad_file = open(filename2, 'w')

	# frame size: 25ms (400 samples)
	# overlapping 15ms (240 samples)
	N = 400

	# frame number (starts from 1)
	frame_no = 0

	# voice-active decision for each frame
	vad_decision = array('d')

	energy = 0

	# initial value of threshold
	for i in range(0, len(noise[1]), 160):

		x = noise_samples[i:i+N]
		if len(x) < N:
			break

		frame_no += 1

		# energy detector
		# calculate energy of a frame
		energy += sum(np.square( x )/N)

	energy_r = (1/frame_no)*energy

	frame_no = 0

	# main loop over each frame
	for i in range(0, len(signal[1]), 160):

		x = signal_samples[i:i+N]
		if len(x) < N:
			break

		frame_no += 1

		# energy detector
		# calculate energy of a frame
		energy = sum(np.square( x )/N)

		k = 1.4
		p = 0.2

		if energy > k*energy_r:
			vad_decision.append( 1 )
		else:
			vad_decision.append( 0 )
			energy_r = ((1-p)*energy_r) + (p*energy)

		temp = (frame_no-1)*160
		vad_file.write("%i \n" % temp)
		vad_file.write("%i \n" % vad_decision[frame_no-1])

	vad_file.close()

elif len(sys.argv) < 3:
	print("You must enter noise and audio filenames as parameter!")
else:
	print("You passed too much parameters!")
