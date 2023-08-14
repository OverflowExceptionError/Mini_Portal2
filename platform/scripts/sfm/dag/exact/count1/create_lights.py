#================= Copyright Valve Corporation, All rights reserved. ==============================
#
# Purpose: Sfm light setup script wich creates a set of 4 lights (key, rim, fill, and bounce) 
# around the currently selected target. All of the lights are constructed as children of the 
# light root, so that the lights can be positioned or re-oriented using a the single root node.
# A 'lightKit' animation set is created for this root node in along with to the animation sets for
# each light. In addition providing controls for the root node the lightKit animation set contains
# a master color which may be used to override the individuals colors of all the lights.
#
#==================================================================================================


#==================================================================================================
def CreateMasterColorBlend( lightAnimSet, colorName, colorizeConn, controlGroup, animSet, shot ):
    '''Create an master color for the specified color component and the expresion which will 
    evaluate the blend between the master color and the local light color'''
        
    # Create the expresion to blend between the local color and the master color. 
    # The attributes used in the expression must be explicitly added to the expression operator
    colorExprName = "lightColorExpr_" + colorName
    colorExpr = sfmUtils.CreateExpression( colorExprName, "lerp( colorize, localColor, masterColor )", animSet )
    colorExpr.SetValue( "localColor",  1.0 )
    colorExpr.SetValue( "masterColor", 1.0 )
    colorExpr.SetValue( "colorize",    1.0 )
    
    # Create a control and channel for the specified component of the master color. 
    # The control is added to the animation set so that it may be used to modify the 
    # values stored in the log belonging to the channel that was created.
    masterColorControlName = "masterColor_" + colorName
    masterColorControl = sfmUtils.CreateControlAndChannel( masterColorControlName, vs.AT_FLOAT, 1.0, animSet, shot )
    
    # Set the target of the channel to be the masterColor attribute of the color blend expression
    masterColorControl.channel.toElement = colorExpr
    masterColorControl.channel.toAttribute = "masterColor"
        
    # Re-route the channel to drive the expression value instead of the color pack operator value
    colorControlName = "color_" + colorName;
    colorControl = lightAnimSet.FindControl( colorControlName )
    colorPackOperator = colorControl.channel.toElement
    colorControl.channel.toElement = colorExpr
    colorControl.channel.toAttribute = "localColor"

    # Connect the result of color expression to the color component attribute of the color pack 
    # operator. "result" is the name of the attribute which is a member of all expression operators 
    # where the result of the expression is stored.
    colorExprConnName = "colorExprConn_" + colorName
    colorExprConn = sfmUtils.CreateConnection( colorExprConnName, colorExpr, "result", animSet )
    colorExprConn.AddOutput( colorPackOperator, colorName )

    # Add the new control to the specified control group, this makes 
    # the control show up in the ui under the specified control group.
    controlGroup.AddControl( masterColorControl )
    
    # Add an output to the colorize connection that drives the value from the colorize 
    # control to the colorize attribute of the color blend expression
    colorizeConn.AddOutput( colorExpr, "colorize" )
    
    return
#==================================================================================================


#==================================================================================================
def CreateLight( lightKitAnimSet, controlGroup, colorizeConn, parent, lightName, rx, ry, rz, dist=100, intensity=1.0, color=vs.Color( 255, 255, 255 ), castsShadows=False, uberLight=True, quadraticAttenuation = 600, volumetric=False, farZAtten=600, radius=0 ):
    '''Create a light which with the specified name, rotation and distance from the center of the 
    parent. Creates an animation set for the light wich is the return value of the function'''

    
    # Create the light 
    newLight = vs.CreateElement( "DmeProjectedLight", lightName, parent.GetFileId() )
    # newLight.drawShadowFrustum = 1
    
 		#connect variables
    newLight.uberlight = uberLight
    newLight.castsShadows = castsShadows
    newLight.intensity = intensity
    newLight.color = color
    newLight.volumetric = volumetric 
    newLight.farZAtten = farZAtten 
    newLight.quadraticAttenuation = quadraticAttenuation
    newLight.radius = radius


    #set default override values
    newLight.cutOn = 50
    newLight.cutOff = 200
    newLight.constantAttenuation = 0
    newLight.linearAttenuation = 0 
    newLight.minDistance = 50 
    newLight.maxDistance = 300 
    newLight.width = 0
    newLight.height = 0
    newLight.edgeWidth = 0.25
    newLight.edgeHeight = 0.25     
    newLight.edgeWidth = 0.25
    newLight.edgeHeight = 0.25   

         
    # Add the light to the specified parent
    parent.children.AddToTail( newLight )
    
    # Create a new animation set for the light
    animSet = sfm.CreateAnimationSet( lightName, target=newLight )

    # Rotate the light and the move it back the specified distance
    sfm.SetOperationMode( "record" )
    sfm.ClearSelection()
    sfm.SelectDag( newLight )
    sfm.Rotate( rx, ry, rz, space="parent" )
    sfm.Move( -dist, 0, 0, space="object" )
    sfm.SetOperationMode( "pass" )

    # Re-position the pivot offset of light transform control so that it is at the 
    # orgin of the parent, making it convient to rotate the light around the target.
    transformControl = animSet.FindControl( "transform" );
    transformControl.SetPivotOffset( vs.Vector( dist, 0, 0 ) );
    #transformControlRot = animSet.FindControl( "transform - rot" );
    #transformControlRot.SetPivotOffset( vs.Vector( dist, 0, 0 ) );
    
    # Connect the master color blend controls
    shot = sfm.GetCurrentShot()
    CreateMasterColorBlend( animSet, "red",   colorizeConn, controlGroup, lightKitAnimSet, shot )
    CreateMasterColorBlend( animSet, "green", colorizeConn, controlGroup, lightKitAnimSet, shot )
    CreateMasterColorBlend( animSet, "blue",  colorizeConn, controlGroup, lightKitAnimSet, shot )
    
    return animSet
#==================================================================================================


#==================================================================================================
def ReparentToWorld( dagNode ):
    '''Re-parent the specified dag node to the world, removing it from its current parent and 
    making it a child of the scene while maintain its world space position and orientation'''

    sfm.ClearSelection()
    sfm.SelectDag( dagNode )
    sfm.Parent( world=True )
    shot.scene.children.AddToTail( dagNode )    
    return
#==================================================================================================





#==================================================================================================
# Script entry
#==================================================================================================

# Get the currently selected shot, and then bet the current active camera from the shot
shot = sfm.GetCurrentShot()
camera = shot.camera

# Get the first dag in the current selection, this is the dag around which the light setup will be centered
targetDag = sfm.FirstSelectedDag()
pos = sfm.GetPosition() 
targetPos = vs.Vector( pos[ 0 ], pos[ 1 ], pos[ 2 ] )

# Create a dag node which will serve as the parent of the all of the lights and add the new node to the scene
lightRoot = vs.CreateElement( "DmeDag", "lightRoot", shot.GetFileId() )
lightRoot.SetAbsPosition( vs.Vector( pos[ 0 ], pos[ 1 ], pos[ 2 ] ) )
print lightRoot
shot.scene.AddChild( lightRoot )

# Reposition the light root to the position of the target dag
lightRoot.SetAbsPosition( targetPos )

# Aim constrain the light root to the camera so that it will rotate based on the camera position
sfm.ClearSelection()
sfm.SelectDag( camera )
sfm.SelectDag( lightRoot )
sfm.AimConstraint()


# Point constrain the light root to the target so that it will move based on the target position
sfm.ClearSelection()
sfm.SelectDag( targetDag )
sfm.SelectDag( lightRoot )
sfm.PointConstraint()

# Create the animation set for the light root control
lightKitAnimSet = sfm.CreateAnimationSet( "lightKit", target=lightRoot )
rootGroup = lightKitAnimSet.GetRootControlGroup()
	    

# Create the colorize control, value element and channel. Then add the colorize
# control to the control group so that it will be displayed in the ui.
colorizeControl, colorizeValue = sfmUtils.CreateControlledValue( "colorize", "value", vs.AT_FLOAT, 0.0, lightKitAnimSet, shot )
rootGroup.AddControl( colorizeControl )

# Create a connection operator which will be used to connect the colorize value to each of the color component blend expressions
colorizeConn = sfmUtils.CreateConnection( "colorizeConn", colorizeValue, "value", lightKitAnimSet )


# Create the lights
CreateLight( lightKitAnimSet, rootGroup, colorizeConn, lightRoot, "keyLight",     0,   45,  -25, intensity = 150, castsShadows = True, color = vs.Color( 227, 149, 150 ), volumetric = True, farZAtten = 300, radius=7 )
CreateLight( lightKitAnimSet, rootGroup, colorizeConn, lightRoot, "bounceLight",  0,  -70,  -120, intensity = 12, castsShadows = True, color = vs.Color( 150, 227, 227 ) )
CreateLight( lightKitAnimSet, rootGroup, colorizeConn, lightRoot, "fillLight",    0,  -12,  -135, intensity = 10, castsShadows = True, color = vs.Color( 255, 255, 255 ), farZAtten = 150 )
CreateLight( lightKitAnimSet, rootGroup, colorizeConn, lightRoot, "rimLight",     0,   15,    60, intensity = 700, castsShadows = True, farZAtten = 150 )



                         
# Destroy the aim constraint, if this is removed the constraint will remain active and
# moving the camera will rotate all the lights around the target position
sfm.ClearSelection()
sfm.SelectDag( lightRoot )
sfm.RemoveConstraints()

#==================================================================================================






























