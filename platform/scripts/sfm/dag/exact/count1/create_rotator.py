#================= Copyright Valve Corporation, All rights reserved. ==============================
#
# Purpose: 
#
#==================================================================================================

shot = sfm.GetCurrentShot()
animSet = sfm.GetCurrentAnimationSet()
targetDag = sfm.FirstSelectedDag()

# Create the rotation constraint and attach it the the target dag node 
constraintName = targetDag.GetName() + "_rotationConstraint"
rotationAxis = vs.Vector( 1, 0, 0 )
rotationConstraint = sfmUtils.CreateRotationConstraint( constraintName, rotationAxis, targetDag, animSet )

# Create a control and channel to drive the rotation value
controlName = targetDag.GetName() + "_rotationValue"
rotationControl = sfmUtils.CreateControlAndChannel( controlName, vs.AT_FLOAT, 0, animSet, shot )

# Now add the new control to the control group associated
# with the dag so that it is displayed in the animation set editor
controlGroup = animSet.FindControlGroupForDag( targetDag )
controlGroup.AddControl( rotationControl )

# Create an expression to map the 0 to 1 range of the sider to a more reasonable range for the rotation
rescaleExprName = targetDag.GetName() + "_rotationRescale"
rescaleExpr = sfmUtils.CreateExpression( rescaleExprName, "lerp(value, lo, hi)", animSet )
sfmUtils.AddAttributeToElement( rescaleExpr, "hi", vs.AT_FLOAT, 360 )
sfmUtils.AddAttributeToElement( rescaleExpr, "lo", vs.AT_FLOAT, 0 )
sfmUtils.AddAttributeToElement( rescaleExpr, "value", vs.AT_FLOAT, 0 )
#rescaleExpr.SetValue( "hi", 360.0 )
#rescaleExpr.SetValue( "lo", 0.0 )
#rescaleExpr.SetValue( "value", 0.0 )

# Set the output of the rotaiton control to be the inpute value of the rotation rescale expression
rotationControl.channel.toElement = rescaleExpr
rotationControl.channel.toAttribute = "value"

# Create a connection from the result of the remap expression to the rotation value of the rotation constraint
rotationConnName = targetDag.GetName() + "_rotationConn"
rotationConn = sfmUtils.CreateConnection( rotationConnName, rescaleExpr, "result", animSet )
rotationConn.AddOutput( rotationConstraint, "rotations", 0 )



