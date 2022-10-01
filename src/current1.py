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



stackHeight = 255+255+80+80 #height of the displayed CV window (waterfall+graph+preview+messages)
cv2.namedWindow('PySpectrometer Pro',cv2.WINDOW_GUI_NORMAL)
cv2.resizeWindow('PySpectrometer Pro',frameWidth,stackHeight)

calibrate = False

clickArray = [] 
def get_click(event,x,y,flags,param):
	global clickArray
	mouseYOffset = 160
	if event == cv2.EVENT_LBUTTONDOWN:
		mouseX = x
		mouseY = y-mouseYOffset
		clickArray.append([mouseX,mouseY])

#listen for click on plot window
cv2.setMouseCallback('PySpectrometer Pro',get_click)


def snapshot(imdata,graphdata):
	now = time.strftime("%d-%m-%Y-%H--%M--%S")
	cv2.imwrite("spectrum-" + now + ".png",imdata)
	#print(graphdata[0]) #wavelengths
	#print(graphdata[1]) #intensities
	f = open("Spectrum-"+now+'.csv','w')
	f.write('Wavelength,Intensity\r\n')
	for x in zip(graphdata[0],graphdata[1]):
		f.write(str(x[0])+','+str(x[1])+'\r\n')
	f.close()
	message = "Last Save Data: "+now
	return(message)


#initial graph points and wavelengths.
point1 = 72  #405nm
nm1 = 405
point2 = 304 #532nm  
nm2 = 532

font=cv2.FONT_HERSHEY_SIMPLEX

intensity = [0] * frameWidth #array for intensity data...full of zeroes
holdpeaks = False


#settings for peak detect
mindist = 50 #minumum distance between peaks
thresh = 20 #Threshold
savpoly = 7 #savgol filter polynomial

#messages
msg1 = ""
msg2 = "Press 's' to save data"

#blank image for Waterfall
waterfall = np.zeros([255,frameWidth,3],dtype=np.uint8)
waterfall.fill(0) #fill black


while(cap.isOpened()):
	# Capture frame-by-frame
	ret, frame = cap.read()

	if ret == True:
		y=200 	#origin of the vert crop
		x=0   	#origin of the horix crop
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
	
		msg3 = "Point1 = "+str(point1)+"px"
		cv2.putText(messages,msg3,(300,20),font,0.4,(0,255,255),1, cv2.LINE_AA)
		msg4 = "Point2 = "+str(point2)+"px"
		cv2.putText(messages,msg4,(300,40),font,0.4,(0,255,255),1, cv2.LINE_AA)


		msg3 = str(nm1)+"nm"
		cv2.putText(messages,msg3,(420,20),font,0.4,(0,255,255),1, cv2.LINE_AA)
		msg4 = str(nm2)+"nm"
		cv2.putText(messages,msg4,(420,40),font,0.4,(0,255,255),1, cv2.LINE_AA)


	

		#blank image for Graph
		graph = np.zeros([255,frameWidth,3],dtype=np.uint8)
		graph.fill(255) #fill white

		#Display a graticule calibrated with cal data
		#calculate the ranges
		pxrange = abs(point1-point2) #how many px between points 1 and 2?
		nmrange = abs(nm1-nm2) #how many nm between points 1 and 2?
		#how many pixels per nm?
		pxpernm = pxrange/nmrange
		#how many nm per pixel?
		nmperpx = nmrange/pxrange
		#how many nm is zero on our axis
		zero = nm1-(point1/pxpernm)
		scalezero =zero #we need this unchanged duplicate of zero for later!
		prevposition = 0
		textoffset = 12

		#Graticule
		#vertical lines
		for i in range(frameWidth):
			position = round(zero)
			if position != prevposition: #because of rounding, sometimes we draw twice. Lets fix tht!
				# we could have grey lines for subdivisions???S
				if position%10==0:
					cv2.line(graph,(i,15),(i,255),(200,200,200),1)
				if position%50==0:
					cv2.line(graph,(i,15),(i,255),(0,0,0),1)
					cv2.putText(graph,str(position)+'nm',(i-textoffset,12),font,0.4,(0,0,0),1, cv2.LINE_AA)
			zero += nmperpx
			prevposition = position
		#horizontal lines
		for i in range (255):
			if i!=0 and i%51==0: #suppress the first line then draw the rest...
				cv2.line(graph,(0,i),(frameWidth,i),(100,100,100),1)


		#Now process the intensity data and display it
		#intensity = []
		for i in range(cols):
			data = bwimage[halfway,i]
			if holdpeaks == True:
				if data > intensity[i]:
					intensity[i] = data
			else:
				intensity[i] = data

		if holdpeaks == False:
			intensity = savitzky_golay(intensity,17,4)
			intensity = np.array(intensity)
			intensity = intensity.astype(int)


		peak = 0
		x=0
		#now draw the graph
		#for each index, plot a verital line derived from int
		#use waveleng_to_rgb to false color the data.
		wavelengths = []
		index=0
		for i in intensity:
			wavelength = (scalezero+(index/pxpernm))
			wavelengthdata = round(wavelength,1)
			wavelength = round(wavelength)
			wavelengths.append(wavelengthdata)
			rgb = wavelength_to_rgb(wavelength)
			r = rgb[0]
			g = rgb[1]
			b = rgb[2]
			#or some reason origin is top left.
			cv2.line(graph, (index,255), (index,255-i), (b,g,r), 1)
			cv2.line(graph, (index,254-i), (index,255-i), (0,0,0), 1,cv2.LINE_AA)
			index+=1


		#filter expects a numpy array...
		intensity = np.array(intensity)
		#filter expects it to be signed
		intensity = intensity.astype(int)
		#print(intensity)
		#find peaks and label them
		textoffset = 12
		thresh = int(thresh) #make sure the data is int.
		indexes = peakIndexes(intensity, thres=thresh/max(intensity), min_dist=mindist)
		#print(indexes)
		for i in indexes:
			height = intensity[i]
			height = 245-height
			wavelength = int(scalezero+(i/pxpernm))
			cv2.rectangle(graph,((i-textoffset)-2,height+3),((i-textoffset)+45,height-11),(0,255,255),-1)
			cv2.rectangle(graph,((i-textoffset)-2,height+3),((i-textoffset)+45,height-11),(0,0,0),1)
			cv2.putText(graph,str(wavelength)+'nm',(i-textoffset,height),font,0.4,(0,0,0),1, cv2.LINE_AA)

		#waterfall....
		#data is smoothed at this point!!!!!!
		#create an empty array for the data
		wdata = np.zeros([1,frameWidth,3],dtype=np.uint8)
		#Iterate over the intesity data
		#wdata[0,1] = (255,255,255)
		#print(len(intensity))
		index=0
		for i in intensity:
			wavelength = round(scalezero+(index/pxpernm))
			rgb=wavelength_to_rgb(wavelength)
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


	

		if clickArray:
			for data in clickArray:
				mouseX=data[0]
				mouseY=data[1]
				cv2.circle(graph,(mouseX,mouseY),5,(0,0,0),-1)
				#we can display text :-) so we can work out wavelength from x-pos and display it ultimately
				cv2.putText(graph,str(mouseX),(mouseX+5,mouseY),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,0,0))
		



		#stack the images and display	
		numpy_vertical = np.vstack((messages,cropped, graph, waterfall))
		#dividing lines...
		cv2.line(numpy_vertical,(0,80),(frameWidth,80),(255,255,255),1)
		cv2.line(numpy_vertical,(0,415),(frameWidth,415),(255,255,255),1)
		cv2.imshow("PySpectrometer Pro",numpy_vertical)





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
			graphdata.append(wavelengths)
			graphdata.append(intensity)
			msg2 = snapshot(numpy_vertical,graphdata)
		elif keyPress == ord("c"):
			calibrate = True
			click0 = clickArray[0][0]
			click1 = clickArray[1][0]
			wl1 = input("Enter wavelength for Point 1 "+str(click0)+"px:")
			wl2 = input("Enter wavelength for Point 2 "+str(click1)+"px:")
			#now do the cal.....
			point1 = int(click0)
			nm1 = int(wl1)
			point2 = int(click1) 
			nm2 = int(wl2)
			print("Done!")
		elif keyPress == ord("x"):
			clickArray = []

	else: 
		break

 
#Everything done, release the vid
cap.release()

cv2.destroyAllWindows()


