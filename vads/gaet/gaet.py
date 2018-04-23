import sys
import math
from array import *
import numpy as np
from scipy.io.wavfile import read
from scipy import stats
import scipy.linalg as linalg

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

	# write plotting data to file
	filename = filename+".txt"
	plot_file = open(filename, 'w')

	# frame size: 400 samples
	# overlapping 15ms (240 samples)
	N = 400
	s = str(N)
	s = s+"\n"
	plot_file.write(s)

	regress_neighborhood = 6

	# frame number (starts from 1)
	frame_no = 0

	# energy of each frame
	energy = array('d')
	# noise level of each frame
	noise_level = array('d')
	# voice-active decision for each frame
	vad_decision = array('d')

	# main loop over each frame
	for i in range(0, len(signal[1]), 160):

		frame_no += 1
		s = str(frame_no)
		s = s+"\n"
		plot_file.write(s)

		# Geometrically Adaptive Energy Threshold (GAET) Method

		# Modified Amplitude Probability Distribution (MAPD)
		y = np.arange(N) / (N-1)
		x = np.sort( abs(signal_samples[i:i+N]) )
		for item in range(len(x)):
			plot_file.write("%i \n" % x[item])

		# set point B to bottom left corner
		B_x = x[0]
		B_y = y[0]
		# set point A to top right corner
		A_x = x[-1]
		A_y = y[-1]
		# top left corner
		C_x = B_x
		C_y = A_y

		Q_x = array('d')
		Q_y = array('d')

		for ii in range(1, 4):

			stop = "no"

			# values of points B' and A' from Tanyer-Ozer
			# Bprim_y = 1/5, 1/10 and 1/20
			# Aprim_y = 4/5, 9/10 and 19/20
			# these values are observed to be not very critical

			if ii == 1:
				Bprim_value = round((N-1)/5)
				Aprim_value = round(4*((N-1)/5))
			elif ii == 2:
				Bprim_value = round((N-1)/10)
				Aprim_value = round(9*((N-1)/10))
			elif ii == 3:
				Bprim_value = round((N-1)/20)
				Aprim_value = round(19*((N-1)/20))

			Bprim_x = x[Bprim_value]
			Bprim_y = y[Bprim_value]
			Aprim_x = x[Aprim_value]
			Aprim_y = y[Aprim_value]

			plot_file.write("\n")
			aAline = aline(A_x, A_y, Aprim_x, Aprim_y)
			plot_file.write("%.15f \n" % aAline)
			bAline = bline(A_x, A_y, Aprim_x, Aprim_y)
			plot_file.write("%.15f \n" % bAline)
			aBline = aline(B_x, B_y, Bprim_x, Bprim_y)
			plot_file.write("%.15f \n" % aBline)
			bBline = bline(B_x, B_y, Bprim_x, Bprim_y)
			plot_file.write("%.15f \n" % bBline)

			# solve: y - ax = b
			a = np.array([[1,-aAline],[1,-aBline]])
			b = np.array([bAline,bBline])
			try:
				c = linalg.solve(a,b)
			except np.linalg.linalg.LinAlgError:
				vad_decision.append( -1 )
			Qprim_x = c[1]
			plot_file.write("%.15f \n" % Qprim_x)
			Qprim_y = c[0]
			plot_file.write("%.15f \n" % Qprim_y)

			aQline = aline(C_x, C_y, Qprim_x, Qprim_y)
			plot_file.write("%.15f \n" % aQline)
			bQline = bline(C_x, C_y, Qprim_x, Qprim_y)
			plot_file.write("%.15f \n" % bQline)

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

				if seg_second > (N-1)-(regress_neighborhood-1):
					Q_x.append( x[len(x)-1] )
					Q_y.append( y[len(y)-1] )

					# save unused values to maintain correct length of file
					plot_file.write("NaN\n")
					plot_file.write("NaN\n")
					plot_file.write("NaN\n")
					plot_file.write("NaN\n")
					plot_file.write("NaN\n")
					plot_file.write("NaN\n")
					plot_file.write("NaN\n")

					stop = "yes"
					break

			if "yes" in stop:
				continue

			x_regress = array('d')
			y_regress = array('d')

			for k in range(0, regress_neighborhood):
				x_regress.append( x[seg_first-k] )
				y_regress.append( y[seg_first-k] )

			for k in range(0, regress_neighborhood):
				x_regress.append( x[seg_second+k] )
				y_regress.append( y[seg_second+k] )

			plot_file.write("%i \n" % regress_neighborhood)
			plot_file.write("%i \n" % seg_first)
			plot_file.write("%i \n" % seg_second)

			(slope, intercept, r_value, p_value, std_err) = stats.linregress(x_regress, y_regress)

			# solve: y - ax = b
			a = np.array([[1,-aQline],[1,-slope]])
			b = np.array([bQline,intercept])
			c = linalg.solve(a,b)
			Q_x.append( c[1] )
			Q_y.append( c[0] )

			plot_file.write("%.15f \n" % slope)
			plot_file.write("%.15f \n" % intercept)
			plot_file.write("%.15f \n" % c[1])
			plot_file.write("%.15f \n" % c[0])

		#safety coefficient (0.8 < alpha < 1.2)
		alpha = 1

		noise_level.append( alpha*((Q_x[0]+Q_x[1]+Q_x[2])/3) )

		vad_decision.append( 0 )
		for m in range(0, N):
			if x[m] > noise_level[frame_no-1]:
				vad_decision[frame_no-1] += 1

		vad_decision[frame_no-1] /= N
		if vad_decision[frame_no-1] > 0.5:
			vad_decision[frame_no-1] = 1
		else:
			vad_decision[frame_no-1] = 0

		print(frame_no)
		print(vad_decision[frame_no-1])

		# energy detector
		# calculate energy of a frame
		energy.append( sum(np.square(signal_samples[i:i+N])) )

	plot_file.close()

elif len(sys.argv) < 2:
	print("You must enter filename as parameter!")
else:
	print("You passed too much parameters!")

# (16000, array([-62, 158, 354, ..., 733, 693, 678], dtype=int16))
