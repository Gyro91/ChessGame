import thread
import time
import os,sys,socket

wxchecked = False
haswx = False
wx = None
qtchecked = False
hasqt = False
# NOTE: Embedded with netvars
#
# XVR Network Variables into Python and vice versa
#
#
# array.array("f") => VmVector
# array.array("b") => BYTEBUFFER => XVRByteBuffer object
# XVRObject is a packed class
# dictionary is packed into a class with two elements called XVRDICT
import cStringIO,struct,sys,types,array

VmStatus = 0
VmVoid = 1
VmInt = 2
VmReal = 3
VmBool = 4
VmString = 5
VmRifStr = 6
VmArray = 7
VmVector = 8
VmObject = 9
VmRifVector = 10

class XVRObject:
	def __init__(self,classname,values,parents):
		self.classname = classname
		self.values = values
		self.parents = parents
	def __repr__(self):
		return "class %s(values=%d,parents=%d)" % (self.classname,len(self.values),len(self.parents))

class XVRByteBuffer(object):
	def __init__(self,data):
		self.data = data
	def __str__(self):
		return self.data
	def __repr__(self):
		return "bytebuffer(%s)" % (self.data[0:min(20,len(self.data))])

def readInt(sio):
	return struct.unpack("!l",sio.read(4))[0]

def readByte(sio):
	return struct.unpack("B",sio.read(1))[0]

def writeInt(sio,data):
	sio.write(struct.pack("!l",data))

def writeByte(sio,data):
	sio.write(struct.pack("B",data))
	
def decode(sio,type=None,s=""):
	if type is None:
		type = readByte(sio)
	#print s,"type",type
	value = None
	if type == VmVoid or type == VmStatus:
		value = None
	elif type == VmInt or type == VmRifVector or type == VmRifStr:
		value = readInt(sio)
	elif type == VmReal:
		value = struct.unpack("<f",sio.read(4))[0]
	elif type == VmBool:
		value = readByte(sio) > 0 and True or False
	elif type == VmString :
		size = readInt(sio)
		value = sio.read(size)
	elif type == VmArray:
		size = readInt(sio)
		#print s,"array ",size
		value = []
		for i in range(0,size):
			value.append(decode(sio,None,s+" "))
	elif type == VmVector:
		size = readInt(sio)
		value = array.array("f",struct.unpack("%df" % size,sio.read(size*4)))
	elif type == VmObject:
		size = readInt(sio)
		classname = sio.read(size)
		#print s,"class <",classname,">"
		if classname == "BYTEBUFFER":
			value = array.array("b") 
			value.fromstring(decode(sio,VmString))
		else:
			values = []
			parents = []
			for i in range(0,readInt(sio)):
				values.append(decode(sio,None,s+" "))
			for i in range(0,readInt(sio)):
				parents.append(decode(sio,VmObject,s+" "))
			if classname == "XVRDICT" and len(values) == 2 and len(parents) == 0:
				value = {}
				ka = values[0]
				va = values[1]
				for i in range(0,len(ka)):
					value[ka[i]] = va[i]
			else:
				value = XVRObject(classname,values,parents)
				
	else:
		raise "Unknown type %d" % type
	return value



class Decoder:
	def __init__(self):
		self.data = ""
		self.lastdata = ""
	def append(self,data):
		self.data = self.data + data
	def decode(self):
		k = self.data.find("\xffXVR_02\xff")
		if k < 0 and len(self.data) < 12:
			return None
		size = struct.unpack("!L",self.data[k+8:k+12])[0]
		if len(self.data) < size:
			print "bad size ",len(self.data),size
			return None
		try:
			self.lastdata = self.data[k:k+size]
			value,flagdata = decodeMessageFlagged(self.lastdata)
		except:
			print "error ",sys.exc_info()
			self.data = self.data[k+size:]
			self.lastdata = ""
			raise
		self.data = self.data[k+size:]
		return (value,flagdata)



def encode(sio,data,skipcodeForObj=False):
	dt = type(data)
	if data is None:
		writeByte(sio,VmVoid)
	elif dt is types.ListType:
		writeByte(sio,VmArray)
		writeInt(sio,len(data))
		for k in data:
			encode(sio,k)
	elif dt is unicode:
		writeByte(sio,VmString)
		q = data.encode("utf-8")
		writeInt(sio,len(q))
		sio.write(q)
	elif dt is types.StringType:
		writeByte(sio,VmString)
		writeInt(sio,len(data))
		sio.write(data)
	elif dt is types.IntType:
		writeByte(sio,VmInt)
		writeInt(sio,data)
	elif dt is types.FloatType:
		writeByte(sio,VmReal)
		sio.write(struct.pack("<f",data))
	elif dt is types.TupleType:
		writeByte(sio,VmArray)
		writeInt(sio,len(data))
		for k in data:
			encode(sio,k)
	elif dt is types.DictType:
		writeByte(sio,VmObject)
		writeInt(sio,len("XVRDICT"))
		sio.write("XVRDICT")
		writeInt(sio,2)
		encode(sio,data.keys())
		encode(sio,data.values())
		writeInt(sio,0)
	elif data is XVRObject:
		if not skipcodeForObj:
			writeByte(sio,VmObject)
		writeInt(sio,len(data.classname))
		sio.write(sio,data.classname)
		writeInt(sio,len(data.values))
		for k in data.values:
			encode(sio,k)
		writeInt(sio,len(data.parents))
		for k in data.parentes:
			encode(sio,k,True)
	elif data is XVRByteBuffer:
		writeByte(sio,VmObject)
		writeInt(sio,len("BYTEBUFFER"))
		sio.write("BYTEBUFFER")
		writeInt(sio,len(data.data))
		sio.write(data.data)
	elif dt is array.array:
		if data.typecode == 'b' or data.typecode == 'c':
			writeByte(sio,VmObject)
			writeInt(sio,len("BYTEBUFFER"))
			sio.write("BYTEBUFFER")
			writeInt(sio,len(data))
			sio.write(data.tostring())
		elif data.typecode == "f":
			writeByte(sio,VmVector)
			writeInt(sio,len(data))
			sio.write(data.tostring())
		else:
			print "Unsupported array typecode",data.typecode
	elif data is True:
		writeByte(sio,VmBool)
		writeByte(sio,1)
	elif data is False:
		writeByte(sio,VmBool)
		writeByte(sio,0)
	else:
		print "Unknown type",dt
		writeByte(sio,VmVoid)

# 0xFF XVR_02 0xFF size(DWORD network) 0xFF flaglen(1) flagdatadata(flaglen) 0xFF data(size)
def decodeMessageFlagged(data):
	flaglength = struct.unpack("b",data[13])[0]
	flagdata = data[14:14+flaglength]
	return decode(cStringIO.StringIO(data[14+flaglength+1:])),flagdata
def toHex(s):
    lst = []
    for ch in s:
        hv = hex(ord(ch)).replace('0x', '')
        if len(hv) == 1:
            hv = '0'+hv
        lst.append(hv)
    
    return reduce(lambda x,y:x+y, lst)

def recvmessage(xs):
	try:
		r = xs.recv(13)
	except:
		return None
	if r[0:8] == "\xFFXVR_02\xFF":
		d = struct.unpack("!l",r[9:13])[0]
		r = r + xs.recv(d)
		return decodeMessage(r)
	else:
		return None

# 0xFF XVR_02 0xFF size(DWORD network) 0xFF flaglen(1) flagdatadata(flaglen) 0xFF data(size)
def decodeMessage(data):
	flaglength = struct.unpack("b",data[13])[0]
	flagdata = data[14:14+flaglength]
	return decode(cStringIO.StringIO(data[14+flaglength+1:]))

def encodeRoom(room):
	sio1 = cStringIO.StringIO()
	if room != "":
		s = "\xff"+struct.pack("b",len(room)+1)+room+"\xff"
	else:
		s = "\xff0\xff"
	sio1.write("\xffXVR_02\xff")
	writeInt(sio1,len(s)+4+8)
	sio1.write(s)
	return sio1.getvalue()
#__NETWORK_VAR_HEADER__ ,sizeof(__NETWORK_VAR_HEADER__)-3
#\0\xFF
#data
#then fix size at pB+__SIZE__NETWORK_VAR_HEADER__
# __NETWORK_VAR_HEADER__ = \xffXVR_02\xff\0\0\0\0\xff\0\xff\0 (is a c string)
# __NETWORK_VAR_HEADER__ - 3 is = \xffXVR_02\xff\0\0\0\0\xff
# __SIZE__NETWORK_VAR_HEADER__ = \xffXVR_02\xff
# room is written as:
# strlen data \xFF
def encodeMessage(data):
	sio = cStringIO.StringIO()
	encode(sio,data)
	d = sio.getvalue()
	sio1 = cStringIO.StringIO()
	sio1.write("\xffXVR_02\xff")
	writeInt(sio1,len(d)+4+8+3) # payload + noroom + header + size
	sio1.write("\xff\x00\xff") #end size, room name is length 0 and then end port
	sio1.write(d) # payload
	xd = sio1.getvalue()
	return xd
def vector(data):
	return array.array("f",data)
if __name__ == "__main__":
	def testEncodeDecode(s,x):
		a = encodeMessage(x)
		y = decodeMessage(a)
		print "Test",s,"with",x,"gives",y," that is equal?",y == x
	testEncodeDecode("void",None)
	testEncodeDecode("bool",True)
	testEncodeDecode("bool",False)
	testEncodeDecode("int",10)
	testEncodeDecode("float",10.3)
	testEncodeDecode("string","Hello World")
	testEncodeDecode("tuple",(1,2,3,4,1))
	testEncodeDecode("list",[1,2,3,"Woooo"])
	a = array.array("f")
	a.fromlist([1,2,3,5,1])
	testEncodeDecode("array",a)
	a = array.array("b")
	a.fromstring("COOL")
	testEncodeDecode("arraybyte",a)
	testEncodeDecode("dictionary",{"A":10,"B":20,"C":"Hello"})

def qtcheck():
	global qtchecked,hasqt
	if qtchecked:
		return
	qtchecked = True
	try:
		hasqt = False
		import PyQt4
		hasqt = True
	except:
		pass
	
def wxcheck():
	global XVRDataEvent,EVT_XVRDATA,wxchecked,wx
	if wxchecked:
		return wx
	wxchecked = True
	try:
		haswx = False
		import wx
		import wx.lib.newevent
		haswx = True
		(XVRDataEvent, EVT_XVRDATA) = wx.lib.newevent.NewEvent()
	except:
		pass

class DataWriter:
	def __init__(self,port,host="127.0.0.1"):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.s.connect((host, port))
	def write(self,data):
		self.s.send(encodeMessage(data))
class DataReader:
    def __init__(self, target,port):
        self.keepGoing = True
        self.target = target
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind(("",port))
    def Start(self):
        self.keepGoing = self.running = True
        thread.start_new_thread(self.Run, ())
    def Stop(self): 
        if self.keepGoing:
           self.keepGoing = False
           self.s.close()
           time.sleep(0.01)
    def __del__(self):
        self.Stop()
    def IsRunning(self):
        return self.running
    def Run(self):
        while self.keepGoing:
            msg = ""
            try:
              msg = self.s.recv(32768*2) # TODO increase size and manage for timeout
            except:
              pass
            try:
             if msg != "":
                self.OnMessage(decodeMessage(msg))                   
            except:
                print sys.exc_info()
        self.s.close()
        self.running = False
	def OnMessage(self,msg):
		self.target(msg,self)

def DataReaderWx(target,port):
	wxcheck()
	import wx
	class DataReaderWxX(DataReader):
		def __init__(self, target,port):
			DataReader.__init__(self,target,port)
		def OnMessage(self,msg):
			global XVRDataEvent
			evt = XVRDataEvent(data = msg,source = self)
			wx.PostEvent(self.target, evt)
	return DataReaderWxX(target,port)
	
def DataReaderQt(target,port):
	qtcheck()
	from PyQt4 import QtGui
	from PyQt4 import QtCore
	class DataReaderQtX(DataReader):
		def __init__(self, target,port):
			DataReader.__init__(self,target,port)
		def OnMessage(self,msg):
			# TODO: in the future use the signal/slot mechanism. Sorry
			self.target.onXVRData(msg)
	return DataReaderQtX(target,port)

def autoguiqt(target):
	qtcheck()
	from PyQt4 import QtGui
	class AutoGui:
		def __init__(self,target):
			self.target = target
			self.lay = QtGui.QGridLayout()
			self.col = 0
			self.row = 0
			self.target.setLayout(self.lay)
		def slider(self,name,range):
			pass
		def textmenu(self,name,list):
			pass
		def edittext(self,name,default):
			pass
		def numericmenu(self,name,range):
			pass
		def pushbutton(self,name):
			button = QtGui.QPushButton(name)
			self.lay.addWidget(button,self.col,self.row)
			self.row = self.row + 1
		def checkbox(self,name):
			button = QtGui.QPushButton(name)
			self.lay.addWidget(button,self.col,self.row)
			self.row = self.row + 1
		def space(self,amount):
			pass
	return AutoGui(target)