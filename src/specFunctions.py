'''
PySpectrometer2 Les Wright 2022
https://www.youtube.com/leslaboratory
https://github.com/leswright1977

This project is a follow on from: https://github.com/leswright1977/PySpectrometer 

This is a more advanced, but more flexible version of the original program. Tk Has been dropped as the GUI to allow fullscreen mode on Raspberry Pi systems and the iterface is designed to fit 800*480 screens, which seem to be a common resolutin for RPi LCD's, paving the way for the creation of a stand alone benchtop instrument.

Whats new:
Higher reolution (800px wide graph)
3 row pixel averaging of sensor data
Fullscreen option for the Spectrometer graph
3rd order polymonial fit of calibration data for accurate measurement.
Improved graph labelling
Labelled measurement cursors
Optional waterfall display for recording spectra changes over time.
Key Bindings for all operations

All old features have been kept, including peak hold, peak detect, Savitsky Golay filter, and the ability to save graphs as png and data as CSV.

For instructions please consult the readme!

Future work:
It is planned to add in GPIO support, to allow the use of buttons and knobs to control the Spectrometer.
'''


import numpy as np
import time

def wavelength_to_rgb(nm):
		#from: Chris Webb https://www.codedrome.com/exploring-the-visible-spectrum-in-python/
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
	'''
	Copyright (c) 2001-2002 Enthought, Inc. 2003-2022, SciPy Developers.
	All rights reserved.

	Redistribution and use in source and binary forms, with or without
	modification, are permitted provided that the following conditions
	are met:

	1. Redistributions of source code must retain the above copyright
	   notice, this list of conditions and the following disclaimer.

	2. Redistributions in binary form must reproduce the above
	   copyright notice, this list of conditions and the following
	   disclaimer in the documentation and/or other materials provided
	   with the distribution.

	3. Neither the name of the copyright holder nor the names of its
	   contributors may be used to endorse or promote products derived
	   from this software without specific prior written permission.

	THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
	"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
	LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
	A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
	OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
	SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
	LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
	DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
	THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
	(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
	OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
	'''
	import numpy as np
	from math import factorial
	try:
		window_size = np.abs(int(window_size))
		order = np.abs(int(order))
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
	#from peakutils
	#from https://bitbucket.org/lucashnegri/peakutils/raw/f48d65a9b55f61fb65f368b75a2c53cbce132a0c/peakutils/peak.py
	'''
	The MIT License (MIT)

	Copyright (c) 2014-2022 Lucas Hermann Negri

	Permission is hereby granted, free of charge, to any person obtaining a copy
	of this software and associated documentation files (the "Software"), to deal
	in the Software without restriction, including without limitation the rights
	to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
	copies of the Software, and to permit persons to whom the Software is
	furnished to do so, subject to the following conditions:

	The above copyright notice and this permission notice shall be included in
	all copies or substantial portions of the Software.

	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
	IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
	AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
	OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
	THE SOFTWARE.
	'''
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
	#compute second or third order polynimial, and generate wavelength array!
	#Les Wright 28 Sept 2022
	errors = 0
	message = 0 #variable to store returned message data
	try:
		print("Loading calibration data...")
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
		print("You MUST perform a Calibration to use this software!\n\n")
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
		print("Generating Wavelength Data!\n\n")
		for pixel in range(width):
			wavelength=((C1*pixel**2)+(C2*pixel)+C3)
			wavelength = round(wavelength,6) #because seriously!
			wavelengthData.append(wavelength)
		print("Done! Note that calibration with only 3 wavelengths will not be accurate!")
		if errors == 1:
			message = 0 #return message zero(errors)
		else:
			message = 1 #return message only 3 wavelength cal secodn order poly (Inaccurate)

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
		print("Generating Wavelength Data!\n\n")
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

		message = 2 #Multiwavelength cal, 3rd order poly


	if message == 0:
		calmsg1 = "UNCALIBRATED!"
		calmsg2 = "Defaults loaded"
		calmsg3 = "Perform Calibration!"
	if message == 1:
		calmsg1 = "Calibrated!!"
		calmsg2 = "Using 3 cal points"
		calmsg3 = "2nd Order Polyfit"
	if message == 2:
		calmsg1 = "Calibrated!!!"
		calmsg2 = "Using > 3 cal points"
		calmsg3 = "3rd Order Polyfit"

	returndata = []
	returndata.append(wavelengthData)
	returndata.append(calmsg1)
	returndata.append(calmsg2)
	returndata.append(calmsg3)
	return returndata


def writecal(clickArray):
	calcomplete = False
	pxdata = []
	wldata = []
	print("Enter known wavelengths for observed pixels!")
	for i in clickArray:
		pixel = i[0]
		wavelength = input("Enter wavelength for: "+str(pixel)+"px:")
		pxdata.append(pixel)
		wldata.append(wavelength)
	#This try except serves two purposes
	#first I want to write data to the caldata.txt file without quotes
	#second it validates the data in as far as no strings were entered 
	try:
		wldata = [float(x) for x in wldata]
	except:
		print("Only ints or decimals are allowed!")
		print("Calibration aborted!")

	pxdata = ','.join(map(str, pxdata)) #convert array to string
	wldata = ','.join(map(str, wldata)) #convert array to string
	f = open('caldata.txt','w')
	f.write(pxdata+'\r\n')
	f.write(wldata+'\r\n')
	print("Calibration Data Written!")
	calcomplete = True
	return calcomplete

def generateGraticule(wavelengthData):
	low = wavelengthData[0] #get lowet number in list
	high = wavelengthData[len(wavelengthData)-1] #get highest number
	#round and int these numbers so we have our range of numbers to look at
	#give a margin of 10 at each end for good measure
	low = int(round(low))-10
	high = int(round(high))+10
	#print('...')
	#print(low)
	#print(high)
	#print('...')
	returndata = []
	#find positions of every whole 10nm
	tens = []
	for i in range(low,high):
		if (i%10==0):
			#position contains pixelnumber and wavelength
			position = min(enumerate(wavelengthData), key=lambda x: abs(i - x[1]))
			#If the difference between the target and result is <9 show the line
			#(otherwise depending on the scale we get dozens of number either end that are close to the target)
			if abs(i-position[1]) <1: 
				#print(i)
				#print(position)
				tens.append(position[0])
	returndata.append(tens)
	fifties = []
	for i in range(low,high):
		if (i%50==0):
			#position contains pixelnumber and wavelength
			position = min(enumerate(wavelengthData), key=lambda x: abs(i - x[1]))
			#If the difference between the target and result is <1 show the line
			#(otherwise depending on the scale we get dozens of number either end that are close to the target)
			if abs(i-position[1]) <1: 
				labelpos = position[0]
				labeltxt = int(round(position[1]))
				labeldata = [labelpos,labeltxt]
				fifties.append(labeldata)
	returndata.append(fifties)
	return returndata


background = 'iVBORw0KGgoAAAANSUhEUgAAAyAAAABQCAYAAADhuhE0AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH5goFFDgj33B8iQAAAB1pVFh0Q29tbWVudAAAAAAAQ3JlYXRlZCB3aXRoIEdJTVBkLmUHAAAgAElEQVR42u2deXxU1fn/P3e2rJM9kIQEEgKEEEIgrEkgiNSq0C+i2BZBlOKGWrTWal1a/epXbf1ZtOJSpWqxImoFXKkoEkzYZA2QhYSwJWQh62Qyk2Uyy/P7IwuZmXvvzISEBHner9d5zcydc892z73n+Zx7FgEAgWEYhmEYhmEY5hKg4CJgGIZhGIZhGIYFCMMwDMMwDMMwLEAYhmEYhmEYhmFYgDAMwzAMwzAMwwKEYRiGYRiGYRiGBQjDMAzDMAzDMCxAGIZhGIZhGIZhAcIwDMMwDMMwDMMChGEYhmEYhmEYFiAMwzAMwzAMwzAsQBiGYRiGYRiGYQHCMAzDMAzDMAwLEIZhGIZhGIZhGBYgDMMwDMMwDMOwAGEYhmEYhmEYhmEBwjAMwzAMwzAMCxCGYRiGYRiGYViAMAzDMAzDMAzDsABhGIZhGIZhGIYFCMMwDMMwDMMwDAsQhmEYhmEYhmEGEyougr5D6xOKxZOeRbRyFhR1sWjT+aDFoICpVYDgDSh8bFAHmaEMaoLFtwY6ysOZxmwcPr0ZhpZaLkCGYa5oYkMDcfuU0Zgb4YdYwYRQQz28jHoIBiOENhNI4w+rxh+GgHCcUAXg67pm/HX3YViJuPAYhmEuIwQAffrkJnwLQNmpbbo+FQ6fPb8rQWoFbFolLFpAN6QZBb4n8FHdRrxbsO6yKMRA33A8MmULrIcno82ogAWAVcRJHbcpCeEJRiA8H2uz07lWMgxzxTAvORYPTR+BdNt5+JwrhmCTeVhanB+mlrBIfDlkNH61dScLEYZhmCtXgHzXKTwUEiJEKXNMafe7Nd6Cfw5Zhwf3PjRoCzBj1I24qe0TNJWrXYoNCwCbeBva7b6BwLWSYZgrBrpB5iHp+EC1ST9cDfGJmFVSj6PVNVyoDMMwV64AUbopNhROwsPRX+W0GkzKn4yalsHVsEyIzsRyUxaMtUqXbzkc/+tqZx2PswC5xJwl5+raVQW1fC0YcTaQ2JOqw13L1cazNmMh5N94SD0sRQRL27A4TCzTo7i+gQuWYRhmENMPk9BJRNNQp9ZBj/+EHp+Cgyay9xe1PxKFYwqh1WgHVeHdE74JrbVKp9QLEqUipfzYXhmMVhEXAcPV5JIXoth3qaZDBO+yM/h24hguU4ZhmCtPgEDE1JZrTcit80KOhOK/ad8OmoK7KeVBGHPDJNtSKSEiJ7WYQYLAqpDx7OkG7kzom/tNAEihQOXIaVgTnIb0qij45qow4nQA/qCdiMqx08T7t3p8H3HoRywfP47LlWEYZhDTD6tgOVpvBPn3Au6MAus4d8beGZgaOQ0HqvYPeMFlBCyHWaT968pl0JTzKFJ8gNzKr3GuvgDNbY0I9BuKUG0MRg3NQJR2OgKsqdCfiYWuihcjGzDIzWMMI/JUIq46fXMPdhbcudjpWJ5dhaxt9s/4Ml0TVu86gtUAPluYiYWFOdKKj4D7I8OwLp+LlmEY5goSIATnYVgXfgtItvPtpdQgKSwRd8Qvw4qqxfA+oxRpyqmjnWkX8PjoJ3FT1Q0DXnB+5xOgl2j/vGbvwZ+zM5yO64yV0BkrcbJqn93xcSOuQXrso7CUzwROcaUctMKEYbiK9AvmkGg8eDYI/1i7z6XfGz/PQfkN0zAsb7+kMhxXe54LlWEY5soSIHLjV5ybbJO1HYerj+Jw9VE85fMCzo49Bv8iP8kw0gwZg6Lg2us1djnuybvHlnsUVmHpNhSWbut7keQXgdSUZ2FqX4Dq2iDU6jRQqghhQ9oRGVWO9pb1OLTvORBZex1H7Ph5iJm4HObA6ahtD4fBqkFjmwIqLyDI14JA3zaEowgtJ79G7lcvwmoxXVSeYmdci5jrl8MyagZq/YbCIKihF5QwKwBvFSFEbUEImhHQUAZb8QGc/XwdKg7uHnQ3XnjyGCT+773QX5WIBn8F6tRmKMiC4S3Aca0LgS0ImPDbGxB842Q0TQhCg9aCJlUbmoRWaElAgEWJYKMSQfkG6L/Ix9FX/wuy2volH3HXj0HM8wmoSKxFhVclbDBjiCUYw8sj0PJGI46sPix5bvozU+C/XIXKqFI0KevgS94IM4ci/HQ0zr9twN5Xj15U2lLmxWLa8hiETzfDFl4Lq8YAs6IRGqjgbQmCT1sgTEXhKPq6BZtezIXZZO3V066/xMh182Jx2/IYpE03Y2h4LTRKAxRoBCwqWNqD0NYciKKScHy9tQUvvpILU7u1z9OQPCoc/3tbIq4aoYe/pQHq9jqQRYEW9XBoVx7vkzjOjEjHzH8fQ2VjudvnvFzbjtVSF4QAL109t+4MwzCDmH7eB6Tnvh8da8QImCh7/sMTH8DfjjwLsaWJLABMw8zwr9DYnVM6zgBVob/Toig2AHmzs/Hr7KvcSvtrs79DZPY1oguteCe0YFmxX7ff1UobLFZBdGndj8Mn4GxtXr9dtESQ5KpbNZ0m0ZyZ7+N43q1o0Cu60yi2GNnYsc2A8R4U5X/oURomXvV7CCMfR255mPgiZiKrMA8LMWOk/lPsXrscNqvZs/gWPwxh/mPItYaJr9rsGF/PY+k9JOIxcrXomsTCbQSnJXqEAJEb4DQk1woVpkChVmHW9+9hz6zhMAtmJz8KssKmuFlSeKS//TucXzYWp70NkF702f53rEmL6I9qsPvOf7kvROgqOK/b1rkOqpAHQSkgc9sN2HnVMdi682GB47JE08tTcXTCIbTp2rqDHnH1cAz5TIuSgALZRbrHV0zHt6l5MNa0eFRXfv77iUh6XEBdWK7Ldfi6XKB5GKo+HYlXl++G1excRm+TeHVxq+o4+E12MVHkgd9PxMOPCwjvkX4lIL2UngUwW4bh0y0jsfz+3TBbXF9j2iFdfYSbAbVKge9fnoVZgXsgmM1OfsmmgOJh24A1XNGBWpwLM0guPUhQQdFo4RaeYRhmkNKPk9AdV74it7TOv09scDjHHnWD80ubTUEfiCoqAjCuOAMqhdqtFI+snNkdhqNKOxH+lX06/ElUwQkAVozdcEkVpL2NqsTPZx7HgV23Qa9XiPrpeXLRST+c1n+AKRlPuxWfxkuLWcuP4QhWI7c0TPrSi/yu0KuxU7UEE/63CiHDEtyKz1sbjJlv5uPI1X9DrilMPi7HdQ0EdwoMrhdu6/Yo9OKK9Kgzfj6YXLYN2ZmxMAvic6Ok7pDgUdGYfP5d7LlrJE57t7odJwCc9WrEruVKTDz/GIJHR3hw/4rln6BQKzDl3AJkz8mDTbA5FKD96nb7og9gZOlo+Ib7dojnW8eifZsBRQEFsnkmAIXD9uHqkjho/NRu1hUNHjg2C0Grj+B8WK5T1ZCqDgKAZnUFgpfsxCtVExCTECLpT7jI3hs5//5aDfYem4VnVh9BcFiu6+rV47taqMCS63ei6sgEJIwK6d1DpPPTz0eNsvWTkRmcDYEkOgoGeMO/5nazbIGS/+BaMZFhGIa5JAJEuIgzBUmDT5AI+k8HHgHCrKKx03kVfpv6uMt400Zcg/YSH9EwlF6Ed/IeszfEI9qcDJuuT+PO8Xg2wYhVs/6D1Nh56O+1cXqW1LUzD2H/rrHiMYoZ2QS0tws4cu5ppEx7UDYeL+9AjLmxHDtPJotfbnJhnXX6O1IXCt+78hAakygbn09AKOL+XopdSJK2IOX0gTs2kqs1Enpdt50DnX5oEw5EaDy+Z4JHx8C/4HkcGtImo5YcC905vNyw8/ArWIyQhMhedih0kHFgEQ5EHofrdVE7/i/UFmLKlimInBaJxnW10Ct0Li9d1+8zAQW4cUu6y9T5BHphRfkYVCTvlEyRq/UGCIAx9AgezfPFiMRQj86FjA52h4BAL+SVj8HoHuknTzLQmeFQvyPI+8YXiaND3bukIgL+0NrpiLAecLfPaEDIGBEl2y/QNCyGW3eGYZgrT4BImQCujbflCUsdWkb7FtAc4vxavcXcjMNJu+za1J7t0i8VK13Guyz2j9LtdOpZVOnP2h0zDi20W8PLsSNdX+wHxc5fIv3sFjzoZ8GTyY14dNYR/Gbmv5Aav6DPS7sr3gM7UzwzlTs9WSwCaqwvQRsYLelx0s15yC8LkF/QDC5ESOfxcoMakff9CLW3n3hsCiWS/5aH481a9yw7ciM9rgqGXIgqj6+I/cm7EkJk7gsSjU7l44WY/X/BOU2bGxeyZ80XV1blah2G/bgEKh+1G+E5rI/aGebOlAKRgpSvbbun7EbwjgA0KOtd6lRHSjP3IyDKXzapK/ImoTIg323tSTI5aFWX4/EfI+Ht5psXT55yoldfAHblTYKvQ/oFqfrsYi1vtVCOHzdHws9X7d4ldiiMBM0uNzIxsMpkVWKMbOHuCwjm1p1hGObKEyAkYxVKE+oTgqdaH5FsVQiAIVwveu4fC1cBKnIa9AUAvociMG5IimzcceXpkjuWfNf6upP/T8r+BEEgJ/tAzG5tb1agNi8Q9TtTYNu1HONOfYG7wy14KOMErp6wCp6+IXHH98Qp5zFmwiqo/SLh5TsU48evxPRpFdLigYCqajUmXbVRNLy0+Wvw4wnpXsXkaB3SVGsQdTQd6i/84f1FCOILF2J2wHb4a8THiufrApD2W/G5J2n3v4H9zZHixlan0eSrJMyu34Ox7yyD9q4YaH4ZgMhHZmDGtlcwo6UUSldGkuCGYBHgUR2WP1lO+UgsurDucRwLanOQ1j1CJCBznwLD534OTcBqRM/+CrP3ekFBUq+lBOQF1SDt/dt6cU8LMvc1yebfKlhxwrfYbZ3Y83ib0Iqrn5eeO7ZoTRrKYn6UjD1cl4yWNWnYnh6Ftf5qvBPijV0L46HcPhsqm79o6o0B+Xj0wzTRXLrKPUmIK6ma85c1aQgVSX/XOY26ZKx5LQ3pM6PgH6JGSJQ3Fi6Jx/bds2Ejf9GTAjT5+PC1NPcf1WIJFCQuygC/FYnQ+uHq6mLpLHl54Y/HjoNhGIYZvPTDJPTvOnWN2ER0BQRMsvOvVqi6l+G9s3oJvE979zjvwtRNghI2AF9kfoFFOQtF4z6Ydgahe2OdJqJbAByZ/S1+k32d6Hmz4q7Ho2f+6zSN1gpAGW3G0nIvkEgxvZR5GOacSaIT0bvmQ9p6hGkV8WcDEDqmBad8/4ztR152q4zHgWSnHafOyse2ncmi52bOOYicHydLThoPCLTBciYCLc213ecolV4Ydl0Tymo1ojNvM6O+Qs466bc60YmZsMzbjvMtKqdzQ3ytaHslCi36mm7/Ko0PIl7Vo7xNLZnOaF8zFC9eh7L9WZLxRk1Kw7CXN+HAnCjpwjxLzpPYu1xAL4bO0RnAqUbYzxrW2gipPxSh8s3/oHL3IZibWxE5YwJibr0OjQsnIj+wYxUsr0B/BNatRY2qBU6zbDvDnvVxLXbe8jenZMzc8FvsukUJqQnxQyw+0Id9AJO+VSIfV4nUrh75IhtmFo1D9VMnULbtFHyH+GH8c5Ox55dHYBXaITY7uOdlTCvOQMWfa3Hmu1Joo/wx9cUkFP5iFwTBJjqxe9zJdGwYvccpmSovJW5pGgadpkx0DQLtV5n4x4Icycs1PjMaS7Zb0K467xSnrzUET0a1QScyCX4DiU8wVwK41oNqo/FS4kTTMKgd0t/19Pvuq0zcKJP+zIxobN9kgcp23qnIrdYQRGW2oabOOf12k9CtIlXWAtgUWvxQlYo3v6rE7qOVaG4zY8a4SNw6JwYL4xsRuHJgNtoouHkmxuXtklx7IWfKbMz+Nptbd4ZhmEFMP7wBEZuMeuE4IQ+EQhCKQTiJdlsJcmu24Ld7b4X3abVDV5tgr5S8CH8teUEy5r83PSeZmuRTc3rML7Fn6fA/iHYAEoCq+BxR8QEAT+7JgP/0Csl+bsfRDWIT1glAzQlf+B75G+6cvcOjEnbsmASAiCgzcvbPlDx3767ZiI6WXoGqyahASvpTdsdSZj6EsvMaUck6I65UVnwAQPnxHMRWrRHtQG8wKTFhkf38mgk3P4zyFrVkD6wKBN+3lsqKDwCozN0rLz66wuzzHl1B8vsIkwD/tPuQPfcOlGz6Fs3n69BuaEbptr3YdfvT3eIDAFIeuRU1KpNkDUho0YqKDwDYtfR1jGkJgdRbyBqVASmPXOthwVwYhpW5ZSx2jfsMJRsLYNK3QVdSj52//g4ZhydL5P0Cad/Pxvaxu1H06QmY9CbUHa/HNwtykHJwpl3MPVPQPKxWNKw5D6WgXlMmmvLI0hmy4gMA8nPKcXJNrOh91a5swOLHJnh0tT3l3odSoBBJPwCUl86QFR8AkLO7HGveixV9MCjRgMfun+Be/XdYvcPkNQJpz/lj7u+zsWlHCc43NMPQ0o5tB0tx+0u7Bkx8bL4xE+MKdknes4Yxibhu++BbdpthGIbpdwHiqqkWWzHHPfbN+FF2F/T1Be/CnGgUD7VcgzsmPiR6Xlx5utMQawIAgfDeiSck42u3tOLBfTFozfwaKj+baE7FzFHxlXQEVGZfhVszN16U7IsZvRMmk17Sn9ncjPjh2bJqSek/x+4c/8hFkurHWPiiW+nL/2a1s1rqRDVmnn18E2+UrT7T6AxObPu077VCvwjxCwWmIgGqXz+Fqv3u7W/h9YtUGXEvYOi35bLRR2zTyWbYa/5wFwUj/oI0oWU4chZ8IS5gP6qTVXZxbSOxY95O0XNPr66WTK1B0yB6zohF0nNDDr1odKucP1+dL1kVkuep3LrSvdWx8zrTL9aJ8bKb6V+9RloMzJulcl3/HaYMkaDCr19TYX9B1aBqrDYtysTCkhzxjgkCzEOjkHayFq0WXn6XYRhmsKPqv6DlVuuBiBCRH1ndMLEB1++91mWsXwSvx41YKdqoL/Z5AO/AfphTZuw8WE95ixoAmtQ6FBza7yKXhBdy/gfDQxOxbMoa+J/KhL5cYxe/WK6lxr3r9t2EqLAkVNYVuLQZxDREdb1rAVNftxnAz5ytp86Aapti7fzXtY2FlLrK930TuP5N8U0Revw2KqUzXq20N4Tr/McArZAcXG/e/WHfVlN3V9i9SHUz9awee79wf8PJ2vggAM0i4XUUTN2Xh2TPr/v8KHBDkuQ9VzvKXRFlz5CvNSiWsLZr9lQ51FL7t5iR26JRbD4tem7J1rOIlCi9FoVB9Bzb2DrJkh/2Zj6Wvym/R0fHp1FyXQPN8Gq3r3RvqlBcZ/rFnpYvv5mPNW867AMiuu+FseNT5NINH1Lt8SP7rHUqvsjeO2gaKQHAnlsyMeN4jqQHS9gQXGNQoqC2jlt1hmGYywDFwEUtuPG741jltCoknkiEod3gMtSnD/yhe0leR9s14NBwjAi2t7puG/GIpDDYpVzndm7K6o/j+exr8GS5F7Ji58M86z8ISSuFNrrd5ZKgPf83mwRck/SKx2ZhlyYoq8xymdaq8h9kA240eNkd1vX8LTayTm5uslTie/ynb7dfmlZn8ZJ+SSYA53K+7H+t3Cf12z5Q23++9yiERm+bbIFW7ZIfBlO1u0jiHuvIsN671Q1lBie5W73xrHSaTzbAWdleOFL7mbSBaNKboCSV6GUxC+2i5zR76WQFPSA/z9pxBJJjrq0avcv7UHAp2WR6gLx0op0V5E71EiA//58AjULv+hHs8DD6z96B22DQER+1CiW3pmPGiRz726pHoVvCI/CLFl9knz3HLTrDMMyVLUCEXvzn3N3dFm/Ca2n/wLD9MahpqXEr5hZzM/KSdjtImM52q13Ao8kv2fkfcW6GqFGhDrbhndxnepX7g2f/izU7f42n9sbiL+Ve2Bw8GnVTnkZQ5o8IjTO53LJCqZ/sls0sRpOh3OW5Bhd+9EalgwBRyasnuRF1blhkDSb7aqgzq2Sriu5cyaXXx30QUPlX2z0TIEqbRFgdNchQUSt7vrGyQTY9OmWLGwLKuSCq9pZKi4gmk4RS7aByZ5WLem0T6YKQplmlc1nyLlattZNbjstqWxQNHmlYT6uNQqVzWe1ITjhIjZTr/E9ha3D9EHEYhvnVznIMBsL9fVH66wmIL9kjqe3bo0Ygs1aBb0+d5dacYRjmMqIfhmBJLUop3cySimDTAlatFQ1DmlDoV4KP6jbinYJ/Aac8T8Gfjj+ATapckMV5l+nU8gsrYc2NvwHWU97ixl/yEbTlNPdJiZzXncTmg88CeBYAMD/1MUSceR4GncLJ2BIANFYE9qvNTGRz57LI/++qe1lwYUH27MG0Ce5nsL+WAO3NJoYeBtpQdPIiwxCbni1znW0kE6YguSiDdIF3fDdWNUmeYTVZZS+YvlQvG6O1cxUsqSrmbrWQKiHy4CnWkR6LyyvTV6P43N1eR3J9AJHfgmDxOPKiMw0YaBKGhuDgnCHwP3VYUlwZY8di2rFaHK+t55acYRjmMqMf3oDIb04mIBkCxkFAAgSMgoA4KCzDodINg1fZMEQeHIO52fM7xEcvKag5ioappeKrTp32xuLxdwMAlkY/JGnTrq94tt8Kfcvhv6JxzEuS0q1Fr+i1DgjQRruMPyBguGy3cKC//YDyYK3F2fARZKwxx0+poVkS1mCw2uJsb/cwPIJjRg/iW0paybTWN3oUUpBVIaLmLjjtsHDZ87XRoXDeneaCC7L69Op+Jmvv90KxmW0exebqrYKfJVi2qknLL7i1IaK7e1b2dhSfzRIsWtWl0umWuO+tkO70W69vHdA7KHN0NI5l+sO/okiyYtQkTMHIH8tYfDAMw1ymqPo3+IHbseqNpufxJP4p2kYvC/wDPsZaxJVNRzuch2poxhmRXfhFv6ZvR+Hr+Bn+aFdSXfErVAS0y5eqlA0yPOpq1DcUy8YdGX0V6k9LBx6kNaHaToCYUNUovqtyeMEE1Fbk9WnZBKlMqGpX2xtbPdIXM2sBzh8/OEirqqO66n2/eFCbAuf9xUzrju+RM8dDd7JC+jpnjIVOcllsILDNB1Vu5ediC0e4qBKUi93XFIwmdZXowgzZE8JxLq+232UmXcRVtpiCoVJXiYY7bUI48vsp/bJqagBZPCUB64fXQ1lbJzm/rChpJiZu3guT1cotOMMwzGVKP09CH7jW7MOCd2AeaxRNReDhUVg8/h5Yz3g7pVQAcCTkM5fhv5XYhHvT1kCj8ulV+oYEjpS0A/xDrC5LVay3lAAMDV3kMu7Q8BulLTwBCA84a+c/zKdYPAEARs+4t8+vXbjxhGzm1TOX9k9VdXsGsDt13tXkGDfK4ZT8G5OwBfJzhcJumADx1QI6wz/pjvDoi3uYLuqpIZcCVXGYqF8CkHnvYH5T1sHZ4jDJlxl3X6r0X8ws+j7k0Wsm4cPIcij1dfa3UI/07UicjcRPd7H4YBiGYQEiZ2z0lQHTO7aGfCg+DrxVwH2Na0RHDSl8CG8eecxl2MbjWsTuXYW/hjTh/zL3YO7Y29xOl0rphfnR6yUHq/mHGXqd54qTmdBotNJxq3xwumy27Bhyq9F+Q0Rj5SbJy1rjuxwqde9EWMr//A7JLzqPNzce+czZDu7xe78iDqPn3twndUTZM3CHlwRKL6+LrP8XJ0JMXx+WVUvVPx8me371NSEy6RNg2lLmwirtq0k3Qq9Lz6UBv8loV016nh++vAYan9695L3pdylY25Ask1Cl6C1B6Njd3F3+u8noNMqw6/uty2vg08v0/+7uFDTkJnsmOvptOWrXvHZzGv7qnQeFqVk0naRS4r2YDFz9H97hnGEYhgWI2yJkYLrVnjnwMBRhVlEZZC3XiJqGrZNOodZY6XYcbTUqUE4aZhW9j79EmvFCegkeytyI68bfi3HRmQgLGA6FoESAbzhSR/4CK2Z+gFVxOlT+GCNp8lkDD7hVumLDQCor1LhquvTuyemZP+DcOY3IEmEdnwH+NhzdYz//5dievyNmaLuzXU3AyWofTL7jBHy14W6Vl19QBDLu/CfGP9eIo2NfQV5jsJOfYxtXI9rXLGkUWWwCWu/dgJgps2XjChudhBnbymT9+MvUzdhrru2jewC9ugeOvrQeQyxqSauw2K8ZMz/4veh/M/99H4r9dJIdAUOsWhx96Vs38iD0WkD1xVPE1fyKH/5+DKHtMaK2c53PSTx0YjICwn3dii84wg+r/pmBNxrHI/2Vo2gOlh5aqCR/0RWpAWDmtbFu5/Gtvx+DrT3G6RkAAF4+J1FwYjLC3Ex/xBA//POVDDQWjscrDx9FsFeeZ0pvgN5+fLEiE/eb9kKwWESHXNo0vviz70Tc8RXvcM4wDPNToR/mgAgiRsvAdKu1mJtxPGk3RmVnivZWirW7Xxpf7VWOAaC5SgVb1SioMQpJWISx6LFvWAtgPd3h6uRkmkA4WPaqW/GJ9bULAPbvnIjMqZXQtz6HktMbARDi4m6Av/Yp5OyK6bjqYl2uBEyMP4icfPtx5xZzK6KFt3EOq0TTs68sGkMXVGKqbzbqij5C+fHtMOgq4BsQjqCh8QiNnYyghGvREpCCPGMEdpMA6KTlr6W9FcOL16E89i7JmcHlJjV8/5iF2fV7cf6L11F+4Ae0NxsQEpeA4T9bCK85N+Ng+Fj8KMjXvXCLCXqlj2gXuvbtf2HMgytR+t13MDXpe1krem/ZmfRGJGwuQc2voiWtxz1Lw5EZ/3848/inOH/wBIamxiP+rzdhZ1prZ83racZfSFvCZgt2ejTZ+OKtU+rlOXId8+ZWC1rfjgatEt8Dojp6H5ZXDoUieyqOfVSH/O3lqK8wIDDcF5HxQRg5ORTjrw1CWEoLTBF5IGE3jOjc+E/uwWkKh8VHL9oh8Pi/tPBeOQY7vyuFQW+S78BoteDjt6OxrDP9jmUUFb0PFZVDsTN7Kj7aUIft28tRUWlAeJgv4kcGYfLEUFw7JwgpY1sQEZAHwbb7wkPH3erZt5fZYxY05Dh1bPRMp8LUgudaDuG5iXDYgBHOmzJaANg6PgUDGIZhmEFKny9sSvgW9nsP22+JLWDSJc1g0pCJWN9wGFaL4Ng+werwXTGiHfNL3Rt2sxok1/ZJb1os0/Tm0mIAAA1tSURBVG5aAcRkFGPt7rGycY8TiVsq/p7HSeyS9NgWOjLKAuPJOBj05aJVZfrSUuw7E2O/lbRS9nJLH+u5JfVfRFZLUygx5c1zONAeKR6G45bWcvGkS4uQjD0nsDt6tGh5OIXXs1QFiV5pOitx1S2AMMXzHgIfL4yrfBfHgppd1Kqex7pqgXiNSG4MxfGoNbC0mmVu5Kuk4xNcLDpAwT3OuXCuEoDVRV/ECJIu/kMySzrfVzodlTH77C6hVBWRq46O/z0kEee/T2RAM3q3nX9Xt4QCQKpIeIIAHCmdjqGd6Zeq5i4fJCKXWxgncYl2dPq1Ol8q4eZL2wjRQg8eZFaHh7fUcRYgDMMwg5pLMARrYCmoOYKmqWV2iksqpSdjszzKoTuTZd0dVi0AGBLXhs8Lf+F26Yr1sU+ZddT1ZmYi2z6rVIQhyj9IiI+OEHI3JiF5hE48UMFFIXi47wjZrMh/NBmJfgbxl2py53tQ/Uyfrb9wDqGf9gPpfSCWVhPOTXscMe0+LmqV2Ds95wKKNgehYsYGefFx0Wnv/bJKUsVPLqJ7LykXUbpklzsQ9fyPenmvAkDOepPYaCG5Tcml00JARlIuWnTJTksGkNz55OaDyZ3L1FebmVzsbeLuEmgCRJfo7te9ghiGYZjBLkCEQZXJtYYXJIVBd4OvILx5/DG3w/SNNru10Rm5WUIRY43Y0ZKBGt1Jt0pXao+Eb3dNxpSZxR4pGI2GMHH4Mzi6X37oV7vJgKJNMciMP9ARiNRapO4YAG74aW2qx5nfjcBMFLpnifZixN+hl59Hkqmpj21woU/vB13JORiTnsDkWh8PEum8Td6kuiFoTvoYDcVVvcjPwN3T7tjUbYZ2vBtThKgDmRDo4uNzxXvPH4KqKcmtW8wd295oaMf4mCLkHcjsvrVIKv9ye/F4YoBf/EJt/dd0CBJCQ6oT4mI2Y2EYhmF+CgLkYvYf7h8+zF8L6lyS1zFV3SlLrUZxzVG3w7yvXIOscb+BIvMg/ONMooaCOzs4B0WZEZz5Od47EYKy6sMet9WOC9gQWbFt11hMnfkR/Pxt9vaFSCOeEN+MkUG34eDuZ9yK09zejJz3pyHJdDemx1VAoSB5a1FUFBDGBLdgtiILsdvmuzAsddh1XxImZT+KSZo6z9Wei4tAVitqb5qNcSZDr97UQL5W9Z0IOVmOQ0NXIP2fZzCyzddFQdsfH2EKwsx1FhyJeBG6kvO9tAQv5h52X8DI2ZquMDWb8fq0HJy/OwmRFdOhIIVsNRDdY54AbcsYtGbNxifzYyXjslkJT8yuhdowzqVgcjcPLc1mzJmWg4fuTkJ1xXSAFK71rcMekwSgxToGWUdnY/6qWM8e1YPBgHf1allwcUEH+i0OwzAM47EN20ftx1aID9gfmDkgXTyf/hZ+tuceySHUW6e9gDX7n+x1+MNDEzFn1HKM8E6Dt2kEbLowtDZq0NaiQGuzAEEDKP1tUPpboApvQKvvCRQ1fobvj67x+BKMA0nOI6np0fpqtdGYlPJ/aG2dh+raINTWq6HUEMKGmhEVVY72tg9xaO+zIOr9mvoRI6YgfvpKCGEZqLPGQG/WwGBWosUiwNuH4OdLCPY1IVhVD29LGVrOZKEkZx0aq0/3Kr7YGdciZt4KmOOno9ZnCAyCGnqFEmYB8FETgtUWhFIzAvTlsBXtx9nP/4WKg65Xz1Go1JjyxNNQLVqCqqgo1GnUMKoEkEroMQi/x8B0yTkgZyA5gL0Xc0DE71oBE367EME3TYY+OQANWiuaVG0wCG3wJwEBFiVCjAoEFRig/zwfR1/9L8hq8/BGvgqiA+s9ngNyIf8KADY35oBIPT0OeWhYjpwSgVkr4xGZIUCIqYNVo4dFaYBNaIEXecOL/OBrCoaiPhitZd44mdWC79eVoOq0+zvWq9QKrHx6CuYsUUEbVQVBXQcIRqgEEp0HMsmDPKROicA9K+ORkSEgNqYOGpUeShgg2FpAZm+QzQ+mlmDUNwSjrNwbWTtbsO7DEpwudZ1+2uF8WbvnjSy6tM/m7jkgUhPmHB9yFhf/d+ZLaOIGnmEY5ooRIIMVP40WP/g2wtyocGrrEGbFL3R+MFtNl0VepASIFUA1d/8xDMMwDMMwgxjFlZLRof5RoGbBTnl1UTXu4GUjPhzVI8sNhmEYhmEYhgXIIOTF8etAZkHEgCe8Xfqnyy4/Yjs/MwzDMAzDMAwLkAHEW+WDjOFX45PZ2RiZM13UeLem1mFv6feXbR75DQjDMAzDMAxzOaH6qWXomWn/D0v3P9IxJ8ICWMoAa1nHXEtHo10A8I7p8csuj45LfDIMwzAMwzDM5cJP8g2I44KkYntmCACa009hU8G7l2X+xPYXYDHCMAzDMAzDsAAZYKR2RlaMbMOdxzJ/Uvnj4VgMwzAMwzAMC5ABMsrF9r/reltgS9bhN/pU1BgrfxJ5ZBiGYRiGYZjLhZ/cHBDq8dk9V8KboAizoDG6Elus/8bfDzwNuswHLAkOeWUY5sqGqONJIAjCJTmPYRiGYS7WZmfHjh27K9J1cSnjPH36NBERpaSkdB+LjIzsTsvIkSO7j0+YMIGIiE6dOtUv+XDnPHfDTklJoVdffZWKi4upra2Namtrad++fXT//feTUqm087t06VIqKiqitrY2KioqoltuucWjcDyJix07duzYDS6nYP3FMAxzacnKygIAzJ07t/vYvHnzur8vWLCg+3tmZsdctR07dsiGKQjCgL/FWLt2LY4fP4758+dDq9Vi0qRJKCwsxOuvv45//OMfdnlav349srKyEBkZiR07dmD9+vVIT093Oxx342IYhmH4DQg7duzYXXZvQO688046evQoGQwGKiwspPvuu8/u/+nTp9MPP/xAOp2OmpubaevWrfTzn/9cMrwlS5YQEdHXX3/dfWzz5s1UW1tLlZWVtGPHju7jn3zyCRERLVmyxC699913H5WWlpLVapXMx4oVK6igoIBaW1spPz+fli1b5uSvi9tvv52Ki4uptbWVDh8+TGlpaXb/98ST8g0ICCAiIqPR2H3syy+/JCKi0aNHEwAaM2YMERF9/vnnHoXTGz/s2LFjx25QOC4EduzYsQCR+n/lypVERPT+++9TQEAAPfvss0REdPfdd3f7OXnyJBERLViwgLy9vWnWrFn01VdfSYYZERFBRERNTU2kVCpJrVaTXq+n9957j9566y0ym80UEhJCAKiyspKIiCIiIuzS+95771FAQIBkPm6//XYiItqyZQtFRkZSZGQkbd26VVKArFu3jgIDA+mWW24hIqKCgoI+GaZ23XXXERFRUVFR97HS0lIiIvLy8iIA5O3tTUREZ86c8Sic3vhhx44dO3YsQNixY8duUAuQgoICIiKKj48nABQYGEhERPn5+d1+6uvrqa2tjSZPnkwajcateLvCTUtLo7lz53YLmC4jetmyZTR69GgiIiosLHRKb5cgkcrHsWPHiIgoISGh+1hiYqKkAImKiiIApFKpiIjIYrFctACJi4ujkpISslgsNH/+/O7jra2tduEJgkBERK2trR6F46kfduzYsWPHAoQdO3bsBr0A6TKWHTGZTN1+7rnnHjIYDEREZDabaf/+/TRnzhzZeF977TUiInryySfp5ZdfJqPRSN7e3t1vQzZu3EgrVqwgIqI33njDZXodjxuNRiIiO0Hk5eUlKUDkwuqNALnrrruoqamJzGYz3XbbbXb/Ob4B8fHxkXwDIheOJ37YsWPHjh0LEHbs2LG7LATIqVOn7N4QSDmNRkOTJ0+mJ554goiIysvLZf3feOONRESUlZVFRUVFtHHjxu7/Pv74YzIYDPTRRx8REdGiRYs8FiBdb0BGjRrl1huQvhIgERERtGXLFiIi2rdvn91KX45zQLreziQkJDjNAXEnHHf8sGPHjh07FiDs2LFjd1kJkAceeICIiDZs2EChoaHk7+9P1113HW3durXbz6ZNm2jq1KmkVqtp6tSpRERUXFwsG29QUBBZLBYym81ERLR06dLu/xYvXtw9DMpqtVJoaKjHAqRrDsjmzZtp6NChFBkZSd98802vBEhNTQ0REcXFxcnm6Ve/+hXV1dWRXq+nVatWkSAIov4yMzOJiOitt96i4OBgeuutt8hqtVJGRobb4bgbFzt27NixYwHCjh07doNSgMit9rR48WLat28fNTY2UmNjI23ZsoWuueaa7v+vv/56ysrKoubmZtLpdJSVlUWpqaku4z548CAREbW3t1NQUFD3ca1WS21tbURElJub65ZgEjt+xx13UGFhIRmNRsrNzaU777yze5iYJwJk5cqVVF1d7VKsuaKn31tvvZWKi4vJZDJRcXGx3T4g7oTjSVzs2LFjx25wuZ4bajMMwzA/YZKSkpCfn4+ioiIkJiZygTAMwzADAm9EyDAM8xNl48aNSE1NhUajwZgxY/Daa68BAF544QUuHIZhGIYFCMMwDNO3bNiwAW+//TYMBgP2798PQRCwcOFCfPDBB1w4DMMwzIDBQ7AYhmEYhmEYhrlk8BsQhmEYhmEYhmFYgDAMwzAMwzAMwwKEYRiGYRiGYRiGBQjDMAzDMAzDMIOf/w/zpJ7quaBv/gAAAABJRU5ErkJggg=='





















