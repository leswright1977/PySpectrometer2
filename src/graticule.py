import numpy

test = [1.01,1.11,1.23,1.67,1.89,1.99,2.1,2.2,2.3]

print(test)

mynum = 2.0

#return closes number
number = min(test, key=lambda x:abs(x-mynum))

print(number)

#return the index of the closes number
index = min(range(len(test)), key=lambda i: abs(test[i]-mynum))

print(index)

#return both the number and index of the closest number!
all = min(enumerate(test), key=lambda x: abs(mynum - x[1]))

print(all)

#So, run the cal, put the cal data in the array. generate an array of ALL our data, then iterate over whole nums from our lowestt data point to the highest, 400 - 700 for example and draw our lines.

#cal data:

x = [175,296,312,342,402,490,604,613,694,1022,1116,1122,1491,1523,1590,1627,1669]
y= [253.65,296.73,302.15,313.16,334.15,365.02,404.66,407.78,435.84,546.07,576.96,579.07,696.54,706.72,727.29,738.4,751.47]

mymodel = numpy.poly1d(numpy.polyfit(x, y, 3))

print(mymodel)

px = 1669

print("Third order")
y=((-2.248e-09*px**3)+(-1.246e-05*px**2)+(0.3632*px)+190.4)

print(y)
#put the above model data in the array.... Verify R??




#Now compute wavelengths for range:
print("Now generate our data....")

wavelengths = []
#remeber we will be generating from pixel 0!!
for pixel in range(0,1699):
	wavelength=((-2.248e-09*pixel**3)+(-1.246e-05*pixel**2)+(0.3632*pixel)+190.4)
	wavelengths.append(wavelength)

print(wavelengths)

#Now pick out our graticule:
mynum = 200
all = min(enumerate(wavelengths), key=lambda x: abs(mynum - x[1]))

print(all)

print("print the graticule")

#Now get he pixlenumbers that correspond to the wavelength range (200 - 800nm in this case, so we need to calc our range rounded to nearest 100:

for mynum in range(0,1699, 10):
	all = min(enumerate(wavelengths), key=lambda x: abs(mynum - x[1]))
	if abs(mynum-all[1]) <9: #If the difference between the target and result is <9 show the line(otherwise depending on the scale we get dozens of number either end that are close to the target)
		print(mynum)
		print(all)






