import serial
import obd_io
import time
import string
import wx

class main():
		
	def __init__(self):	
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

			for port in self.available:
				print("Available ports: " + str(port))
		
				try:
					self.elm = serial.Serial(port, parity = serial.PARITY_NONE, stopbits = 1, bytesize = 8, timeout = 1)
					print(self.elm.is_open)
				except serial.SerialException as e:
					print(e)

			try: 
				if self.elm:
					#self.initialize()
					#reset all
					#self.elm.write(b"ATZ\r\n")
					#x = self.elm.readline()

					#x = self.read_cmd()
					#print(x)
								

					#linefeed on
					#self.elm.write(b"ATL1\r\n")
					#x = self.elm.readline()
					#x = self.read_cmd()
					#print(x)

					self.send_command("010C")
					#self.send_command("010D")
					while 1:
						time.sleep(.1)
						self.send_command("")
						x = self.read_cmd()
						x = self.interpret(x)
						#x = self.getRPM(x)
						print(x)
							
			except serial.SerialException as e:
				print(e)


	def initialize(self):
		self.elm.flushInput()
		self.elm.flushOutput()

		#reset all
		self.elm.write(b"ATZ\r\n")
		#x = self.elm.readline()
		x = self.read_cmd()
		print(x)

		#echo off
		self.elm.write(b"ATE0\r\n")
		#x = self.elm.readline()
		x = self.read_cmd()
		print(x)

		#headers off
		self.elm.write(b"ATH0\r\n")
		#x = self.elm.readline()
		x = self.read_cmd()
		print(x)

		#linefeeds off
		self.elm.write(b"ATL0\r\n")
		#x = self.elm.readline()
		x = self.read_cmd()
		print(x)

		#Set protocol to automatic
		self.elm.write(b"ATSP0\r\n")
		x = self.elm.readline()
		print(x)

		#print the version ID
		self.elm.write(b"ATI\r\n")
		x = self.elm.readline()
		print(x)

		#read signal level at pin 15
		self.elm.write(b"ATIGN\r\n")
		x = self.read_cmd()
		print(x)

		self.elm.write(b"0100\r\n")
		x = self.elm.readline()
		print(x)


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

	def getRPM(self, str):

		rpm = int(resData, 16) / 4
		return rpm

	#def getSpeed(self, resData):



class Frame(wx.Frame):
     def __init__(self, parent, title):
         wx.Frame.__init__(self, parent=parent, title=title)

         # Create status bar
         self.CreateStatusBar()
         self.SetStatusText("Welcome to my fkin project mate!")

         # Create the panel
         self.panel = wx.Panel(self, -1, size=wx.Size(1000,800))
         self.panel.SetBackgroundColour(wx.NamedColour("grey"))

         #box = wx.BoxSizer(wx.HORIZONTAL)
         #box.Add(self.panel, 1, wx.EXPAND)
         #self.SetSizerAndFit(box)

class MyApp(wx.App):
     def OnInit(self):
         frame = Frame(parent=None, title='Resize Panel')
         frame.Show()
         self.SetTopWindow(frame)
         start = main()
         return True


if __name__ == '__main__':
     app = MyApp(False)
     app.MainLoop()





