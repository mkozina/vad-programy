import sys
from array import *
import numpy as np
import matplotlib.pyplot as plt

if len(sys.argv) == 2:

	filename = sys.argv[1]
	plot_file = open(filename, 'r')

	# frame size
	N = plot_file.readline()
	N = N.rstrip('\n')
	N = int(N)

	# frame no - ???1575??? - (starts from 1)
	frame_no = input('Plot frame: ')
	frame_no = int(frame_no)

	# y
	y = np.arange(N) / (N-1)

	# x
	x = array('I')
	for i, line in enumerate(plot_file):
		if i >= ((frame_no-1)*(N+1+48))+1 and i <= ((frame_no-1)*(N+1+48))+1+(N-1):
			line_int = line.rstrip('\n')
			line_int = int(line_int)
			x.append( line_int )
		elif i > ((frame_no-1)*(N+1+48))+1+(N-1):
			break

	B_x = x[0]
	A_x = x[-1]

	for ii in range(1, 4):

		for i, line in enumerate(plot_file):
			if i == 0:
				line_int = line.rstrip('\n')
				line_int = float(line_int)
				aAline = line_int
			elif i == 1:
				line_int = line.rstrip('\n')
				line_int = float(line_int)
				bAline = line_int
			elif i == 2:
				line_int = line.rstrip('\n')
				line_int = float(line_int)
				aBline = line_int
			elif i == 3:
				line_int = line.rstrip('\n')
				line_int = float(line_int)
				bBline = line_int
			elif i == 4:
				line_int = line.rstrip('\n')
				line_int = float(line_int)
				Qprim_x = line_int
			elif i == 5:
				line_int = line.rstrip('\n')
				line_int = float(line_int)
				Qprim_y = line_int
			elif i == 6:
				line_int = line.rstrip('\n')
				line_int = float(line_int)
				aQline = line_int
			elif i == 7:
				line_int = line.rstrip('\n')
				line_int = float(line_int)
				bQline = line_int
			elif i == 8:
				line_int = line.rstrip('\n')
				line_int = int(line_int)
				regress_neighborhood = line_int
			elif i == 9:
				line_int = line.rstrip('\n')
				line_int = int(line_int)
				seg_first = line_int
			elif i == 10:
				line_int = line.rstrip('\n')
				line_int = int(line_int)
				seg_second = line_int
			elif i == 11:
				line_int = line.rstrip('\n')
				line_int = float(line_int)
				slope = line_int
			elif i == 12:
				line_int = line.rstrip('\n')
				line_int = float(line_int)
				intercept = line_int
			elif i == 13:
				line_int = line.rstrip('\n')
				line_int = float(line_int)
				Q_x = line_int
			elif i == 14:
				line_int = line.rstrip('\n')
				line_int = float(line_int)
				Q_y = line_int
			elif i > 14:
				break

		# lines that crosses A', B' and Q' points

		Aline_x = array('d')
		Aline_y = array('d')
		Bline_x = array('d')
		Bline_y = array('d')
		Qline_x = array('d')
		Qline_y = array('d')

		for j in range(B_x, A_x+1):
			Aline_x.append( j )
			Aline_y.append( aAline*j + bAline )
			Bline_x.append( j )
			Bline_y.append( aBline*j + bBline )
			Qline_x.append( j )
			Qline_y.append( aQline*j + bQline )

		plt.plot(Aline_x, Aline_y, 'r-')
		plt.plot(Bline_x, Bline_y, 'g-')
		plt.plot(Qprim_x, Qprim_y, 'ko')
		plt.plot(Qline_x, Qline_y, 'k-')

		# linear regression and Q point

		x_regress = array('d')

		for k in range(0, regress_neighborhood):
			x_regress.append( x[seg_first-k] )
			x_regress.append( x[seg_second+k] )

			plt.plot(x[seg_first-k], y[seg_first-k], 'yo')
			plt.plot(x[seg_second+k], y[seg_second+k], 'yo')

		Rline_x = array('d')
		Rline_y = array('d')

		for l in range(0, 2*regress_neighborhood):
			Rline_x.append( x_regress[l] )
			Rline_y.append( slope*x_regress[l] + intercept )

		plt.plot(Rline_x, Rline_y, 'm')
		plt.plot(Q_x, Q_y, 'mo')

	# plot GAET
	plt.scatter(x, y)
	plt.title("%s, frame: %i" % (filename, frame_no))
	mng = plt.get_current_fig_manager()
	mng.resize(*mng.window.maxsize())
	plt.show()

	# plot frame
#	plt.plot(signal_samples[i:i+N])
#	plt.axhline(y=noise_level[frame_no-1], color='m')
#	plt.ylabel("Amplitude")
#	plt.xlabel("Time (samples)")
#	plt.title("%s, frame: %i" % (filename, frame_no))
#	mng = plt.get_current_fig_manager()
#	mng.resize(*mng.window.maxsize())
#	plt.show()

	plot_file.close()

elif len(sys.argv) < 2:
	print("You must enter filename as parameter!")
else:
	print("You passed too much parameters!")
