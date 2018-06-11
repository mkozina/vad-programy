import sys
from array import *
import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import read

if len(sys.argv) == 4:

	# open audio file 
	filename = sys.argv[1]
	signal = read(filename)

	# array of samples
	signal_samples = signal[1]
	signal_samples = signal_samples.astype(np.int64)

	log1 = sys.argv[2]
	vad_file = open(log1, 'r')
	log2 = sys.argv[3]
	frame_file = open(log2, 'r')

	sample = array('Q')
	sample_frame = array('Q')
	# energy of each block
	energy = array('d')
	# noise level of each block
	noise_level = array('d')
	# voice-active decision for each frame
	vad_decision = array('i')

	for i, line in enumerate(vad_file):
		line_int = line.rstrip('\n')
		if i%3 == 0:
			sample.append( int(line_int) )
		elif i%3 == 1:
			noise_level.append( float(line_int) )
		elif i%3 == 2:
			energy.append( int(line_int) )

	for i, line in enumerate(frame_file):
		line_int = line.rstrip('\n')
		if i%2 == 0:
			sample_frame.append( int(line_int) )
		elif i%2 == 1:
			vad_decision.append( int(line_int) )

	# normalize plot data
	ceiling = max(signal_samples)
	floor = min(signal_samples)
	ceiling2 = abs(floor)
	if ceiling > ceiling2:
		scale_param = ceiling
	else:
		scale_param = ceiling2

	# normalize noise level
	ceiling = max(noise_level)
	floor = min(noise_level)
	ceiling2 = abs(floor)
	if ceiling > ceiling2:
		noise_scale_param = ceiling
	else:
		noise_scale_param = ceiling2

	# normalize energy
	ceiling = max(energy)
	floor = min(energy)
	ceiling2 = abs(floor)
	if ceiling > ceiling2:
		energy_scale_param = ceiling
	else:
		energy_scale_param = ceiling2

	signal_samples_scaled = [i / scale_param for i in signal_samples]
	noise_level_scaled = [i / scale_param for i in noise_level]
	energy_scaled = [i / energy_scale_param for i in energy]

	vad_signal = array('d')
	i = 0
	while i < len(energy):
		vad_signal.append(energy_scaled[i] - noise_level_scaled[i])
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
	plt.plot(sample, noise_level_scaled, 'ro')
	plt.plot(sample, energy_scaled, 'yo')
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

	# plot binary detection
	plt.plot(sample_frame, vad_decision, 'ko')
	plt.ylabel("Decision")
	plt.xlabel("Time (samples)")
	plt.title("%s - binary detection w/o post-processing" % filename)
	plt.show()

	# plot binary detection
	#plt.plot(sample_frame, vad_decision, 'ko')
	#plt.ylabel("Decision")
	#plt.xlabel("Time (samples)")
	#plt.title("%s - binary detection w/ post-processing" % filename)
	#plt.show()

	# plot signal
	plt.plot(signal_samples_scaled)
	plt.plot(sample, noise_level_scaled, 'ro')
	plt.plot(sample, vad_signal_scaled, 'yo')
	plt.plot(sample_frame, vad_decision, 'ko')
	plt.ylabel("Amplitude")
	plt.xlabel("Time (samples)")
	plt.title("%s" % filename)
	plt.show()

	vad_file.close()

elif len(sys.argv) < 4:
	print("You must enter audio and detection log filenames as parameter!")
else:
	print("You passed too much parameters!")
