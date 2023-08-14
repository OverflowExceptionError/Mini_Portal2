#================= Copyright Valve Corporation, All rights reserved. ==============================
#
# Purpose: SFM utlities script to create an parent constraint with the current selection ( last 
# selected is constrained between the other selections ). The maintain offset option (mo) is set to 
# true so that the constrained dag will maintain its current world space position and orientation 
# at the current time.
#
#==================================================================================================

sfm.ParentConstraint( mo=True )
