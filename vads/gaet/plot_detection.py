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

	ceiling = max(signal_samples)

	log = sys.argv[2]
	vad_file = open(log, 'r')

	sample = array('Q')
	# energy of each frame
	energy = array('d')
	# noise level of each frame
	noise_level = array('d')
	# voice-active decision for each frame
	vad_decision = array('i')

	for i, line in enumerate(vad_file):
		line_int = line.rstrip('\n')
		if i%4 == 0:
			sample.append( int(line_int) )
		elif i%4 == 1:
			noise_level.append( float(line_int) )
		elif i%4 == 2:
			vad_decision.append( int(line_int) )
		elif i%4 == 3:
			energy.append( int(line_int) )

	vad_decision_signal = [i * ceiling for i in vad_decision]

	# plot frame
	plt.plot(signal_samples)
	plt.plot(sample, noise_level, 'ro')
	plt.plot(sample, vad_decision_signal, 'ko')
	#plt.axhline(y=noise_level[frame_no-1], color='m')
	plt.ylabel("Amplitude")
	plt.xlabel("Time (samples)")
	plt.title("%s" % filename)
	mng = plt.get_current_fig_manager()
	mng.resize(*mng.window.maxsize())
	plt.show()

	# plot soft detection
	plt.plot(sample, vad_decision, 'ro')
	plt.ylabel("Decision")
	plt.xlabel("Time (samples)")
	plt.title("%s" % filename)
	mng = plt.get_current_fig_manager()
	mng.resize(*mng.window.maxsize())
	plt.show()

	vad_file.close()

elif len(sys.argv) < 3:
	print("You must enter audio and detection log filenames as parameter!")
else:
	print("You passed too much parameters!")
