#================= Copyright Valve Corporation, All rights reserved. ==============================
#
# Purpose: SFM utility script which moves the parent of the selected dag node to the world space
# position of the dag node without modifiying the animation of its children
#
#==================================================================================================

dagNode = sfm.FirstSelectedDag()
parent = dagNode.GetParent()
print parent.GetName()

# Move the children into world space while maintaining their world space animation 
sfm.ClearSelection()
sfmUtils.SelectChildren( parent )
sfm.Parent( world=True, maintainWorldPos=True, logMode=vs.REPARENT_LOGS_MAINTAIN_WORLD )

# Hold the selected dag node where it is
sfm.PushSelection()

sfm.SelectDag( dagNode )
targetPos = sfm.GetPosition()

sfm.ClearSelection()
sfm.SelectDag( parent )
sfm.SetOperationMode( "Record" )   
sfm.Move( targetPos[ 0 ], targetPos[ 1 ], targetPos[ 2 ], offsetMode=True )
sfm.SetOperationMode( "Pass" )
sfm.PopSelection()

# Reparent the children back to the dag node 
sfm.SelectDag( parent )
sfm.Parent( world=False, maintainWorldPos=True, logMode=vs.REPARENT_LOGS_MAINTAIN_WORLD )

