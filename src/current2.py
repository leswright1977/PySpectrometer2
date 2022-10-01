import cv2
import time
import numpy as np
from specFunctions import wavelength_to_rgb, savitzky_golay, peakIndexes,readcal

#init video
cap = cv2.VideoCapture(0)
print("[info] W, H, FPS")
cap.set(cv2.CAP_PROP_FRAME_WIDTH,800)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,600)
print(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
print(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(cap.get(cv2.CAP_PROP_FPS))
frameWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frameHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

title1 = 'PySpectrometer 2 - Spectrograph'
title2 = 'PySpectrometer 2 - Waterfall'

stackHeight = 255+80+80+80 #height of the displayed CV window (waterfall+graph+preview+messages+sliders)
cv2.namedWindow(title1,cv2.WINDOW_GUI_NORMAL)
cv2.resizeWindow(title1,frameWidth,stackHeight)
'''
This is how we do fullscreen!
Add as an option??
cv2.namedWindow(title1,cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty(title1,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
'''

cv2.namedWindow(title2,cv2.WINDOW_GUI_NORMAL)
cv2.resizeWindow(title2,frameWidth,stackHeight)

#settings for peak detect
savpoly = 7 #savgol filter polynomial
mindist = 50 #minumum distance between peaks
thresh = 20 #Threshold

def savgol(value):
	global savpoly
	savpoly = value;

def peakwidth(value):
	global mindist
	mindist = value;

def peakthreshold(value):
	global thresh
	thresh = value;

cv2.createTrackbar('Savgol Filter ', title1, 7,15, savgol)
cv2.createTrackbar('Peak width', title1, 50,100, peakwidth)
cv2.createTrackbar('Threshold ', title1, 20,100, peakthreshold)

calibrate = False

clickArray = [] 
cursorX = 0
cursorY = 0
def handle_mouse(event,x,y,flags,param):
	global clickArray
	global cursorX
	global cursorY
	mouseYOffset = 160
	if event == cv2.EVENT_MOUSEMOVE:
		cursorX = x
		cursorY = y		

	if event == cv2.EVENT_LBUTTONDOWN:
		mouseX = x
		mouseY = y-mouseYOffset
		clickArray.append([mouseX,mouseY])

#listen for click on plot window
cv2.setMouseCallback(title1,handle_mouse)


def snapshot(imdata1,imdata2,graphdata):
	now = time.strftime("%Y%m%d--%H%M%S")
	cv2.imwrite("spectrum-" + now + ".png",imdata1)
	cv2.imwrite("waterfall-" + now + ".png",imdata2)
	#print(graphdata[0]) #wavelengths
	#print(graphdata[1]) #intensities
	f = open("Spectrum-"+now+'.csv','w')
	f.write('Wavelength,Intensity\r\n')
	for x in zip(graphdata[0],graphdata[1]):
		f.write(str(x[0])+','+str(x[1])+'\r\n')
	f.close()
	message = "Last Save Data: "+now
	return(message)

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
	#second it validates the data in as far os no strings were entered 
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



font=cv2.FONT_HERSHEY_SIMPLEX

intensity = [0] * frameWidth #array for intensity data...full of zeroes
holdpeaks = False




#messages
msg1 = ""
msg2 = "Press 's' to save data"

#blank image for Waterfall
waterfall = np.zeros([335,frameWidth,3],dtype=np.uint8)
waterfall.fill(0) #fill black

#Go grab the computed calibration data
wavelengthData = readcal(frameWidth)

print(len(wavelengthData))



def generateGraticule():
	low = wavelengthData[0]
	high = wavelengthData[len(wavelengthData)-1]
	#round and int these numbers so we have our range of numbers to look at
	#give a margin of 10 at each end for good measure
	low = int(round(low))-10
	high = int(round(high))+10
	print('...')
	print(low)
	print(high)
	print('...')
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


graticuleData = generateGraticule()
tens = (graticuleData[0])
fifties = (graticuleData[1])




while(cap.isOpened()):
	# Capture frame-by-frame
	ret, frame = cap.read()

	if ret == True:
		y=200 	#origin of the vert crop
		x=0   	#origin of the horiz crop
		h=80 	#height of the crop
		w=frameWidth 	#width of the crop
		cropped = frame[y:y+h, x:x+w]
		bwimage = cv2.cvtColor(cropped,cv2.COLOR_BGR2GRAY)
		rows,cols = bwimage.shape
		halfway =int(rows/2)
		#show our line on the original image
		cv2.line(cropped,(0,halfway),(frameWidth,halfway),(255,255,255),1)


		#blank image for Messages
		messages = np.zeros([80,frameWidth,3],dtype=np.uint8)
		messages[:,:] = [50, 0, 0] #fill array with color
		#now display useful data
		if holdpeaks == True:
			msg1 = "Holdpeaks ON"
		else:
			msg1 = "Holdpeaks OFF" 
		cv2.putText(messages,msg1,(20,20),font,0.4,(0,255,255),1, cv2.LINE_AA)
		cv2.putText(messages,msg2,(20,40),font,0.4,(0,255,255),1, cv2.LINE_AA)
		'''
		msg3 = "Point1 = "+str(point1)+"px"
		cv2.putText(messages,msg3,(300,20),font,0.4,(0,255,255),1, cv2.LINE_AA)
		msg4 = "Point2 = "+str(point2)+"px"
		cv2.putText(messages,msg4,(300,40),font,0.4,(0,255,255),1, cv2.LINE_AA)


		msg3 = str(nm1)+"nm"
		cv2.putText(messages,msg3,(420,20),font,0.4,(0,255,255),1, cv2.LINE_AA)
		msg4 = str(nm2)+"nm"
		cv2.putText(messages,msg4,(420,40),font,0.4,(0,255,255),1, cv2.LINE_AA)
		'''


		#blank image for Graph
		graph = np.zeros([255,frameWidth,3],dtype=np.uint8)
		graph.fill(255) #fill white

		




		#Display a graticule calibrated with cal data
		textoffset = 12
		#vertial lines every whole 10nm
		for position in tens:
			cv2.line(graph,(position,15),(position,255),(200,200,200),1)

		#vertical lines every whole 50nm
		for positiondata in fifties:
			cv2.line(graph,(positiondata[0],15),(positiondata[0],255),(0,0,0),1)
			cv2.putText(graph,str(positiondata[1])+'nm',(positiondata[0]-textoffset,12),font,0.4,(0,0,0),1, cv2.LINE_AA)

		#horizontal lines
		for i in range (255):
			if i!=0 and i%51==0: #suppress the first line then draw the rest...
				cv2.line(graph,(0,i),(frameWidth,i),(100,100,100),1)
		
		#Now process the intensity data and display it
		#intensity = []
		for i in range(cols):
			data = bwimage[halfway,i] #pull the pixel data from the halfway mark
			if holdpeaks == True:
				if data > intensity[i]:
					intensity[i] = data
			else:
				intensity[i] = data


		#waterfall....
		#data is smoothed at this point!!!!!!
		#create an empty array for the data
		wdata = np.zeros([1,frameWidth,3],dtype=np.uint8)
		index=0
		for i in intensity:
			rgb = wavelength_to_rgb(round(wavelengthData[index]))#derive the color from the wvalenthData array
			luminosity = intensity[index]/255
			b = rgb[0]*luminosity
			g = rgb[1]*luminosity
			r = rgb[2]*luminosity
			#print(b,g,r)
			#wdata[0,index]=(r,g,b) #fix me!!! how do we deal with this data??
			wdata[0,index]=(r,g,b)
			index+=1
		waterfall = np.insert(waterfall, 0, wdata, axis=0)
		waterfall = waterfall[:-1].copy()


		#Draw the intensity data :-)
		#first filter if not holding peaks!
		if holdpeaks == False:
			intensity = savitzky_golay(intensity,17,savpoly)
			intensity = np.array(intensity)
			intensity = intensity.astype(int)

		index=0
		for i in intensity:
			rgb = wavelength_to_rgb(round(wavelengthData[index]))#derive the color from the wvalenthData array
			r = rgb[0]
			g = rgb[1]
			b = rgb[2]
			#or some reason origin is top left.
			cv2.line(graph, (index,255), (index,255-i), (b,g,r), 1)
			cv2.line(graph, (index,254-i), (index,255-i), (0,0,0), 1,cv2.LINE_AA)
			index+=1


		#find peaks and label them
		textoffset = 12
		thresh = int(thresh) #make sure the data is int.
		indexes = peakIndexes(intensity, thres=thresh/max(intensity), min_dist=mindist)
		#print(indexes)
		for i in indexes:
			height = intensity[i]
			height = 245-height
			wavelength = round(wavelengthData[i],1)
			cv2.rectangle(graph,((i-textoffset)-2,height),((i-textoffset)+60,height-15),(0,255,255),-1)
			cv2.rectangle(graph,((i-textoffset)-2,height),((i-textoffset)+60,height-15),(0,0,0),1)
			cv2.putText(graph,str(wavelength)+'nm',(i-textoffset,height-3),font,0.4,(0,0,0),1, cv2.LINE_AA)
			#flagpoles
			cv2.line(graph,(i,height),(i,height+10),(0,0,0),1)



		cv2.line(graph,(cursorX,cursorY-140),(cursorX,cursorY-180),(0,0,0),1)
		cv2.line(graph,(cursorX-20,cursorY-160),(cursorX+20,cursorY-160),(0,0,0),1)
		cv2.putText(graph,str(round(wavelengthData[cursorX],2))+'nm',(cursorX+5,cursorY-165),font,0.4,(0,0,0),1, cv2.LINE_AA)

		if clickArray:
			for data in clickArray:
				mouseX=data[0]
				mouseY=data[1]
				cv2.circle(graph,(mouseX,mouseY),5,(0,0,0),-1)
				#we can display text :-) so we can work out wavelength from x-pos and display it ultimately
				cv2.putText(graph,str(mouseX),(mouseX+5,mouseY),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,0,0))
		



		#stack the images and display the spectrum	
		spectrum_vertical = np.vstack((messages,cropped, graph))
		#dividing lines...
		cv2.line(spectrum_vertical,(0,80),(frameWidth,80),(255,255,255),1)
		cv2.line(spectrum_vertical,(0,160),(frameWidth,160),(255,255,255),1)
		cv2.imshow(title1,spectrum_vertical)


		#stack the images and display the waterfall	
		waterfall_vertical = np.vstack((messages,cropped, waterfall))
		#dividing lines...
		cv2.line(waterfall_vertical,(0,80),(frameWidth,80),(255,255,255),1)
		cv2.line(waterfall_vertical,(0,160),(frameWidth,160),(255,255,255),1)
		#Draw this stuff over the top of the image!
		#Display a graticule calibrated with cal data
		textoffset = 12

		#vertical lines every whole 50nm
		for positiondata in fifties:
			for i in range(162,480):
				if i%20 == 0:
					cv2.line(waterfall_vertical,(positiondata[0],i),(positiondata[0],i+1),(0,0,0),2)
					cv2.line(waterfall_vertical,(positiondata[0],i),(positiondata[0],i+1),(255,255,255),1)
			cv2.putText(waterfall_vertical,str(positiondata[1])+'nm',(positiondata[0]-textoffset,490),font,0.4,(0,0,0),2, cv2.LINE_AA)
			cv2.putText(waterfall_vertical,str(positiondata[1])+'nm',(positiondata[0]-textoffset,490),font,0.4,(255,255,255),1, cv2.LINE_AA)
		cv2.imshow(title2,waterfall_vertical)


		keyPress = cv2.waitKey(10) #Altering waitkey val can alter the framreate for vid files.
		if keyPress == ord('q'):
			break
		elif keyPress == ord('a'):
			print(mouseX,mouseY)
		elif keyPress == ord('h'):
			print(holdpeaks)
			if holdpeaks == False:
				holdpeaks = True
			elif holdpeaks == True:
				holdpeaks = False
		elif keyPress == ord("s"):
			#package up the data!
			graphdata = []
			graphdata.append(wavelengthData)
			graphdata.append(intensity)
			msg2 = snapshot(spectrum_vertical,waterfall_vertical,graphdata)
		elif keyPress == ord("c"):
			calcomplete = writecal(clickArray)
			if calcomplete:
				#overwrite wavelength data
				wavelengthData = readcal(frameWidth)
				#overwrite graticule data
				graticuleData = generateGraticule()
				tens = (graticuleData[0])
				fifties = (graticuleData[1])
		elif keyPress == ord("x"):
			clickArray = []

	else: 
		break

 
#Everything done, release the vid
cap.release()

cv2.destroyAllWindows()


