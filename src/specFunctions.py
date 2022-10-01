import numpy as np


def wavelength_to_rgb(nm):
		#from: https://www.codedrome.com/exploring-the-visible-spectrum-in-python/
		#returns RGB vals for a given wavelength
		gamma = 0.8
		max_intensity = 255
		factor = 0
		rgb = {"R": 0, "G": 0, "B": 0}
		if 380 <= nm <= 439:
			rgb["R"] = -(nm - 440) / (440 - 380)
			rgb["G"] = 0.0
			rgb["B"] = 1.0
		elif 440 <= nm <= 489:
			rgb["R"] = 0.0
			rgb["G"] = (nm - 440) / (490 - 440)
			rgb["B"] = 1.0
		elif 490 <= nm <= 509:
			rgb["R"] = 0.0
			rgb["G"] = 1.0
			rgb["B"] = -(nm - 510) / (510 - 490)
		elif 510 <= nm <= 579:
			rgb["R"] = (nm - 510) / (580 - 510)
			rgb["G"] = 1.0
			rgb["B"] = 0.0
		elif 580 <= nm <= 644:
			rgb["R"] = 1.0
			rgb["G"] = -(nm - 645) / (645 - 580)
			rgb["B"] = 0.0
		elif 645 <= nm <= 780:
			rgb["R"] = 1.0
			rgb["G"] = 0.0
			rgb["B"] = 0.0
		if 380 <= nm <= 419:
			factor = 0.3 + 0.7 * (nm - 380) / (420 - 380)
		elif 420 <= nm <= 700:
			factor = 1.0
		elif 701 <= nm <= 780:
			factor = 0.3 + 0.7 * (780 - nm) / (780 - 700)
		if rgb["R"] > 0:
			rgb["R"] = int(max_intensity * ((rgb["R"] * factor) ** gamma))
		else:
			rgb["R"] = 0
		if rgb["G"] > 0:
			rgb["G"] = int(max_intensity * ((rgb["G"] * factor) ** gamma))
		else:
			rgb["G"] = 0
		if rgb["B"] > 0:
			rgb["B"] = int(max_intensity * ((rgb["B"] * factor) ** gamma))
		else:
			rgb["B"] = 0
		#display no color as gray
		if(rgb["R"]+rgb["G"]+rgb["B"]) == 0:
			rgb["R"] = 155
			rgb["G"] = 155
			rgb["B"] = 155
		return (rgb["R"], rgb["G"], rgb["B"])


def savitzky_golay(y, window_size, order, deriv=0, rate=1):
	#scipy
	#From: https://scipy.github.io/old-wiki/pages/Cookbook/SavitzkyGolay
	import numpy as np
	from math import factorial
	try:
		window_size = np.abs(np.int(window_size))
		order = np.abs(np.int(order))
	except ValueError:
		raise ValueError("window_size and order have to be of type int")
	if window_size % 2 != 1 or window_size < 1:
		raise TypeError("window_size size must be a positive odd number")
	if window_size < order + 2:
		raise TypeError("window_size is too small for the polynomials order")
	order_range = range(order+1)
	half_window = (window_size -1) // 2
	# precompute coefficients
	b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
	m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
	# pad the signal at the extremes with
	# values taken from the signal itself
	firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
	lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
	y = np.concatenate((firstvals, y, lastvals))
	return np.convolve( m[::-1], y, mode='valid')

def peakIndexes(y, thres=0.3, min_dist=1, thres_abs=False):
	#peakutils
	#from https://bitbucket.org/lucashnegri/peakutils/raw/f48d65a9b55f61fb65f368b75a2c53cbce132a0c/peakutils/peak.py
	if isinstance(y, np.ndarray) and np.issubdtype(y.dtype, np.unsignedinteger):
		raise ValueError("y must be signed")

	if not thres_abs:
		thres = thres * (np.max(y) - np.min(y)) + np.min(y)

	min_dist = int(min_dist)

	# compute first order difference
	dy = np.diff(y)

	# propagate left and right values successively to fill all plateau pixels (0-value)
	zeros, = np.where(dy == 0)

	# check if the signal is totally flat
	if len(zeros) == len(y) - 1:
		return np.array([])

	if len(zeros):
		# compute first order difference of zero indexes
		zeros_diff = np.diff(zeros)
		# check when zeros are not chained together
		zeros_diff_not_one, = np.add(np.where(zeros_diff != 1), 1)
		# make an array of the chained zero indexes
		zero_plateaus = np.split(zeros, zeros_diff_not_one)

		# fix if leftmost value in dy is zero
		if zero_plateaus[0][0] == 0:
			dy[zero_plateaus[0]] = dy[zero_plateaus[0][-1] + 1]
			zero_plateaus.pop(0)

		# fix if rightmost value of dy is zero
		if len(zero_plateaus) and zero_plateaus[-1][-1] == len(dy) - 1:
			dy[zero_plateaus[-1]] = dy[zero_plateaus[-1][0] - 1]
			zero_plateaus.pop(-1)

		# for each chain of zero indexes
		for plateau in zero_plateaus:
			median = np.median(plateau)
			# set leftmost values to leftmost non zero values
			dy[plateau[plateau < median]] = dy[plateau[0] - 1]
			# set rightmost and middle values to rightmost non zero values
			dy[plateau[plateau >= median]] = dy[plateau[-1] + 1]

	# find the peaks by using the first order difference
	peaks = np.where(
		(np.hstack([dy, 0.0]) < 0.0)
		& (np.hstack([0.0, dy]) > 0.0)
		& (np.greater(y, thres))
	)[0]

	# handle multiple peaks, respecting the minimum distance
	if peaks.size > 1 and min_dist > 1:
		highest = peaks[np.argsort(y[peaks])][::-1]
		rem = np.ones(y.size, dtype=bool)
		rem[peaks] = False

		for peak in highest:
			if not rem[peak]:
				sl = slice(max(0, peak - min_dist), peak + min_dist + 1)
				rem[sl] = True
				rem[peak] = False

		peaks = np.arange(y.size)[~rem]

	return peaks	


def readcal(width):
	#read in the calibration points
	#compute third order polynimial, and generate wavelength array!
	#Les Wright 28 Sept 2022
	errors = 0
	try:
		print("Loading calibration data")
		file = open('caldata.txt', 'r')
	except:
		errors = 1

	try:
		#read both the pixel numbers and wavelengths into two arrays.
		lines = file.readlines()
		line0 = lines[0].strip() #strip newline
		pixels = line0.split(',') #split on ,
		pixels = [int(i) for i in pixels] #convert list of strings to ints
		line1 = lines[1].strip()
		wavelengths = line1.split(',')
		wavelengths = [float(i) for i in wavelengths]#convert list of strings to floats
	except:
		errors = 1

	try:
		if (len(pixels) != len(wavelengths)):
			#The Calibration points are of unequal length!
			errors = 1
		if (len(pixels) < 3):
			#The Cal data contains less than 3 pixels!
			errors = 1
		if (len(wavelengths) < 3):
			#The Cal data contains less than 3 wavelengths!
			errors = 1
	except:
		errors = 1

	if errors == 1:
		print("Loading of Calibration data failed (missing caldata.txt or corrupted data!")
		print("Loading placeholder data...")
		print("You MUST perform a Calibration to use this software!")
		pixels = [0,400,800]
		wavelengths = [380,560,750]


	#create an array for the data...
	wavelengthData = []

	if (len(pixels) == 3):
		print("Calculating second order polynomial...")
		coefficients = np.poly1d(np.polyfit(pixels, wavelengths, 2))
		print(coefficients)
		C1 = coefficients[2]
		C2 = coefficients[1]
		C3 = coefficients[0]
		print("Generating Wavelength Data!")
		for pixel in range(width):
			wavelength=((C1*pixel**2)+(C2*pixel)+C3)
			wavelength = round(wavelength,6) #because seriously!
			wavelengthData.append(wavelength)
		print("Done! Note that calibration with only 3 wavelengths will not be accurate!")

	if (len(pixels) > 3):
		print("Calculating third order polynomial...")
		coefficients = np.poly1d(np.polyfit(pixels, wavelengths, 3))
		print(coefficients)
		#note this pulls out extremely precise numbers.
		#this causes slight differences in vals then when we compute manual, but hey ho, more precision
		#that said, we waste that precision later, but tbh, we wouldn't get that kind of precision in
		#the real world anyway! 1/10 of a nm is more than adequate!
		C1 = coefficients[3]
		C2 = coefficients[2]
		C3 = coefficients[1]
		C4 = coefficients[0]
		'''
		print(C1)
		print(C2)
		print(C3)
		print(C4)
		'''
		print("Generating Wavelength Data!")
		for pixel in range(width):		
			wavelength=((C1*pixel**3)+(C2*pixel**2)+(C3*pixel)+C4)
			wavelength = round(wavelength,6)
			wavelengthData.append(wavelength)

		#final job, we need to compare all the recorded wavelenths with predicted wavelengths
		#and note the deviation!
		#do something if it is too big!
		predicted = []
		#iterate over the original pixelnumber array and predict results
		for i in pixels:
			px = i
			y=((C1*px**3)+(C2*px**2)+(C3*px)+C4)
			predicted.append(y)

		#calculate 2 squared of the result
		#if this is close to 1 we are all good!
		corr_matrix = np.corrcoef(wavelengths, predicted)
		corr = corr_matrix[0,1]
		R_sq = corr**2
		 
		print("R-Squared="+str(R_sq))

	return wavelengthData
























