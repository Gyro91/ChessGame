import pyxvrlight
from PyQt4 import QtGui,QtCore,uic

import sys
import os, glob
import subprocess
import string, time
import datetime

try:
	print "using ",XVR_Port
except:
	XVR_Port = 12345
	GUI_Port = 12346

form_class, base_class = uic.loadUiType("GUI_Cubes.ui")

puzzle = []
app_on = 0
code = ""
data = ""
paziente = "<Patient>"
lista = []
log = 0		# 0: log off    1: log on
cubesize = 0.15
scale = 3.0
horiz = 0.0
vert =  -0.4
depth = 0.5
force_enabled = False
tot_time = 0
logger_on = False	# ENABLE THE PYTHON LOGGER ON A FILE

class MyFrame(QtGui.QMainWindow,form_class):
	def __init__(self, title):
		QtGui.QMainWindow.__init__(self)
		self.setupUi(self)
		# create writer,reader and binding to event
		self.writer = pyxvrlight.DataWriter(XVR_Port)
		self.reader = pyxvrlight.DataReaderQt(self, GUI_Port)
		self.reader.Start()

		self.setWindowTitle("GUI CUBES v.2.0")

		#TIMER
		global tot_time
		tot_time = QtCore.QTime(0,0,0,0)
		self.stimer = QtCore.QTimer()
		QtCore.QObject.connect(self.stimer,QtCore.SIGNAL("timeout()"),self.timerUpdate)
		self.stimer.start(1000)

		# INIT PARAMETERS
		self.SliderGrasp.setValue(2)
		self.SliderScale.setValue(scale)
		self.SliderVert.setValue(10*vert)
		self.SliderHoriz.setValue(10*horiz)
		self.SliderDepth.setValue(10*depth)
#		self.label_scale.setNum(round(1/float(scale),2))
		self.label_scale.setNum(round(float(scale)/2,2))
		global paziente, lista

		# ADD COMBO PAZIENTE ON TOOLBAR
		self.comboPaziente = QtGui.QComboBox()
		self.comboPaziente.setGeometry(QtCore.QRect(210, 40, 101, 22))
		self.comboPaziente.setAutoFillBackground(False)
		self.comboPaziente.setEditable(True)
		self.comboPaziente.setObjectName("comboPaziente")
		self.comboPaziente.addItem(QtCore.QString())
		self.comboPaziente.setItemText(0, QtGui.QApplication.translate("MainWindow", paziente, None, QtGui.QApplication.UnicodeUTF8))
		# SEARCH AND LIST EACH PATIENT NAME FROM FOLDER IN LOG
		#lista=listname("Log","txt")
		lista=listname("Log","")
		#... AND UPDATE THE COMBOLIST
		for i in range(len(lista)):
			self.comboPaziente.addItem(QtCore.QString())
			self.comboPaziente.setItemText(i+1, QtGui.QApplication.translate("MainWindow", unicode(lista[i]), None, QtGui.QApplication.UnicodeUTF8))
		self.toolBar.addWidget(self.comboPaziente)
		QtCore.QObject.connect(self.comboPaziente, QtCore.SIGNAL("activated(QString)"), self.on_comboPaziente_activated)
#		QtCore.QObject.connect(self.comboPaziente.lineEdit(), QtCore.SIGNAL("returnPressed()"), self.on_comboPaziente_returnPressed)
		print "Nr.",self.comboPaziente.count()-1,"Patients"
		

		#... AND UPDATE THE PUZZLE COMBOLIST FIRST ELEMENT
		self.comboPuzzle.setAutoFillBackground(False)
		self.comboPuzzle.setEditable(True)
		self.comboPuzzle.addItem(QtCore.QString())
		self.comboPuzzle.setItemText(0, QtGui.QApplication.translate("MainWindow", "", None, QtGui.QApplication.UnicodeUTF8))

			# Begin handling of receiving data from XVR to GUI here
			
	def onXVRData(self,xvrdata):
		global code, data, cubesize, scale, lista, app_on, log, paziente, force_enabled, puzzle
		
		# DECODING COMMAND PROTOCOL
		if(xvrdata.find(",")>=0):
			command = string.split(xvrdata,",")	# "<code> , <data>"
			code=command[0]
			data=command[1:]
			print "Received ",code,"-",data," From XVR"
		else:
			code=xvrdata
			print "Received ",code," From XVR"
		
		# RECEIVE ALL THE PUZZLE LOADED FROM XVR
		if (code=="PUZ"):
			for p in data:
				puzzle.append(p)
			#... AND LOAD IT INSIDE THE COMBOBOX
			for i in range(len(puzzle)):
				self.comboPuzzle.addItem(QtCore.QString())
				self.comboPuzzle.setItemText(i+1, QtGui.QApplication.translate("MainWindow", unicode(puzzle[i]), None, QtGui.QApplication.UnicodeUTF8))
			self.comboPuzzle.setCurrentIndex(2)
			self.writer.write(["PUZ",str(self.comboPuzzle.currentText())])
			image=QtGui.QPixmap("Cubes\\"+str(self.comboPuzzle.currentText())+"\\Sinopia.jpg")
			self.label_puzzle.setPixmap(image.scaled(QtCore.QSize(86,86),0))

			
		elif (code == "LOG"):	# ENABLE THE GREEN LED TO INDICATE THE STARTING LOG OF DATA
			val=string.atof(data[0])
			#print "Val=",val
			if(val==1):
				self.led.setPixmap(QtGui.QPixmap("img_gui\\Button Blank Green-01.png"))
				self.label_log.setText("LOG ON")
				log = 1
				print "LOG ON"
			elif (val==0):
				self.led.setPixmap(QtGui.QPixmap("img_gui\\Button Blank Gray-01.png"))
				self.label_log.setText("LOG OFF")
				log = 0
				print "LOG OFF"
		
		elif(code == "CUB"):
			cubesize=string.atof(data[0])	# TO RECEIVE THE DIM OF CUBE
			print "CubeSize=",cubesize

		elif(code == "PAT"):
			tempdata = ["Patients",len(lista)]
			for x in lista[:]:
				tempdata.append(x)
			#print "DATA :",tempdata
			self.writer.write(tempdata)
			print "Patients(",len(lista),"):", lista
			
		elif(code == "APP"):
			val=string.atof(data[0])
			if(val==-1):	# EXIT FROM APP
				self.PushStartApp.setText("START XVR")
				app_on = 0
				log = 0
				self.led.setPixmap(QtGui.QPixmap("img_gui\\Button Blank Gray-01.png"))
				self.label_log.setText("LOG OFF")
				#delnullfile()
				
		elif (code == "INT"):   # INITIALIZE PARAMETERS
			print " ************ Initialization ************"
			self.writer.write(["ChangeBodyMass", self.DoubleSpinBoxBodyMass.value()])
			print "Sending [\"ChangeBodyMass\", %f]" %self.DoubleSpinBoxBodyMass.value()	
			self.writer.write(["ChangeGrasp", self.SliderGrasp.value()])
			print "Sending [\"ChangeGrasp\", %d]" %self.SliderGrasp.value()
			self.writer.write(["ChangeScale", self.SliderScale.value()])
			print "Sending [\"ChangeScale\", %d]" %self.SliderScale.value()
			if( (paziente!="<Patient>") & (log==0) ):
				self.writer.write(["NewLog",paziente])
				print "Sending [\"NEW LOG:",paziente,"\"]"
			self.writer.write(["ChangeVert", float(self.SliderVert.value())/10])
			self.writer.write(["ChangeHoriz", float(self.SliderHoriz.value())/10])
			self.writer.write(["ChangeDepth", float(self.SliderDepth.value())/10])
			print "H=",float(self.SliderHoriz.value())/10
			print "V=",float(self.SliderVert.value())/10
			print "D=",float(self.SliderDepth.value())/10
			self.writer.write(["ChangeDamper", float(self.SliderDamper.value())])
			self.comboPuzzle.setCurrentIndex(2)
			image=QtGui.QPixmap("Cubes\\"+str(self.comboPuzzle.currentText())+"\\Sinopia.jpg")
			print " ****************************************"
			
		elif (code == "FOR"):	#FORCE ENABLE
			force_enabled = not force_enabled

		elif (code == "SAVE"):   # SAVE AND APPEND SCORES DATA
			task_score = data[0]
			data_score = data[1]
			date_score = data[2]
			#print existfile("TotalScores.dat",".")
			if(paziente!="<Patient>"):
				if(existfile("TotalScores.dat",".")):	# IF FILE EXIST...
					#print"SAVING..."
					filescore = open("TotalScores.dat","a")
					filescore.write("\n"+paziente+","+date_score+","+task_score+","+data_score)
					filescore.close()
				else:
					#print"FIRST SAVING..."
					filescore = open("TotalScores.dat","a")
					filescore.write(paziente+","+date_score+","+task_score+","+data_score)
					filescore.close()
	
		elif (code == "LOAD"):   # LOAD AND SEND SCORES DATA
			task = data[0]
			scores = []
			if(paziente!="<Patient>"):
				if(existfile("TotalScores.dat",".")):	# IF FILE EXIST...
					filescore = open("TotalScores.dat","r")
					for line in filescore:
						temp = line.split(",")
						if((temp[0]==paziente)&(temp[2]==task)):
							score = float(temp[3])
							scores.append(round(score,1))
					print "TASK:",task," > ",scores
					filescore.close()
					self.writer.write(["SCORE",scores])

		else:
			print "Undefined Command"

	# End handling of receiving data from XVR to GUI here
		
	# Begin handling of sending data from GUI to XVR here	
	
	#@QtCore.pyqtSignature("") 		# define a new signal ("" for Strings; "int" for Integer)
	#def on_upButton_clicked(self):	# on_<GUI element name>_<GUI element action> ("clicked" for Button, "valueChanged" for Slider)
	#	self.writer.write("up") 	# send this variable ( can be String, Int, Array, etc)


	
	
	def timerUpdate(self):
		global tot_time, log
		# TIMER UPDATED ONLY DURING ACTIVE TASK
		if(log==1):
			tot_time = tot_time.addSecs(1)
			time_text = tot_time.toString("mm:ss")
			self.label_totaltime.setText(time_text)


			
			
	# PUT  A CONSTRAINTS FOR THE START APPLICATION
	@QtCore.pyqtSignature("")
	def on_PushStartApp_clicked(self):
		global app_on
		#print "[App %d]" %app_on
		if (app_on==0):
			app_on = 1
			self.writer.write(["StartApp"])
			#os.startfile("CubAppl_B.htm")
			#os.startfile("cubetti.bat")
			os.startfile("cubes.bat")
			self.PushStartApp.setText("CLOSE XVR")
			print "[StartApp]"
		elif (app_on==1):
			self.PushStartApp.setText("START XVR")
			app_on = 0
			self.writer.write(["CloseApp"])
			print "[ColseApp]"
			#os.system("cls")
#		print "Sending [ Start XVR App %d]" %startapp




	# SAVE CONFIGURATION DATA FOR THE ACTUAL PATIENT
	@QtCore.pyqtSignature("")
	def on_PushSaveConfig_clicked(self):
		global paziente
		config=[0,0,0,0,0,0,0,0]
		if paziente==("" or "<Patient>" or " "):
			MESSAGE = "<p> INVALID PATIENT'S NAME!</p>"
			reply=QtGui.QMessageBox(QtGui.QMessageBox.Warning, "WARNING!", MESSAGE, QtGui.QMessageBox.NoButton,self)
			reply.addButton("O&K",QtGui.QMessageBox.AcceptRole)
			if reply.exec_()==QtGui.QMessageBox.AcceptRole:
				print "OK"
		else:
			config[0]=self.SliderVert.value()
			config[1]=self.SliderDepth.value()
			config[2]=self.SliderHoriz.value()
			config[3]=self.SliderScale.value()
			config[4]=self.SliderDamper.value()
			config[5]=self.SliderGrasp.value()
			config[6]=self.DoubleSpinBoxGravityCompensation.value()
			config[7]=self.DoubleSpinBoxBodyMass.value()
			str_config=datetime.date.today().strftime("%d%m%y")
			for i in range(0,len(config)):
				str_config+=",%d"
			print "SAVE ",paziente," CONFIGURATION"
			paziente_path="Log\\"+paziente
			if(not(os.path.exists(paziente_path))):
				os.mkdir(paziente_path)
			fileconfig=open(paziente_path+"\\Config.dat","a")
			fileconfig.write(str_config%tuple(config))
			fileconfig.close()
			
# *************************** TOOLBAR ************************************
	
	@QtCore.pyqtSignature("")
	def on_actionNew_triggered(self):
		global paziente, log
		# IF paziente IS VALID NAME AND LOG NOT JUST STARTED...
		if( (paziente!="<Patient>") & (log==0) ):
			self.writer.write(["NewLog",paziente])
			print "Sending [\"NEW LOG:",paziente,"\"]"
		
	
	
	@QtCore.pyqtSignature("")
	def on_actionSave_triggered(self):
		global paziente, log
		if(paziente!="<Patient>"):
			self.writer.write(["StopLog"])
			print "Sending [\"STOP LOG:",paziente,"\"]"
		

	@QtCore.pyqtSignature("")
	def on_actionPlotData_triggered(self):
		self.writer.write(["PlotData"])
		print "Sending [\"PLOT DATA\"]"

		

    # TO SELECT COMBO ITEM
	@QtCore.pyqtSignature("QString")
	def on_comboPaziente_activated(self,value):
		print "ACTIVE"
		global paziente, lista, log
		paziente = str(self.comboPaziente.currentText())
		# IF paziente IS VALID NAME AND LOG NOT JUST STARTED...
		if( (paziente!="<Patient>") & (log==0) ):
			tot_time.setHMS(0,0,0,0)	#RESET TIMER WHEN CHANGE NEW PATIENT
			time_text = tot_time.toString("mm:ss")
			self.label_totaltime.setText(time_text)
			self.writer.write(["NewLog",paziente])
			self.setWindowTitle("GUI CUBES v.2.0 - "+paziente.upper())
			print "Sending [\"New Patient: ", paziente,"\"]"
			paziente_path="Log\\"+paziente
			# IF IT DOESN'T EXIST, IT CREATES FOLDER FOR paziente
			if(not os.path.exists(paziente_path)):
				os.mkdir(paziente_path)
			if(os.path.exists(paziente_path+"\\Config.dat")):
				print "LOADING CONFIG"
				fileconfig=open(paziente_path+"\\Config.dat","r")
				for line in fileconfig:
					temp=line.split(",")
					config=[float(i) for i in temp[1:]]
					self.label_vert.setNum(float(config[0])/10)
					self.SliderVert.setValue(config[0])
					self.label_depth.setNum(float(config[1])/10)
					self.SliderDepth.setValue(config[1])
					self.label_horiz.setNum(float(config[2])/10)
					self.SliderHoriz.setValue(config[2])
#					self.label_scale.setNum(round(1/float(config[3]),2))
					self.label_scale.setNum(round(float(config[3])/2,2))
					self.SliderScale.setValue(config[3])
					self.SliderDamper.setValue(config[4])
					self.label_damper.setNum(config[4])
					self.SliderGrasp.setValue(config[5])
					self.label_grasp.setNum(config[5])
					self.DoubleSpinBoxGravityCompensation.setValue(config[6])
					self.DoubleSpinBoxBodyMass.setValue(config[7])



	# TO REMOVE COMBO ITEM
	@QtCore.pyqtSignature("")
	def on_actionDel_triggered(self):
	# IF COMBOLIST EXIST AND CONTAINS PATIENTS...
		if ((self.comboPaziente.count()>0) & (self.comboPaziente.currentText() != "<Patient>")):
			reply=QtGui.QMessageBox.critical(self, "ATTENZIONE!", "Vuoi Cancellare Tutti i Dati del Paziente %s?" %unicode(self.comboPaziente.currentText()), QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
			if reply == QtGui.QMessageBox.Yes:
				self.writer.write(["",str(self.comboPaziente.currentText())," removed"])
				print self.comboPaziente.currentText()," removed"
				self.comboPaziente.removeItem(self.comboPaziente.currentIndex())
			else:
				self.writer.write(["",str(self.comboPaziente.currentText())," not removed"])
				print self.comboPaziente.currentText()," not removed"
		else:
			print "No Patient"


# ************************************************************************************************
	
# ------------------------------------------------ SESSION ---------------------------------------------------
	@QtCore.pyqtSignature("QString")
	def on_comboPuzzle_activated(self,value):
		if(value!=""):
			self.writer.write(["PUZ",str(value)])
			image=QtGui.QPixmap("Cubes\\"+str(value)+"\\Sinopia.jpg")
			self.label_puzzle.setPixmap(image.scaled(QtCore.QSize(86,86),0))
			print "Sending [ %s]" %value


	# ------------- Radio VIEW MODE ----------------
	# @QtCore.pyqtSignature("")
	# def on_radio2d_clicked(self):
		# self.writer.write(["2d"])
		# print "Sending [\"Change View: 2D\"]"

	# @QtCore.pyqtSignature("")
	# def on_radio3d_clicked(self):
		# self.writer.write(["3d"])
		# print "Sending [\"Change View: 3D\"]"

	@QtCore.pyqtSignature("")
	def on_PushButtonPuzzle_clicked(self):
		self.writer.write(["Puzzle"])
		print "Enable Puzzle"
		value=self.comboPuzzle.currentText()
		image=QtGui.QPixmap("Cubes\\"+str(value)+"\\Sinopia.jpg")
		self.label_puzzle.setPixmap(image.scaled(QtCore.QSize(86,86),0))
		self.writer.write(["PUZ",str(value)])

	@QtCore.pyqtSignature("")
	def on_PushButtonClock_clicked(self):
		self.comboPuzzle.setCurrentIndex(2)
		image=QtGui.QPixmap("Cubes\\"+str(self.comboPuzzle.currentText())+"\\Sinopia.jpg")
		self.label_puzzle.setPixmap(image.scaled(QtCore.QSize(86,86),0))
		self.writer.write(["Clock"])
		print "Enable Clock"
		
	@QtCore.pyqtSignature("")
	def on_PushButtonEval_clicked(self):
		self.writer.write(["Basket"])
		print "Enable Basket"
		value=self.comboPuzzle.currentText()
		image=QtGui.QPixmap("Cubes\\"+str(value)+"\\Sinopia.jpg")
		self.label_puzzle.setPixmap(image.scaled(QtCore.QSize(86,86),0))
		self.writer.write(["PUZ",str(value)])

# ------------------------------------ TECHNICAL PARAMETERS ---------------------------------------------------
	@QtCore.pyqtSignature("")
	def on_radioActGravComp_clicked(self):
		if (self.radioActGravComp.isChecked()):
			self.writer.write(["GravCompOn"])
			print "Sending [\"GravCompOn\"]"
		else:
			self.writer.write(["GravCompOff"])
			print "Sending [\"GravCompOff\"]"

	@QtCore.pyqtSignature("double")
	def on_DoubleSpinBoxBodyMass_valueChanged(self, value):
		self.writer.write(["ChangeBodyMass", value])
		print "Sending [\"ChangeBodyMass\", %f]" %value	

	@QtCore.pyqtSignature("double")
	def on_DoubleSpinBoxGravityCompensation_valueChanged(self, value):
		self.writer.write(["ChangeGravityCompensation", value])
		print "Sending [\"ChangeGravityCompensation\", %f]" %value	

	@QtCore.pyqtSignature("int")
	def on_SliderGrasp_valueChanged(self, value):
		self.label_grasp.setNum(value)
		self.writer.write(["ChangeGrasp", value])
		print "Sending [\"ChangeGrasp\", %d]" %value


	@QtCore.pyqtSignature("int")
	def on_SliderDamper_valueChanged(self, value):
		damping = float(value)
		self.label_damper.setNum(damping)
		self.writer.write(["ChangeDamper", damping])
		print "Sending [\"ChangeDamper\", %f]" %damping


	@QtCore.pyqtSignature("int")
	def on_SliderCompensation_valueChanged(self, value):
		self.writer.write(["Compensation", value])
		print "Sending [\"Compensation\", %d]" %value
                if (value==3):
                    self.SliderDamper.setDisabled(True)
                else:
                    self.SliderDamper.setEnabled(True)

		
	@QtCore.pyqtSignature("")
	def on_pushForceEnable_clicked(self):
		global force_enabled
		force_enabled = not force_enabled
		self.writer.write(["ForceOn"])
		if(force_enabled):
			self.groupBox_GeoPar.setDisabled(True)
		else:
			self.groupBox_GeoPar.setEnabled(True)
			
		print "Enable Force"
		
# ------------------------------------ GEOMETRIC PARAMETERS ---------------------------------------------------

	@QtCore.pyqtSignature("int")
	def on_SliderScale_valueChanged(self, value):
		global scale
		scale=value
		self.label_scale.setNum(round(float(scale)/2,2))
#		self.label_scale.setNum(round(1/float(scale),2))
		self.writer.write(["ChangeScale", scale])
		print "Sending [\"ChangeScale\", %d]" %scale

	@QtCore.pyqtSignature("int")
	def on_SliderHoriz_valueChanged(self, value):
		global horiz
		horiz=float(value)/10
		self.label_horiz.setNum(horiz)
		self.writer.write(["ChangeHoriz", horiz])
		print "Sending [\"ChangePlace\", (,",horiz,",",vert,",",depth,")]"

	@QtCore.pyqtSignature("int")
	def on_SliderVert_valueChanged(self, value):
		global vert
		vert=float(value)/10
		self.label_vert.setNum(vert)
		self.writer.write(["ChangeVert", vert])
		print "Sending [\"ChangePlace\", (,",horiz,",",vert,",",depth,")]"

	@QtCore.pyqtSignature("int")
	def on_SliderDepth_valueChanged(self, value):
		global depth
		depth=float(value)/10
		self.label_depth.setNum(depth)
		self.writer.write(["ChangeDepth", depth])
		print "Sending [\"ChangePlace\", (,",horiz,",",vert,",",depth,")]"

# ----------------------------------------------- DEVICE CONTROL --------------------------------------------------
	@QtCore.pyqtSignature("")
	def on_PushButtonDeviceOff_clicked(self):
		self.writer.write(["ChangeDeviceOff"])
		print "Sending [\"ChangeDeviceOff\"]"
		
	@QtCore.pyqtSignature("")
	def on_PushButtonDeviceReset_clicked(self):
		self.writer.write(["ChangeDeviceReset"])
		print "Sending [\"ChangeDeviceReset\"]"		

	@QtCore.pyqtSignature("")
	def on_PushButtonDeviceStart_clicked(self):
		self.writer.write(["ChangeDeviceStart"])
		print "Sending [\"ChangeDeviceStart\"]"
		
	@QtCore.pyqtSignature("")
	def on_PushButtonDeviceStop_clicked(self):
		self.writer.write(["ChangeDeviceStop"])
		print "Sending [\"ChangeDeviceStop\"]"

		
		
#  *************************************  UTILITIES  *****************************************
def delnullfile():
# DELETE ALL FILE WITH NULL DIMENSION
# try: os.remove(filename)
#except:
	lista = glob.glob(".\\Log\\*.*")
	#print lista
	for x in lista[:]:
		lenx=os.stat(x)[6]
		#print x,":",lenx
		if(lenx==0):
			os.system("del "+x)
	#lista = glob.glob(".\\Log\\*.*")
	#print lista
	
def existfile(name, directory):
	#file=name.split(".")
	if("." in name):
		dati=glob.glob(directory+"\\"+name)
		#print dati
		temp=dati[0].split(directory+"\\")
		if (name==temp[1]):
			return 1
		else:
			return 0
	else:
		return 0


def findname(name, directory, ext):                                        
	dati=glob.glob(directory+"\\*."+ext)
	lista=[]
	for x in dati[:]:
		temp=x.split(directory+"\\")
		lista.append(temp[1])
	nomi=[]
	for x in lista[:]:
		temp=x.split("_")
		if not(temp[0] in nomi):
			nomi.append(temp[0])
	#print nomi
	if (name in nomi):
		return 1
	else:
		return 0
		
def listname(directory, ext):      
# RETURN THE PATIENTS LIST FROM THE LOG FOLDER                                  
	if(ext!=""):
		dati=glob.glob(directory+"\\*."+ext)
		lista=[]
		for x in dati[:]:
			temp=x.split(directory+"\\")
			lista.append(temp[1])
		nomi=[]
		for x in lista[:]:
			temp=x.split("_")
			if not(temp[0] in nomi):
				nomi.append(temp[0])
		if ("process.m" in nomi):
			nomi.remove("process.m")
	else:
		dati=glob.glob(directory+"\\*")
		nomi=[]
		for x in dati[:]:
			temp=x.split("\\")
			if(not(os.path.isfile(temp[0]+"\\"+temp[1]))):
				if not(temp[1] in nomi):
					nomi.append(temp[1])
		if ("archive" in nomi):
			nomi.remove("archive")
	return nomi
	
class Logger(object):
	def __init__(self):
		self.terminal = sys.stdout
		self.log = open("log.dat", "a")
	def write(self, message):
		self.terminal.write(message)
		self.log.write(message)

		
# FUNCTION CALLED BY THE EXIT SIGNAL
def CloseAll(a):
	global logger_on
	print "EXIT:",a
	writer = pyxvrlight.DataWriter(XVR_Port)
	writer.write(["CloseApp"])
	if(logger_on):
		sys.stdout = sys.__stdout__	# RESET STDOUT
#  **********************************************************************************************

	# End handling of sending data from GUI to XVR here	
	
	
def main():
	global logger_on
	argv = ["me"]
	try:
		argv = sys.argv
	except:
		pass
	if(logger_on):
		sys.stdout = Logger();
	app = QtGui.QApplication(argv)
	qb = MyFrame("Test")
	qb.show()
	sys.exitfunc = CloseAll(app.exec_())
	os._exit(1)
	# sys.exit(app.exec_())	#sys.exit(1) # Or something that calls sys.exit() 

		
if __name__ == "__main__": 
	main()
    
