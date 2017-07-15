import sys
import rpy2
import rpy2.robjects as robjects

if len(sys.argv) == 5:
	no = int(sys.argv[1])
	dist = sys.argv[2]
	param1dist = float(sys.argv[3])
	param2dist = float(sys.argv[4])
	if dist == "rbeta":
		rbeta = robjects.r['rbeta']
		res = rbeta(no,param1dist,param2dist)
	elif dist == "rgamma":
		rgamma = robjects.r['rgamma']
		res = rgamma(no,param1dist,scale=param2dist)
	elif dist == "rnorm":
		rnorm = robjects.r['rnorm']
		res = rnorm(no,param1dist,param2dist)
	elif dist == "runif":
		runif = robjects.r['runif']
		res = runif(no,param1dist,param2dist)
	for i in range(no):
		print(abs(round(res[i],2)))
else:
	print("No arg found!")
