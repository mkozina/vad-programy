import sys
import math
from array import *
import numpy as np
from scipy.io.wavfile import read
from scipy import stats
import scipy.linalg as linalg
import warnings

# Hann window
def w(n,N):
	return 0.5*(1-math.cos((2*math.pi*n)/(N-1)));

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

	# write plotting data to files
	filename1 = filename+".block.txt"
	plot_file = open(filename1, 'w')
	filename2 = filename+".detection.txt"
	vad_file = open(filename2, 'w')
	filename3 = filename+".frame.txt"
	frame_file = open(filename3, 'w')

	# block size in frames
	F = 75

	# block size: F frames * 160 samples = F * 10ms
	B = F*160
	s = str(B)
	s = s+"\n"
	plot_file.write(s)

	# frame size: 25ms (400 samples)
	# overlapping 15ms (240 samples)
	N = 400

	regress_neighborhood = 6

	# block number (starts from 1)
	block_no = 0
	# frame number (starts from 1)
	frame_no = 0

	# energy of each block
	energy = array('d')
	# noise level of each block
	noise_level = array('d')
	# voice-active decision for each frame
	vad_decision = array('d')

	# main loop over each block
	for i in range(0, len(signal[1]), B):

		# Geometrically Adaptive Energy Threshold (GAET) Method

		# Modified Amplitude Probability Distribution (MAPD)
		y = np.arange(B) / (B-1)
		x_signal = signal_samples[i:i+B]
		x_hann = array('d')
		block_pos = 0
		for sample in np.nditer(x_signal):
			x_hann.append( abs(sample*w(block_pos,B)) )
			block_pos += 1
		x = np.sort(x_hann)
		x_frames = abs(signal_samples[i:i+B+240])
		if len(x) < B:
			break

		# normalize signal samples
		ceiling = max(x)
		floor = min(x)
		ceiling2 = abs(floor)
		if ceiling > ceiling2:
			scale_param = ceiling
		else:
			scale_param = ceiling2

		x_frames_scaled = array('d')
		for a in x_frames:
			x_frames_scaled.append(a / scale_param)

		block_no += 1
		s = str(block_no)
		s = s+"\n"
		plot_file.write(s)
		for item in range(len(x)):
			plot_file.write("%i \n" % x[item])

		vad_file.write("%i \n" % i)

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
				Bprim_value = round((B-1)/5)
				Aprim_value = round(4*((B-1)/5))
			elif ii == 2:
				Bprim_value = round((B-1)/10)
				Aprim_value = round(9*((B-1)/10))
			elif ii == 3:
				Bprim_value = round((B-1)/20)
				Aprim_value = round(19*((B-1)/20))

			Bprim_x = x[Bprim_value]
			Bprim_y = y[Bprim_value]
			Aprim_x = x[Aprim_value]
			Aprim_y = y[Aprim_value]

			plot_file.write("\n")

			if A_x != Aprim_x:
				aAline = aline(A_x, A_y, Aprim_x, Aprim_y)
				plot_file.write("%.15f \n" % aAline)
				bAline = bline(A_x, A_y, Aprim_x, Aprim_y)
				plot_file.write("%.15f \n" % bAline)
				if B_x != Bprim_x:
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
						Q_x.append( 0 )
						plot_file.write("NaN\n")
						plot_file.write("NaN\n")
						plot_file.write("NaN\n")
						plot_file.write("NaN\n")
						plot_file.write("NaN\n")
						plot_file.write("NaN\n")
						plot_file.write("NaN\n")
						plot_file.write("NaN\n")
						plot_file.write("NaN\n")
						plot_file.write("NaN\n")
						plot_file.write("NaN\n")
						continue

					Qprim_x = c[1]
					plot_file.write("%.15f \n" % Qprim_x)
					Qprim_y = c[0]
					plot_file.write("%.15f \n" % Qprim_y)

					if C_x != Qprim_x:
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

							if seg_second > (B-1)-(regress_neighborhood-1):
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

						with warnings.catch_warnings():
							warnings.simplefilter("ignore", RuntimeWarning)
							(slope, intercept, r_value, p_value, std_err) = stats.linregress(x_regress, y_regress)

						# solve: y - ax = b
						a = np.array([[1,-aQline],[1,-slope]])
						b = np.array([bQline,intercept])
						try:
							c = linalg.solve(a,b)
						except ValueError:
							Q_x.append( x[seg_first] )
							plot_file.write("NaN\n")
							plot_file.write("NaN\n")
							plot_file.write("NaN\n")
							plot_file.write("NaN\n")
							continue
						Q_x.append( c[1] )
						Q_y.append( c[0] )

						plot_file.write("%.15f \n" % slope)
						plot_file.write("%.15f \n" % intercept)
						plot_file.write("%.15f \n" % c[1])
						plot_file.write("%.15f \n" % c[0])

					else:
						plot_file.write("NaN\n")
						plot_file.write("NaN\n")
						plot_file.write("NaN\n")
						plot_file.write("NaN\n")
						plot_file.write("NaN\n")
						plot_file.write("NaN\n")
						plot_file.write("NaN\n")
						plot_file.write("NaN\n")
						plot_file.write("NaN\n")

				else:
					plot_file.write("NaN\n")
					plot_file.write("NaN\n")
					plot_file.write("NaN\n")
					plot_file.write("NaN\n")
					plot_file.write("NaN\n")
					plot_file.write("NaN\n")
					plot_file.write("NaN\n")
					plot_file.write("NaN\n")
					plot_file.write("NaN\n")
					plot_file.write("NaN\n")
					plot_file.write("NaN\n")
					plot_file.write("NaN\n")
					plot_file.write("NaN\n")

			else:
				plot_file.write("NaN\n")
				plot_file.write("NaN\n")
				plot_file.write("NaN\n")
				plot_file.write("NaN\n")
				plot_file.write("NaN\n")
				plot_file.write("NaN\n")
				plot_file.write("NaN\n")
				plot_file.write("NaN\n")
				plot_file.write("NaN\n")
				plot_file.write("NaN\n")
				plot_file.write("NaN\n")
				plot_file.write("NaN\n")
				plot_file.write("NaN\n")
				plot_file.write("NaN\n")
				plot_file.write("NaN\n")

		#safety coefficient (0.8 < alpha < 1.2)
		alpha = 1.2

		Q_av = 0
		for a in Q_x:
			Q_av = Q_av + a
		noise_lvl_avg = alpha*(Q_av/len(Q_x))
		noise_level.append( noise_lvl_avg )

		vad_file.write("%.15f \n" % noise_level[block_no-1])

		# energy detector
		# calculate energy of a block
		energy.append( sum(np.square( signal_samples[i:i+B] ))/B )

		vad_file.write("%i \n" % energy[block_no-1])

		# frame counter (0 - F-1)
		frame_i = 0

		while frame_i < F:

			frame_no += 1
			frame_pos = 0
			vad_decision.append( 0 )
			for m in range(frame_i*160, (frame_i*160)+N):
				if (x_frames[m]*w(frame_pos,N)) > noise_level[block_no-1]:
					vad_decision[frame_no-1] += 1
				frame_pos += 1

			vad_decision[frame_no-1] /= N
			if vad_decision[frame_no-1] > 0.5:
				vad_decision[frame_no-1] = 1
			else:
				vad_decision[frame_no-1] = 0

			temp = (frame_no-1)*160
			frame_file.write("%i \n" % temp)
			frame_file.write("%i \n" % vad_decision[frame_no-1])

			frame_i += 1

	plot_file.close()
	vad_file.close()
	frame_file.close()

elif len(sys.argv) < 2:
	print("You must enter filename as parameter!")
else:
	print("You passed too much parameters!")

# (16000, array([-62, 158, 354, ..., 733, 693, 678], dtype=int16))
