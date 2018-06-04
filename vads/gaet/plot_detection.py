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

	log = sys.argv[2]
	vad_file = open(log, 'r')

	sample = array('Q')
	# energy of each block
	energy = array('d')
	# noise level of each block
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

	# normalize plot data
	ceiling = max(signal_samples)
	floor = min(signal_samples)
	ceiling2 = abs(floor)
	if ceiling > ceiling2:
		scale_param = ceiling
	else:
		scale_param = ceiling2

	signal_samples_scaled = [i / scale_param for i in signal_samples]
	noise_level_scaled = [i / scale_param for i in noise_level]
	energy_scaled = [i / scale_param for i in energy]

	vad_signal = array('d')
	i = 0
	while i < len(energy):
		vad_signal.append(energy[i] - noise_level[i])
		i += 1

	# normalize vad_signal
	ceiling = max(vad_signal)
	floor = min(vad_signal)
	ceiling2 = abs(floor)
	if ceiling > ceiling2:
		vad_scale_param = ceiling
	else:
		vad_scale_param = ceiling2

	vad_signal_scaled = [i / vad_scale_param for i in vad_signal]

	# plot noisy speech
	plt.plot(signal_samples_scaled)
	plt.ylabel("Amplitude")
	plt.xlabel("Time (samples)")
	plt.title("%s - noisy speech" % filename)
	plt.show()

	# plot noise level
	axes = plt.gca()
	#axes.set_ylim([-0.04,1.04])
	plt.plot(sample, noise_level, 'ro')
	plt.plot(sample, energy, 'yo')
	plt.ylabel("Amplitude")
	plt.xlabel("Time (samples)")
	plt.title("%s - noise level" % filename)
	plt.show()

	# plot vad signal
	plt.plot(sample, vad_signal_scaled, 'yo')
	plt.ylabel("Amplitude")
	plt.xlabel("Time (samples)")
	plt.title("%s - vad signal" % filename)
	plt.show()

	# plot soft detection
	plt.plot(sample, vad_decision, 'ko')
	plt.ylabel("Decision")
	plt.xlabel("Time (samples)")
	plt.title("%s - soft detection" % filename)
	plt.show()

	# plot signal
	plt.plot(signal_samples_scaled)
	plt.plot(sample, noise_level_scaled, 'ro')
	plt.plot(sample, vad_signal_scaled, 'yo')
	plt.plot(sample, vad_decision, 'ko')
	#plt.axhline(y=noise_level[frame_no-1], color='m')
	plt.ylabel("Amplitude")
	plt.xlabel("Time (samples)")
	plt.title("%s" % filename)
	plt.show()

	vad_file.close()

elif len(sys.argv) < 3:
	print("You must enter audio and detection log filenames as parameter!")
else:
	print("You passed too much parameters!")
