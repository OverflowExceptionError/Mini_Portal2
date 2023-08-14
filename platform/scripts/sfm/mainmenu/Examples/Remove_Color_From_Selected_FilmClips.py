import vs
import sfmApp
import sfmClipEditor
from PySide import QtGui

if sfmApp.HasDocument():
	shots = sfmClipEditor.GetSelectedShots()
	nCounter = 0
	for shot in shots:
		shot.color = vs.Color( 0, 0, 0, 0 )
		nCounter += 1
	message = "Removed color in %d shots" % nCounter
	QtGui.QMessageBox.information( None, " ", message )
else:
	QtGui.QMessageBox.information( None, " ", "No current document..." )