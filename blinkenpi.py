import xml.etree.ElementTree as ET
import sys, serial, time

global settings

class PIMovie(object):
	def __init__(self):
		self.frames = []
		self.length = 0
		self.settings = {}

	def addframe(self, toadd):
		self.frames.append(toadd)
		self.length = self.length + 1


class PIFrame(object):
	def __init__(self):
		self.framebuffer = '000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
		self.time = 0


class Movie(object):
	def __init__(self):
		self.frames = []
		self.length = 0
		self.settings = {}

	def addframe(self, toadd):
		self.frames.append(toadd)
		self.length = self.length + 1


class Frame(object):
	def __init__(self):
		self.rows = []
		self.time = 0
		self.number_rows = 0

	def addrow(self, toadd):
		self.rows.append(toadd)
		self.number_rows = self.number_rows + 1


def checkSettings(tocheck):
	if(tocheck['width'] > 14):
		print "Your animation is too wide. It will be cropped. Ideal width is 14 pixels."

	if(tocheck['width'] < 14):
		print("Your animation is not wide enough. Part of the matrix will remain off. Ideal width is 14 pixels.")

	if(tocheck['height'] > 9):
		print("Your animation is too high. It will be cropped. Ideal height is 9 pixels.")

	if(tocheck['height'] < 9):
		print("Your animation is not high enough. Part of the matrix will remain off. Ideal height is 9 pixels.")

def parseBML(file):

	document = ET.parse(file)
	animation = document.getroot()

	if(animation.tag != 'blm'):
		print "Sorry, can't find blm root. Looks like this is not a valid blinkenmovie file"
		sys.exit()

	m = Movie()

	m.settings = animation.attrib

	checkSettings(m.settings)

	for frame in animation.findall('frame'):
		f = Frame()
		for row in frame.findall('row'):
			f.addrow(row.text)
		f.time = frame.attrib['duration']
		m.addframe(f)


	return m

def printMovie(toprint):
	for frame in toprint.frames:
		print frame.time
		for row in frame.rows:
			print row

def printPIMovie(toprint):
	for frame in toprint.frames:
		print frame.time
		print frame.framebuffer


def setupPILite():
	s = serial.Serial()
	s.baudrate = 9600
	s.timeout = 0
	s.port = "/dev/ttyAMA0"

	try:
		s.open()
	except serial.SerialException, e:
		sys.stderr.write("could not open port %r: %s\n" % (port, e))
		sys.exit(1)


	return s


def convert(toconvert):
	pi = PIMovie()
	pi.settings = toconvert.settings

	for frame in toconvert.frames:
		pif = PIFrame()
		pif.time = frame.time
		framebuffer = ""
		for x in range(0,14):
			number_rows = 0
			for row in frame.rows:
				number_rows = number_rows + 1
				if (number_rows < 10):
					if(row[x] == '0'):
						framebuffer = framebuffer + '0'
					else:
						framebuffer = framebuffer + '1'
			while(number_rows < 10):
				framebuffer = framebuffer + '0'
				number_rows = number_rows + 1


		while(len(framebuffer) < 126):
			framebuffer = framebuffer + '0'

		pif.framebuffer = framebuffer

		pi.addframe(pif)

	return pi

def play(matrix, movie):
	for frame in movie.frames:
		sleeptime = float(frame.time) / 1000.0
		matrix.write('$$$F' + frame.framebuffer + '\r')
		time.sleep(sleeptime)


script, filename = sys.argv

m = parseBML(filename)
pi = convert(m)

lite = setupPILite()

play(lite, pi)

