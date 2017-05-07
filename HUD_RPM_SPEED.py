from threading import *
import wx
import time
import serial
import string

EVT_RESULT_ID = wx.NewId()
EVT_CONNECT_ID = wx.NewId()
EVT_SPEED_ID = wx.NewId()

def EVT_RESULT(win, func):
	win.Connect(-1,-1, EVT_RESULT_ID, func)

def EVT_CONNECT(win, func):
	win.Connect(-1,-1, EVT_CONNECT_ID, func)

def EVT_SPEED(win, func):
	win.Connect(-1,-1, EVT_SPEED_ID, func)

class ResultEvent(wx.PyEvent):

	def __init__(self, data):
		wx.PyEvent.__init__(self)
		self.SetEventType(EVT_RESULT_ID)
		self.data = data

class ConnectEvent(wx.PyEvent):

	def __init__(self, data):
		wx.PyEvent.__init__(self)
		self.SetEventType(EVT_CONNECT_ID)
		self.data = data

class SpeedEvent(wx.PyEvent):

	def __init__(self, data):
		wx.PyEvent.__init__(self)
		self.SetEventType(EVT_CONNECT_ID)
		self.data = data


class WorkerThread(Thread):

	def __init__(self, notify_window, port_connected, which_worker):
		Thread.__init__(self)

		self._notify_window = notify_window
		self._port_connected = port_connected 
		self._which_worker = which_worker

		#self.start()

	def run(self):

			self.available = []
			#connection = obd_io.OBDPort("/dev/rfcomm5");s
			for i in range(256):
				try:
					self.s = serial.Serial("/dev/rfcomm"+str(i))
					self.available.append(self.s.portstr)
					self.s.close()
				except serial.SerialException:
					pass


			baud = 9600;

			if not self._port_connected:
				for port in self.available:
					print("Available ports: " + str(port))
					wx.PostEvent(self._notify_window, ConnectEvent(port))
		
					try:
						serialLock.aqcuire()
						self.elm = serial.Serial(port, parity = serial.PARITY_NONE, stopbits = 1, bytesize = 8, timeout = 1)
						print(self.elm.is_open)
						self._port_connected = True
						serialLock.release()
					except serial.SerialException as e:
						print(e)

			try: 
				if self.elm:
					#needed every once and a while to reset config
					#self.initialize()

					#reset all every once and a while 
					#self.elm.write(b"ATZ\r\n")
					#x = self.read_cmd()
					#print(x)
								

					#linefeed on
					self.elm.write(b"ATL1\r\n")
					#x = self.elm.readline()
					x = self.read_cmd()
					print(x)
					oldData = 0

					#rpm command 
					if self._which_worker = "rpm_worker":
						self.send_command("010C")
					else:
						self.send_command("010D")

					while 1:
						time.sleep(.1)
						self.send_command("")
						data = self.read_cmd()
						newData = self.interpret(data)
						#x = self.getRPM(x)
						print(newData)

						
						if data != "None" or data != "" or data != " ":
							oldData = newData
							if self._which_worker == "rpm_worker":
								wx.PostEvent(self._notify_window, ResultEvent(newData))
							else:
								wx.PostEvent(self._notify_window, SpeedEvent(newData))
						else:
							if self._which_worker == "rpm_worker":
								wx.PostEvent(self._notify_window, ResultEvent(oldData))
							else:
								wx.PostEvent(self._notify_window, SpeedEvent(oldData))

			except serial.SerialException as e:
				print(e)


	



	def send_command(self, cmd):
			#checking to make sure port is still open
			
			if self.elm:
				self.elm.flushOutput()
				self.elm.flushInput()

				#for c in cmd:
				self.elm.write(cmd)
				self.elm.write("\r\n")
				
			"""	while 1:
					
					c = self.elm.read(1)
					if c != "\r":
						buff += c
					else:
						break

				print(buff)"""


	def read_cmd(self):
			#checking to make sure port is still open 
			time.sleep(0.1)
			#self.elm.flush()
			buffer = ""
			if self.elm:
				while 1:
					
					c = self.elm.read(1)
					
					
					buffer += c


					if c == "\r":
						#print(buffer)
						break

				#print(buffer)
				return buffer
			else:
				return None



	def interpret(self, response):

		#Since response from ELM327 comes in as "41 0C 0A B4 00 00\r" (RPM example, code: 010C)
		#'4' in 410C indicates is a response to our cmd
		response = string.split(response, "\r")
		response = response[0] #since we only want the first part of that split

		response = string.split(response) #removes whitespace
		response = string.join(response, "")

		response = response[4:8] #only want the actual data, not elm's response indicator 

		if response == "PED":
			return None

		#simple way to capture rpm
		if len(response) >= 3 or response != '':
			rpm = int(response, 16) / 4
			return rpm

		return response



class Frame(wx.Frame):

	def __init__(self, parent, id):

		wx.Frame.__init__(self, parent, id, "OBD Reader")
		self.status = wx.StaticText(self, -1, '', pos=(0,100))
		self.rpm = wx.StaticText(self, -1,'', pos = (0, 150))
		self.speed = wx.StaticText(self, -1, '', pos = (0, 200))

		EVT_RESULT(self, self.onResult)
		EVT_CONNECT(self, self.onConnect)
		EVT_SPEED(self, self.onSpeed)

		self.rpm_worker = WorkerThread(self, False, "rpm_worker")
		self.speed_worker = WorkerThread(self, True, "speed_worker")

		serialLock = threading.Lock()

		self.rpm_worker.start()
		self.speed_worker.start()




	def onResult(self, event):

		if event.data is None:
			self.rpm.SetLabel("RETRIEVING...")
		else:
			self.rpm.SetLabel("RPM: %s" % event.data )

		#self.worker = None #change later to create new thread again
		#self.worker = WorkerThread(self)  #restarting thread to get rpm again



	def onConnect(self, event):

		if event.data is None:
			self.status.SetLabel("Couldn't connect...")
		else:
			self.status.SetLabel("Port connected: %s" % event.data )

		#self.worker = WorkerThread(self, True) #change later to create new thread again

	def onSpeed(self, event):

		if event.data  is None:
			self.speed.SetLabel("SPEED:  RETRIEVING...")
		else:
			self.speed.SetLabel("SPEED: %s" % event.data)



class myApp(wx.App):
	#Initialize myApp class and wx stuff
	def OnInit(self):

		self.frame = Frame(None, -1)
		self.frame.Show(True)
		#self.SetTopWindow(self.frame)
		return True

if __name__ == '__main__':
	app = myApp(0)
	app.MainLoop()

