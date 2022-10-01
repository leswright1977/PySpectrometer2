x = [175,296,312,342,402,490,604,613,694,1022,1116,1122,1491,1523,1590,1627,1669]
y= [253.65,296.73,302.15,313.16,334.15,365.02,404.66,407.78,435.84,546.07,576.96,579.07,696.54,706.72,727.29,738.4,751.47]

mymodel = numpy.poly1d(numpy.polyfit(x, y, 3))

print(mymodel)

px = 1669

print("Third order")
y=((-2.248e-09*px**3)+(-1.246e-05*px**2)+(0.3632*px)+190.4)

print(y)

#put the above model data in the array.... Verify R??


predict = []

for i in x:
	px = i
	y=((-2.248e-09*px**3)+(-1.246e-05*px**2)+(0.3632*px)+190.4)
	predict.append(y)

print(predict)


actual = [253.65,296.73,302.15,313.16,334.15,365.02,404.66,407.78,435.84,546.07,576.96,579.07,696.54,706.72,727.29,738.4,751.47]

 
corr_matrix = numpy.corrcoef(actual, predict)
corr = corr_matrix[0,1]
R_sq = corr**2
 
print(R_sq)
