import sys
from array import *
import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import read

if len(sys.argv) == 3:

	# open audio file 
	filename = sys.argv[1]
	signal = read(filename)

	# array of samples
	signal_samples = signal[1]
	signal_samples = signal_samples.astype(np.int64)

	log1 = sys.argv[2]
	vad_file = open(log1, 'r')

	sample_frame = array('Q')
	# voice-active decision for each frame
	vad_decision = array('i')

	# normalize plot data
	ceiling = max(signal_samples)
	floor = min(signal_samples)
	ceiling2 = abs(floor)
	if ceiling > ceiling2:
		scale_param = ceiling
	else:
		scale_param = ceiling2

	signal_samples_scaled = [i / scale_param for i in signal_samples]

	for i, line in enumerate(vad_file):
		line_int = line.rstrip('\n')
		if i%2 == 0:
			sample_frame.append( int(line_int) )
		elif i%2 == 1:
			vad_decision.append( int(line_int) )

	# plot signal
	plt.plot(signal_samples_scaled)
	plt.plot(sample_frame, vad_decision, 'ko')
	plt.ylabel("Amplitude")
	plt.xlabel("Time (samples)")
	plt.title("%s" % filename)
	plt.show()

	vad_file.close()

elif len(sys.argv) < 3:
	print("You must enter audio and detection log filenames as parameter!")
else:
	print("You passed too much parameters!")
