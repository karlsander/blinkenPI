import xml.etree.ElementTree as ET
import sys, serial, time


class Movie(object):
	"""Class for and Animation. A collection of frames and Settings."""
	def __init__(self):
		self.frames = []
		self.length = 0
		self.settings = {}


	def addframe(self, toadd):
		self.frames.append(toadd)
		self.length = self.length + 1

	def __str__(self):
		rep = ''
		for frame in self.frames:
			rep = rep + "Frame that will be shown for %s seconds: \n" % frame.time
			if(type(frame) is Frame):
				for row in frame.rows:
					rep = rep + row + "\n"
			if(type(frame) is PIFrame):
				rep = rep + frame.framebuffer + "\n"
		
		return rep


class Frame(object):
	"""A Frame with indivdual rows as used in the blm file."""
	def __init__(self):
		self.rows = []
		self.time = 0
		self.number_rows = 0


	def addrow(self, toadd):
		self.rows.append(toadd)
		self.number_rows = self.number_rows + 1


class PIFrame(object):
	"""A frame with all the rows consolidated into a framebuffer content that can be sent to the PI Lite 
	This String isn't a concatination of the rows but the columns. It can only contain 0 for off and 1 for on pixels."""
	def __init__(self):
		self.framebuffer = '000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
		self.time = 0


def checkSettings(tocheck):
	"""Checks the settings of the file and gives the user hints on how to make a better suited animation"""
	if(tocheck['width'] > 14):
		print "Your animation is too wide. It will be cropped. Ideal width is 14 pixels."

	if(tocheck['width'] < 14):
		print("Your animation is not wide enough. Part of the matrix will remain off. Ideal width is 14 pixels.")

	if(tocheck['height'] > 9):
		print("Your animation is too high. It will be cropped. Ideal height is 9 pixels.")

	if(tocheck['height'] < 9):
		print("Your animation is not high enough. Part of the matrix will remain off. Ideal height is 9 pixels.")


def parseBML(file):
	"""Function to parse a blm file into a 'Movie' object with 'Frame' frames.
	Takes filename as argument"""
	document = ET.parse(file)
	animation = document.getroot()

	if(animation.tag != 'blm'):
		print "Sorry, can't find blm root. Looks like this is not a valid blinkenmovie file"
		sys.exit()

	m = Movie()

	# get settings from the attributes of the root tag
	m.settings = animation.attrib
	# add the text of the 'loop' tag inside the header to the settings dictionary
	m.settings['loop'] = animation.find('header').find('loop').text

	checkSettings(m.settings)

	# go through all the frames and all the in each frame and add them to the Movie object
	for frame in animation.findall('frame'):
		f = Frame()
		for row in frame.findall('row'):
			f.addrow(row.text)
		f.time = frame.attrib['duration']
		m.addframe(f)
		
	return m


def setupPILite():
	"""Sets up the serial connection to the Pi Lite."""
	s = serial.Serial()
	s.baudrate = 9600
	s.timeout = 0
	s.port = "/dev/ttyAMA0"

	try:
		s.open()
	except serial.SerialException, e:
		sys.stderr.write("could not open port %r: %s\n" % (s.port, e))
		sys.exit(1)

	return s


def convert(toconvert):
	"""Takes a Movie object with frames of type 'Frame' and returns a movie object with frames of type 'PIFrame'.
	To do this it converts the rows found in the frame into a string that can be sent to the framebuffer of the PI Lite"""
	pi = Movie()
	pi.settings = toconvert.settings

	for frame in toconvert.frames:
		pif = PIFrame()
		pif.time = frame.time
		framebuffer = ""
		#This strange construction takes the n'th pixel from each row and adds them together to form a column.
		#All the columns together make for the framebuffer string
		#This is only done for the first 14 columns and 9 rows because thats all the PI Lite can display
		for x in range(0,14):
			number_rows = 0
			for row in frame.rows:
				number_rows = number_rows + 1
				if (number_rows < 10):
					if(row[x] == '0'):
						framebuffer = framebuffer + '0'
					else:
						framebuffer = framebuffer + '1'
			#Fill the rest of each column with zeros
			while(number_rows <= 9):
				framebuffer = framebuffer + '0'
				number_rows = number_rows + 1
		#Fill the Remaining columns with zeros
		while(len(framebuffer) < 126):
			framebuffer = framebuffer + '0'

		pif.framebuffer = framebuffer

		pi.addframe(pif)

	return pi


def play(matrix, movie):
	""" Plays an animation of type 'Movie' with frames of type 'PIFrame' on the PI Lite"""
	if (movie.settings['loop'] == 'yes'):
		print "The animation will loop forever. To quit hit CTRL+C"

	while True:
		for frame in movie.frames:
			sleeptime = float(frame.time) / 1000.0
			matrix.write('$$$F' + frame.framebuffer + '\r')
			time.sleep(sleeptime)

		if (movie.settings['loop'] == 'no'):
			break


if (len(sys.argv) == 1):
	print "You need to run this script with a filename. Example: 'python blinkenpi.py test.bml'"
	sys.exit()

if (len(sys.argv) == 2):
	script, filename = sys.argv

if (len(sys.argv) > 2):
	print "Thats to many arguments. You need to run this script with one argument: the filename of the animation you want to play. Example: 'python blinkenpi.py test.bml'"
	sys.exit()

m = parseBML(filename)
pi = convert(m)

lite = setupPILite()

play(lite, pi)