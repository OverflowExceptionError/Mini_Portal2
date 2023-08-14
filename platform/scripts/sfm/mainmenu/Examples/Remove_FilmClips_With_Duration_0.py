import sfmApp
import sfmClipEditor
from PySide import QtGui

if sfmApp.HasDocument():
	shots = sfmApp.GetShots()
	nCounter = 0
	for shot in shots:
		flDuration = shot.timeFrame.duration.GetValue().GetSeconds()
		if flDuration == 0.0:
			nCounter += 1
			track = sfmApp.GetParentTrack( shot )
			track.RemoveClip( shot ) 
	message = "Removed %d shots because of duration 0" % nCounter
	QtGui.QMessageBox.information( None, " ", message )
else:
	QtGui.QMessageBox.information( None, " ", "No current document..." )