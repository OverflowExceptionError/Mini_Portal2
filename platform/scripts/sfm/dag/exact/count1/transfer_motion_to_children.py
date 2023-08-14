#================= Copyright Valve Corporation, All rights reserved. ==============================
#
# Purpose: SFM utility script which transfers all motion from a dag node to all of its childern so
# that the motion of the node is elminated but that the child maintain thier world space motion.
#
#==================================================================================================

dagNode = sfm.FirstSelectedDag()

# Move the children into world space while maintaining their world space animation 
sfm.ClearSelection()
sfmUtils.SelectChildren( dagNode )
sfm.Parent( world=True, maintainWorldPos=True, logMode=vs.REPARENT_LOGS_MAINTAIN_WORLD )

# Hold the selected dag node where it is
sfm.PushSelection()
sfm.SelectDag( dagNode )
sfm.SetOperationMode( "Record" )         
sfm.Move( 0, 0, 0, relative=True )
sfm.SetOperationMode( "Pass" )
sfm.PopSelection()

# Reparent the children back to the dag node 
sfm.SelectDag( dagNode )
sfm.Parent( world=False, maintainWorldPos=True, logMode=vs.REPARENT_LOGS_MAINTAIN_WORLD )










