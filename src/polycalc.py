import numpy

x = [604,694,1491]
y = [404.66,435.84,696.54]

mymodel = numpy.poly1d(numpy.polyfit(x, y, 2))

print(mymodel)

x = 1100 #1100

print("Second order")

y=((-2.181e-05*x**2)+(0.3747*x)+186.3)

print(y)


x = [175,296,312,342,402,490,604,613,694,1022,1116,1122,1491,1523,1590,1627,1669]
y= [253.65,296.73,302.15,313.16,334.15,365.02,404.66,407.78,435.84,546.07,576.96,579.07,696.54,706.72,727.29,738.4,751.47]

mymodel = numpy.poly1d(numpy.polyfit(x, y, 3))

print(mymodel)

x = 1100 #1100

print("Third order")

y=((-2.248e-09*x**3)+(-1.246e-05*x**2)+(0.3632*x)+190.4)

print(y)

'''
pixel = 174
for pixel in range(1101):
	wl=((-2.248e-09*pixel**3)+(-1.246e-05*pixel**2)+(0.3632*pixel)+190.4)
	print("pixel:"+str(pixel)+" Wavelength:"+str(wl))
	pixel+=1
'''


