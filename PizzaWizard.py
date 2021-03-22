import pygame, sys
from pygame import *

#This funcion will parse a file and play the level
def fileparser(filename):
#Initial variables
	health = 10
	spells = []

#This section takes all of the information from the file with the 'with' statement
#-----------------------------------------------------------------------------------------------------------------------------------------------------
	try:
		with open(filename, 'rt') as fh:
			text = fh.read()
	except:
		print ('Coordinate file cannot be read. Terminating')
		sys.exit(1)
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#This part parses the information we got from the previous section
	coordinates = text.split('\n')
	del coordinates[-1]
	separated_coordinates = []
	for coordinate in coordinates:
		separated_coordinates.append(coordinate.split(':'))
	print (separated_coordinates)
#-----------------------------------------------------------------------------------------------------------------------------------------------------


fileparser("level1.py")
