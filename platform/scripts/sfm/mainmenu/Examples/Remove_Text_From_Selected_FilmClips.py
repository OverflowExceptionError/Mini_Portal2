import sfmApp
import sfmClipEditor
from PySide import QtGui

if sfmApp.HasDocument():
	shots = sfmClipEditor.GetSelectedShots()
	nCounter = 0
	for shot in shots:
		shot.text = ""
		nCounter += 1
	message = "Removed text in %d shots" % nCounter
	QtGui.QMessageBox.information( None, " ", message )
else:
	QtGui.QMessageBox.information( None, " ", "No current document..." )