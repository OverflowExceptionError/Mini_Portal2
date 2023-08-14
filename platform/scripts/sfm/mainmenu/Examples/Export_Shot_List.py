import sfmApp
import csv
from PySide import QtGui

filename, _  = QtGui.QFileDialog.getSaveFileName( None, 'Export Shot List ', 'C:\export.csv')
if filename:
	fps = sfmApp.GetFramesPerSecond()
	framerate = vs.DmeFramerate_t( fps )

	with open( filename, 'wb') as csvfile:
		spamwriter = csv.writer( csvfile, delimiter=',', quotechar='\'', quoting=csv.QUOTE_MINIMAL)
		spamwriter.writerow( ['Name', 'Artist', 'Start Time', 'Duration' ] )

		shots = sfmApp.GetShots()
		for shot in shots:
			nStartFrame = shot.GetStartTime().CurrentFrame( framerate, 0 )
			nDuration =  shot.GetDuration().CurrentFrame( framerate, 0 );
			spamwriter.writerow( [ shot.name, shot.text, nStartFrame, nDuration ] )
