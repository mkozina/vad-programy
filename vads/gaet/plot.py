import sys
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
	for i, line in enumerate(plot_file):
		if i >= ((frame_no-1)*(N+1))+1 and i <= ((frame_no-1)*(N+1))+1+(N-1):
			print(line)

#	if plot != 0 and frame_no == plot:

#		Aline_x = array('d')
#		Aline_y = array('d')
#		Bline_x = array('d')
#		Bline_y = array('d')
#		Qline_x = array('d')
#		Qline_y = array('d')

#		for j in range(B_x, A_x+1):
#			Aline_x.append( j )
#			Aline_y.append( aAline*j + bAline )
#			Bline_x.append( j )
#			Bline_y.append( aBline*j + bBline )
#			Qline_x.append( j )
#			Qline_y.append( aQline*j + bQline )

#		plt.plot(Aline_x, Aline_y, 'r-')
#		plt.plot(Bline_x, Bline_y, 'g-')
#		plt.plot(Qprim_x, Qprim_y, 'ko')
#		plt.plot(Qline_x, Qline_y, 'k-')

#	if plot != 0 and frame_no == plot:
#		plt.plot(x[seg_first-k], y[seg_first-k], 'yo')

#	if plot != 0 and frame_no == plot:
#		plt.plot(x[seg_second+k], y[seg_second+k], 'yo')

#	if plot != 0 and frame_no == plot:

#		Rline_x = array('d')
#		Rline_y = array('d')

#		for l in range(0, 2*regress_neighborhood):
#			Rline_x.append( x_regress[l] )
#			Rline_y.append( slope*x_regress[l] + intercept )

#		plt.plot(Rline_x, Rline_y, 'm')
#		plt.plot(Q_x[ii-1], Q_y[ii-1], 'mo')

	# plot GAET
#	plt.scatter(x, y)
#	plt.title("%s, frame: %i" % (filename, frame_no))
#	mng = plt.get_current_fig_manager()
#	mng.resize(*mng.window.maxsize())
#	plt.show()

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
