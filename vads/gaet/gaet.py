import sys
import math
from array import *
import numpy as np
from scipy.io.wavfile import read
from scipy import stats
import scipy.linalg as linalg
import matplotlib.pyplot as plt

# calculate coefficient a of a linear function that passes through (x1,y1) and (x2,y2)
def aline(x1, y1, x2, y2):
	a = (y2-y1)/(x2-x1)
	return a;

# calculate coefficient b of a linear function that passes through (x1,y1) and (x2,y2)
def bline(x1, y1, x2, y2):
	b = ((x2-x1)*y1 - (y2-y1)*x1) / (x2-x1)
	return b;

if len(sys.argv) == 2:

	# open audio file 
	filename = sys.argv[1]
	signal = read(filename)
	print("\nsampling rate:", signal[0])
	print("no of audio samples:", len(signal[1]), "\n")
	# array of samples
	signal_samples = signal[1]
	signal_samples = signal_samples.astype(np.int64)

	# frame size: 400 samples
	# overlapping 15ms (240 samples)
	N = 400
	# energy of each frame
	energy = array('d')

	# frame number (starts from 1)
	frame_no = 0

	# main loop over each frame
	for i in range(0, len(signal[1]), 160):

		frame_no += 1

		# Geometrically Adaptive Energy Threshold (GAET) Method

		# Modified Amplitude Probability Distribution (MAPD)
		y = np.arange(N) / (N-1)
		x = np.sort( abs(signal_samples[i:i+N]) )

		# set point B to bottom left corner
		B_x = x[0]
		B_y = y[0]
		# set point A to top right corner
		A_x = x[-1]
		A_y = y[-1]
		# top left corner
		C_x = B_x
		C_y = A_y

		# values of points B' and A' from Tanyer-Ozer
		# Bprim_y = 1/5, 1/10 and 1/20
		# Aprim_y = 4/5, 9/10 and 19/20
		# these values are observed to be not very critical

		Bprim_value = round((N-1)/5)
		Aprim_value = round(4*((N-1)/5))

		Bprim_x = x[Bprim_value]
		Bprim_y = y[Bprim_value]
		Aprim_x = x[Aprim_value]
		Aprim_y = y[Aprim_value]

		Aline_x = array('d')
		Aline_y = array('d')
		Bline_x = array('d')
		Bline_y = array('d')
		Qline_x = array('d')
		Qline_y = array('d')

		aAline = aline(A_x, A_y, Aprim_x, Aprim_y)
		bAline = bline(A_x, A_y, Aprim_x, Aprim_y)
		aBline = aline(B_x, B_y, Bprim_x, Bprim_y)
		bBline = bline(B_x, B_y, Bprim_x, Bprim_y)

		# solve: y - ax = b
		a = np.array([[1,-aAline],[1,-aBline]])
		b = np.array([bAline,bBline])
		c = linalg.solve(a,b)
		Qprim_x = c[1]
		Qprim_y = c[0]

		aQline = aline(C_x, C_y, Qprim_x, Qprim_y)
		bQline = bline(C_x, C_y, Qprim_x, Qprim_y)

		for j in range(B_x, A_x+1):
			Aline_x.append( j )
			Aline_y.append( aAline*j + bAline )
			Bline_x.append( j )
			Bline_y.append( aBline*j + bBline )
			Qline_x.append( j )
			Qline_y.append( aQline*j + bQline )

# #########################
		# point Q

		seg_base = math.ceil(len(x)/2)
		seg_first = 0
		seg_second = seg_base
		prev_seg_first = -1
		prev_seg_second = -1

		while (seg_first != prev_seg_first) or (seg_second != prev_seg_second):

			firstQ = aQline*x[seg_first] + bQline
			secondQ = aQline*x[seg_second] + bQline

			prev_seg_first = seg_first
			prev_seg_second =	seg_second
			seg_base = math.ceil(seg_base/2)

			if y[seg_first] <= firstQ and y[seg_second] <= secondQ:
				seg_first = seg_second
				seg_second = seg_second + seg_base
			elif y[seg_first] <= firstQ and y[seg_second] > secondQ:
				seg_second = seg_first + seg_base

		x_regress = array('d')
		y_regress = array('d')

		for k in range(0, 6):
			x_regress.append( x[seg_first-k] )
			y_regress.append( y[seg_first-k] )
			plt.plot(x[seg_first-k], y[seg_first-k], 'yo')

		for k in range(0, 6):
			x_regress.append( x[seg_second+k] )
			y_regress.append( y[seg_second+k] )
			plt.plot(x[seg_second+k], y[seg_second+k], 'yo')

		(slope, intercept, r_value, p_value, std_err) = stats.linregress(x_regress, y_regress)

		Rline_x = array('d')
		Rline_y = array('d')

		for l in range(0, 12):
			Rline_x.append( x_regress[l] )
			Rline_y.append( slope*x_regress[l] + intercept )

		plt.plot(Rline_x, Rline_y, 'm')

		# solve: y - ax = b
		a = np.array([[1,-aQline],[1,-slope]])
		b = np.array([bQline,intercept])
		c = linalg.solve(a,b)
		Q_x = c[1]
		Q_y = c[0]

		plt.plot(Q_x, Q_y, 'mo')

		#safety coefficient alpha (0.8 < alpha < 1.2)
		alpha = 1
		noise_level = alpha*Q_x

# #########################

		# plot only first 149 frames (ca 1505ms)
		if i <= 23680:
		#if frame_no == 135:

			# plot GAET
			plt.scatter(x, y)
			plt.plot(Aline_x, Aline_y, 'r-')
			plt.plot(Bline_x, Bline_y, 'g-')
			plt.plot(Qprim_x, Qprim_y, 'ko')
			plt.plot(Qline_x, Qline_y, 'k-')
			plt.title("%s, frame: %i" % (filename, frame_no))
			mng = plt.get_current_fig_manager()
			mng.resize(*mng.window.maxsize())
			plt.show()

			# plot frame
			plt.plot(signal_samples[i:i+N])
			plt.ylabel("Amplitude")
			plt.xlabel("Time (samples)")
			plt.title("%s, frame: %i" % (filename, frame_no))
			mng = plt.get_current_fig_manager()
			mng.resize(*mng.window.maxsize())
			plt.show()

		# energy detector
		# calculate energy of a frame
		energy.append( sum(np.square(signal_samples[i:i+N])) )

elif len(sys.argv) < 2:
	print("You must enter filename as parameter!")
else:
	print("You passed too much parameters!")

# (16000, array([-62, 158, 354, ..., 733, 693, 678], dtype=int16))
