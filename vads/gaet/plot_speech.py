import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import read

if len(sys.argv) == 2:

	# open audio file 
	filename = sys.argv[1]
	signal = read(filename)

	# array of samples
	signal_samples = signal[1]
	signal_samples = signal_samples.astype(np.int64)

	# normalize plot data
	ceiling = max(signal_samples)
	floor = min(signal_samples)
	ceiling2 = abs(floor)
	if ceiling > ceiling2:
		scale_param = ceiling
	else:
		scale_param = ceiling2

	signal_samples_scaled = [i / scale_param for i in signal_samples]

	# plot clear speech
	axes = plt.gca()
	axes.set_ylim([-1.04,1.04])
	plt.plot(signal_samples_scaled)
	plt.ylabel("Amplitude")
	plt.xlabel("Time (samples)")
	plt.title("%s - clear speech" % filename)
	plt.show()

elif len(sys.argv) < 2:
	print("You must enter audio filename as parameter!")
else:
	print("You passed too much parameters!")
