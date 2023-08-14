import vs

#==================================================================================================
def AddValidObjectToList( objectList, obj ):
    if ( obj != None ): objectList.append( obj )
    

#==================================================================================================
def HideControlGroups( rig, rootGroup, *groupNames ):
    for name in groupNames:    
        group = rootGroup.FindChildByName( name, False )
        if ( group != None ):
            rig.HideControlGroup( group )

    
#==================================================================================================
# Create the reverse foot control and operators for the foot on the specified side
#==================================================================================================
def CreateReverseFoot( controlName, sideName, gameModel, animSet, shot, helperControlGroup, footControlGroup ) :
    
    # Cannot create foot controls without heel position, so check for that first
    heelAttachName = "pvt_heel_" + sideName
    if ( gameModel.FindAttachment( heelAttachName ) == 0 ):
        print "Could not create foot control " + controlName + ", model is missing heel attachment point: " + heelAttachName;
        return None
    
    footRollDefault = 0.5
    rotationAxis = vs.Vector( 1, 0, 0 )
        
    # Construct the name of the dag nodes of the foot and toe for the specified side
    footName = "rig_foot_" + sideName
    toeName = "rig_toe_" + sideName    
    
    # Get the world space position and orientation of the foot and toe
    footPos = sfm.GetPosition( footName )
    footRot = sfm.GetRotation( footName )
    toePos = sfm.GetPosition( toeName )
    
    # Setup the reverse foot hierarchy such that the foot is the parent of all the foot transforms, the 
    # reverse heel is the parent of the heel, so it can be used for rotations around the ball of the 
    # foot that will move the heel, the heel is the parent of the foot IK handle so that it can perform
    # rotations around the heel and move the foot IK handle, resulting in moving all the foot bones.
    # root
    #   + rig_foot_R
    #       + rig_knee_R
    #       + rig_reverseHeel_R
    #           + rig_heel_R
    #               + rig_footIK_R
    
  
    # Construct the reverse heel joint this will be used to rotate the heel around the toe, and as
    # such is positioned at the toe, but using the rotation of the foot which will be its parent, 
    # so that it has no local rotation once parented to the foot.
    reverseHeelName = "rig_reverseHeel_" + sideName
    reverseHeelDag = sfm.CreateRigHandle( reverseHeelName, pos=toePos, rot=footRot, rotControl=False )
    sfmUtils.Parent( reverseHeelName, footName, vs.REPARENT_LOGS_OVERWRITE )
    
    
    
    # Construct the heel joint, this will be used to rotate the foot around the back of the heel so it 
    # is created at the heel location (offset from the foot) and also given the rotation of its parent.
    heelName = "rig_heel_" + sideName
    vecHeelPos = gameModel.ComputeAttachmentPosition( heelAttachName )
    heelPos = [ vecHeelPos.x, vecHeelPos.y, vecHeelPos.z ]     
    heelRot = sfm.GetRotation( reverseHeelName )
    heelDag = sfm.CreateRigHandle( heelName, pos=heelPos, rot=heelRot, posControl=True, rotControl=False )
    sfmUtils.Parent( heelName, reverseHeelName, vs.REPARENT_LOGS_OVERWRITE )
    
    # Create the ik handle which will be used as the target for the ik chain for the leg
    ikHandleName = "rig_footIK_" + sideName   
    ikHandleDag = sfmUtils.CreateHandleAt( ikHandleName, footName )
    sfmUtils.Parent( ikHandleName, heelName, vs.REPARENT_LOGS_OVERWRITE )
                    
    # Create an orient constraint which causes the toe's orientation to match the foot's orientation
    footRollControlName = controlName + "_" + sideName
    toeOrientTarget = sfm.OrientConstraint( footName, toeName, mo=True, controls=False )
    footRollControl, footRollValue = sfmUtils.CreateControlledValue( footRollControlName, "value", vs.AT_FLOAT, footRollDefault, animSet, shot )
    
    # Create the expressions to re-map the footroll slider value for use in the constraint and rotation operators
    toeOrientExprName = "expr_toeOrientEnable_" + sideName    
    toeOrientExpr = sfmUtils.CreateExpression( toeOrientExprName, "inrange( footRoll, 0.5001, 1.0 )", animSet )
    toeOrientExpr.SetValue( "footRoll", footRollDefault )
    
    toeRotateExprName = "expr_toeRotation_" + sideName
    toeRotateExpr = sfmUtils.CreateExpression( toeRotateExprName, "max( 0, (footRoll - 0.5) ) * 140", animSet )
    toeRotateExpr.SetValue( "footRoll", footRollDefault )
                            
    heelRotateExprName = "expr_heelRotation_" + sideName
    heelRotateExpr = sfmUtils.CreateExpression( heelRotateExprName, "max( 0, (0.5 - footRoll) ) * -100", animSet )
    heelRotateExpr.SetValue( "footRoll", footRollDefault )
        
    # Create a connection from the footroll value to all of the expressions that require it
    footRollConnName = "conn_footRoll_" + sideName
    footRollConn = sfmUtils.CreateConnection( footRollConnName, footRollValue, "value", animSet )
    footRollConn.AddOutput( toeOrientExpr, "footRoll" )
    footRollConn.AddOutput( toeRotateExpr, "footRoll" )
    footRollConn.AddOutput( heelRotateExpr, "footRoll" )
    
    # Create the connection from the toe orientation enable expression to the target weight of the 
    # toe orientation constraint, this will turn the constraint on an off based on the footRoll value
    toeOrientConnName = "conn_toeOrientExpr_" + sideName;
    toeOrientConn = sfmUtils.CreateConnection( toeOrientConnName, toeOrientExpr, "result", animSet )
    toeOrientConn.AddOutput( toeOrientTarget, "targetWeight" )
    
    # Create a rotation constraint to drive the toe rotation and connect its input to the 
    # toe rotation expression and connect its output to the reverse heel dag's orientation
    toeRotateConstraintName = "rotationConstraint_toe_" + sideName
    toeRotateConstraint = sfmUtils.CreateRotationConstraint( toeRotateConstraintName, rotationAxis, reverseHeelDag, animSet )
    
    toeRotateExprConnName = "conn_toeRotateExpr_" + sideName
    toeRotateExprConn = sfmUtils.CreateConnection( toeRotateExprConnName, toeRotateExpr, "result", animSet )
    toeRotateExprConn.AddOutput( toeRotateConstraint, "rotations", 0 );

    # Create a rotation constraint to drive the heel rotation and connect its input to the 
    # heel rotation expression and connect its output to the heel dag's orientation 
    heelRotateConstraintName = "rotationConstraint_heel_" + sideName
    heelRotateConstraint = sfmUtils.CreateRotationConstraint( heelRotateConstraintName, rotationAxis, heelDag, animSet )
    
    heelRotateExprConnName = "conn_heelRotateExpr_" + sideName
    heelRotateExprConn = sfmUtils.CreateConnection( heelRotateExprConnName, heelRotateExpr, "result", animSet )
    heelRotateExprConn.AddOutput( heelRotateConstraint, "rotations", 0 )
    
    if ( helperControlGroup != None ):
        sfmUtils.AddDagControlsToGroup( helperControlGroup, reverseHeelDag, ikHandleDag, heelDag )       
    
    if ( footControlGroup != None ):
        footControlGroup.AddControl( footRollControl )
        
    return ikHandleDag


#==================================================================================================
# Build a simple ik rig for the currently selected animation set
#==================================================================================================
def BuildRig():
    
    # Get the currently selected animation set and shot
    shot = sfm.GetCurrentShot()
    animSet = sfm.GetCurrentAnimationSet()
    gameModel = animSet.gameModel
    rootGroup = animSet.GetRootControlGroup()
    
    # Start the biped rig to which all of the controls and constraints will be added
    rig = sfm.BeginRig( "rig_biped_" + animSet.GetName() );
    if ( rig == None ):
        return
    
    # Change the operation mode to passthrough so changes chan be made temporarily
    sfm.SetOperationMode( "Pass" )
    
    # Move everything into the reference pose
    sfm.SelectAll()
    sfm.SetReferencePose()
    
    #==============================================================================================
    # Find the dag nodes for all of the bones in the model which will be used by the script
    #==============================================================================================
    boneRoot      = sfmUtils.FindFirstDag( [ "RootTransform" ], True )
    bonePelvis    = sfmUtils.FindFirstDag( [ "Base" ], True )
    boneSpine0    = sfmUtils.FindFirstDag( [ "Aim_LR" ], True )

	
    boneUpperLegR = sfmUtils.FindFirstDag( [ "Right_leg" ], True )
    boneLowerLegR = sfmUtils.FindFirstDag( [ "Right_rotator" ], True )
    boneFootR     = sfmUtils.FindFirstDag( [ "Right_foot" ], True )
	
    boneCollarR   = sfmUtils.FindFirstDag( [ "RT_Wing_Rotator" ], True )   

    boneHandR     = sfmUtils.FindFirstDag( [ "RT_Wing" ], True )
   
    boneUpperLegL = sfmUtils.FindFirstDag( [ "Left_leg" ], True )
    boneLowerLegL = sfmUtils.FindFirstDag( [ "Left_rotator" ], True )
    boneFootL     = sfmUtils.FindFirstDag( [ "Left_foot" ], True )

    boneCollarL   = sfmUtils.FindFirstDag( [ "LFT_Wing_Rotator" ], True )   

    boneHandL     = sfmUtils.FindFirstDag( [ "LFT_Wing" ], True )
    
    boneUpperLegM = sfmUtils.FindFirstDag( [ "back_leg" ], True )
    boneLowerLegM = sfmUtils.FindFirstDag( [ "back_leg_rotator" ], True )
    boneFootM     = sfmUtils.FindFirstDag( [ "back_leg_foot1" ], True )

	
    boneFootPLM = sfmUtils.FindFirstDag( [ "back_leg_footPlatform" ], True )
    boneFootPLL = sfmUtils.FindFirstDag( [ "Left_foot_platform" ], True )	
    boneFootPLR = sfmUtils.FindFirstDag( [ "Right_foot_platform" ], True )
	
    boneLidUpper = sfmUtils.FindFirstDag( [ "Lid_Upper" ], True )
    boneLidLower = sfmUtils.FindFirstDag( [ "Lid_Lower" ], True )
	
    boneEye = sfmUtils.FindFirstDag( [ "eyeball_bone" ], True )
    boneEyeLight = sfmUtils.FindFirstDag( [ "eyeball_light" ], True )
	
    boneRTgun1 = sfmUtils.FindFirstDag( [ "RT_Gun1" ], True )
    boneRTgun2 = sfmUtils.FindFirstDag( [ "RT_Gun2" ], True )
    boneLFTgun1 = sfmUtils.FindFirstDag( [ "LFT_Gun1" ], True )
    boneLFTgun2 = sfmUtils.FindFirstDag( [ "LFT_Gun2" ], True )
    #==============================================================================================
    # Create the rig handles and constrain them to existing bones
    #==============================================================================================
    rigRoot    = sfmUtils.CreateConstrainedHandle( "rig_root",     boneRoot,    bCreateControls=False )
    rigPelvis  = sfmUtils.CreateConstrainedHandle( "rig_base",   bonePelvis,  bCreateControls=False )
    rigSpine0  = sfmUtils.CreateConstrainedHandle( "rig_Aim",  boneSpine0,  bCreateControls=False )

    rigLidUpper  = sfmUtils.CreateConstrainedHandle( "rig_upper_lid",  boneLidUpper,  bCreateControls=False )
    rigLidLower  = sfmUtils.CreateConstrainedHandle( "rig_lower_lid",  boneLidLower,  bCreateControls=False )
	
    rigEye = sfmUtils.CreateConstrainedHandle( "rig_eye",  boneEye,  bCreateControls=False )
    rigEyeLight = sfmUtils.CreateConstrainedHandle( "rig_iris",  boneEyeLight,  bCreateControls=False )
	
    rigRTgun1 = sfmUtils.CreateConstrainedHandle( "rig_RT_Gun1",  boneRTgun1,  bCreateControls=False )
    rigRTgun2 = sfmUtils.CreateConstrainedHandle( "rig_RT_Gun2",  boneRTgun2,  bCreateControls=False )
    rigLFTgun1 = sfmUtils.CreateConstrainedHandle( "rig_LFT_Gun1",  boneLFTgun1,  bCreateControls=False )
    rigLFTgun2 = sfmUtils.CreateConstrainedHandle( "rig_LFT_Gun2",  boneLFTgun2,  bCreateControls=False )
	
    rigHipR   = sfmUtils.CreateConstrainedHandle( "rig_legbase_R",   boneUpperLegR,   bCreateControls=False )
    rigFootR  = sfmUtils.CreateOffsetHandle( "rig_joint_R",   boneFootR, vs.Vector( 0, 0,  5 ),  bCreateControls=False)
    rigCollarR = sfmUtils.CreateConstrainedHandle( "rig_wing_rotator_R", boneCollarR, bCreateControls=False )
    rigHandR   = sfmUtils.CreateConstrainedHandle( "rig_wing_R",   boneHandR,   bCreateControls=False )
	
    rigHipL   = sfmUtils.CreateConstrainedHandle( "rig_legbase_L",   boneUpperLegL,   bCreateControls=False )
    rigFootL  = sfmUtils.CreateOffsetHandle( "rig_joint_L",   boneFootL, vs.Vector( 0, 0,  5 ),  bCreateControls=False)
    rigCollarL = sfmUtils.CreateConstrainedHandle( "rig_wing_rotator_L", boneCollarL, bCreateControls=False )
    rigHandL   = sfmUtils.CreateConstrainedHandle( "rig_wing_L",   boneHandL,   bCreateControls=False )
        
    rigHipM   = sfmUtils.CreateConstrainedHandle( "rig_legbase_M",   boneUpperLegM,   bCreateControls=False )
    rigFootM   = sfmUtils.CreateOffsetHandle( "rig_joint_M", boneFootM, vs.Vector( 0, 0,  5 ),  bCreateControls=False)
		

	
    rigFootPlatformR = sfmUtils.CreateConstrainedHandle( "rig_foot_R",  boneFootPLR,  bCreateControls=False )   
    rigFootPlatformL = sfmUtils.CreateConstrainedHandle( "rig_foot_L",  boneFootPLL,  bCreateControls=False )
    rigFootPlatformM = sfmUtils.CreateConstrainedHandle( "rig_foot_M",  boneFootPLM,  bCreateControls=False )   	

    
    # Create a helper handle which will remain constrained to the each foot position that can be used for parenting.
    rigFootHelperR = sfmUtils.CreateConstrainedHandle( "rig_footHelper_R", boneFootPLR, bCreateControls=False )
    rigFootHelperL = sfmUtils.CreateConstrainedHandle( "rig_footHelper_L", boneFootPLL, bCreateControls=False )
    rigFootHelperM = sfmUtils.CreateConstrainedHandle( "rig_footHelper_M", boneFootPLM, bCreateControls=False )
    # Create a list of all of the rig dags
    # allRigHandles = [ rigRoot, rigPelvis, rigSpine0, rigSpine1, rigSpine2, rigChest, rigNeck, rigHead,
    #                   rigCollarR, rigElbowR, rigHandR, rigKneeR, rigFootR, rigToeR,
    #                   rigCollarL, rigElbowL, rigHandL, rigKneeL, rigFootL, rigToeL ];
    allRigHandles = [ rigRoot, rigPelvis, rigSpine0, rigEye, rigEyeLight, rigLidUpper, rigLidLower,
                       rigCollarR, rigHandR, rigHipR, rigFootR, rigFootPlatformR, rigRTgun1, rigRTgun2,
                       rigCollarL, rigHandL, rigHipL, rigFootL, rigFootPlatformL, rigLFTgun1, rigLFTgun2,
                       rigHipM, rigFootM, rigFootPlatformM ];
    
    #==============================================================================================
    # Generate the world space logs for the rig handles and remove the constraints
    #==============================================================================================
    sfm.ClearSelection()
    sfmUtils.SelectDagList( allRigHandles )
    sfm.GenerateSamples()
    sfm.RemoveConstraints()    
    
    
    #==============================================================================================
    # Build the rig handle hierarchy
    #==============================================================================================
    sfmUtils.ParentMaintainWorld( rigPelvis,        rigRoot )
    sfmUtils.ParentMaintainWorld( rigSpine0,        rigPelvis )
    
    sfmUtils.ParentMaintainWorld( rigFootPlatformR,   rigRoot )
    sfmUtils.ParentMaintainWorld( rigFootPlatformL,   rigRoot )
    sfmUtils.ParentMaintainWorld( rigFootPlatformM,   rigRoot )
    sfmUtils.ParentMaintainWorld( rigFootHelperR,   rigRoot )
    sfmUtils.ParentMaintainWorld( rigFootHelperL,   rigRoot )
    sfmUtils.ParentMaintainWorld( rigFootHelperM,   rigRoot )
    sfmUtils.ParentMaintainWorld( rigHipR,          rigPelvis )
    sfmUtils.ParentMaintainWorld( rigHipL,          rigPelvis )	
    sfmUtils.ParentMaintainWorld( rigHipM,          rigPelvis )
    sfmUtils.ParentMaintainWorld( rigFootR,         rigHipR )
    sfmUtils.ParentMaintainWorld( rigFootL,         rigHipL )	
    sfmUtils.ParentMaintainWorld( rigFootM,         rigHipM )

    sfmUtils.ParentMaintainWorld( rigEye,          rigPelvis )
    sfmUtils.ParentMaintainWorld( rigEyeLight,          rigEye )
	
    sfmUtils.ParentMaintainWorld( rigLidUpper,          rigPelvis )
    sfmUtils.ParentMaintainWorld( rigLidLower,          rigPelvis )
	
    sfmUtils.ParentMaintainWorld( rigLFTgun1,          rigHandL )
    sfmUtils.ParentMaintainWorld( rigLFTgun2,          rigHandL )
    sfmUtils.ParentMaintainWorld( rigRTgun1,          rigHandR )
    sfmUtils.ParentMaintainWorld( rigRTgun2,          rigHandR )
	
    sfmUtils.ParentMaintainWorld( rigCollarR,       rigSpine0 )	
    sfmUtils.ParentMaintainWorld( rigHandR,	        rigCollarR )
    sfmUtils.ParentMaintainWorld( rigCollarL,       rigSpine0 )	
    sfmUtils.ParentMaintainWorld( rigHandL,	        rigCollarL )
    
    # Create the hips control, this allows a pelvis rotation that does not effect the spine,
    # it is only used for rotation so a position control is not created. Additionally add the
    # new control to the selection so the that set default call operates on it too.
    
    #rigHips = sfmUtils.CreateHandleAt( "rig_hips", rigPelvis, False, True )
    #sfmUtils.Parent( rigHips, rigPelvis, vs.REPARENT_LOGS_OVERWRITE )
    #sfm.SelectDag( rigHips )

    # Set the defaults of the rig transforms to the current locations. Defaults are stored in local
    # space, so while the parent operation tries to preserve default values it is cleaner to just
    # set them once the final hierarchy is constructed.
    sfm.SetDefault()
    
    
    #==============================================================================================
    # Create the reverse foot controls for both the left and right foot
    #==============================================================================================
    rigLegsGroup = rootGroup.CreateControlGroup( "RigLegs" )
    rigHelpersGroup = rootGroup.CreateControlGroup( "RigHelpers" )
    rigHelpersGroup.SetVisible( False )
    rigHelpersGroup.SetSnappable( False )
    
    footIKTargetR = rigFootPlatformR
    footIkTargetL = rigFootPlatformL
    footIkTargetM = rigFootPlatformM
    
    if ( gameModel != None ) :
        footRollIkTargetR = CreateReverseFoot( "rig_footRoll", "R", gameModel, animSet, shot, rigHelpersGroup, rigLegsGroup )
        footRollIkTargetL = CreateReverseFoot( "rig_footRoll", "L", gameModel, animSet, shot, rigHelpersGroup, rigLegsGroup )
        footRollIkTargetM = CreateReverseFoot( "rig_footRoll", "M", gameModel, animSet, shot, rigHelpersGroup, rigLegsGroup )
        if ( footRollIkTargetR != None ) :
            footIKTargetR = footRollIkTargetR
        if ( footRollIkTargetL != None ) :
            footIkTargetL = footRollIkTargetL
        if ( footRollIkTargetM != None ) :
            footIkTargetM = footRollIkTargetM
   
    
    #==============================================================================================
    # Create constraints to drive the bone transforms using the rig handles
    #==============================================================================================
    
    # The following bones are simply constrained directly to a rig handle
    sfmUtils.CreatePointOrientConstraint( rigRoot,      boneRoot        )
    sfmUtils.CreatePointOrientConstraint( rigPelvis,    bonePelvis      )
    sfmUtils.CreatePointOrientConstraint( rigSpine0,    boneSpine0      )
    sfmUtils.CreatePointOrientConstraint( rigHipR,      boneUpperLegR   )
    sfmUtils.CreatePointOrientConstraint( rigHipL,      boneUpperLegL   )
    sfmUtils.CreatePointOrientConstraint( rigHipM,      boneUpperLegM   )
    sfmUtils.CreatePointOrientConstraint( rigCollarR,   boneCollarR     )
    sfmUtils.CreatePointOrientConstraint( rigCollarL,   boneCollarL     )
    sfmUtils.CreatePointOrientConstraint( rigHandL,   boneHandL     )
    sfmUtils.CreatePointOrientConstraint( rigHandR,   boneHandR     )
	
    sfmUtils.CreatePointOrientConstraint( rigLFTgun1, boneLFTgun1 )
    sfmUtils.CreatePointOrientConstraint( rigLFTgun2, boneLFTgun2 )
    sfmUtils.CreatePointOrientConstraint( rigRTgun1, boneRTgun1 )	
    sfmUtils.CreatePointOrientConstraint( rigRTgun2, boneRTgun2 )
	
    sfmUtils.CreatePointOrientConstraint( rigLidUpper,  boneLidUpper )
    sfmUtils.CreatePointOrientConstraint( rigLidLower,  boneLidLower )
    sfmUtils.CreatePointOrientConstraint( rigEye,  boneEye )
    sfmUtils.CreatePointOrientConstraint( rigEyeLight,  boneEyeLight ) 
    
    # Create ik constraints for the arms and legs that will control the rotation of the hip / knee and 
    # upper arm / elbow joints based on the position of the foot and hand respectively.
    sfmUtils.BuildArmLeg( rigFootR,  footIKTargetR, boneLowerLegR,  boneFootPLR, True )
    sfmUtils.BuildArmLeg( rigFootL,  footIkTargetL, boneLowerLegL,  boneFootPLL, True )
    sfmUtils.BuildArmLeg( rigFootM,  footIkTargetM, boneLowerLegM,  boneFootPLM, True )
    
    
    #==============================================================================================
    # Create handles for the important attachment points 
    #==============================================================================================    
    attachmentGroup = rootGroup.CreateControlGroup( "Attachments" )  
    attachmentGroup.SetVisible( False )
    
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_heel_R",       attachmentGroup )

    sfmUtils.CreateAttachmentHandleInGroup( "pvt_outerFoot_R",  attachmentGroup )
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_innerFoot_R",  attachmentGroup )
    
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_heel_L",       attachmentGroup )

    sfmUtils.CreateAttachmentHandleInGroup( "pvt_outerFoot_L",  attachmentGroup )
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_innerFoot_L",  attachmentGroup )
     
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_heel_M",       attachmentGroup )

    sfmUtils.CreateAttachmentHandleInGroup( "pvt_outerFoot_M",  attachmentGroup )
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_innerFoot_M",  attachmentGroup )
    
    
    
    #==============================================================================================
    # Re-organize the selection groups
    #==============================================================================================  
    rigBodyGroup = rootGroup.CreateControlGroup( "RigBody" )
    rigArmsGroup = rootGroup.CreateControlGroup( "RigArms" )
    rigFaceGroup = rootGroup.CreateControlGroup( "RigEye" )
    RightArmGroup = rootGroup.CreateControlGroup( "RightArm" )
    LeftArmGroup = rootGroup.CreateControlGroup( "LeftArm" )
    RightLegGroup = rootGroup.CreateControlGroup( "RightLeg" )
    LeftLegGroup = rootGroup.CreateControlGroup( "LeftLeg" )    
    MidLegGroup = rootGroup.CreateControlGroup( "MidLeg" )   
    #sfmUtils.AddDagControlsToGroup( rigBodyGroup, rigRoot, rigPelvis, rigHips, rigSpine0, rigSpine1, rigSpine2, rigChest, rigNeck, rigHead )  
    sfmUtils.AddDagControlsToGroup( rigBodyGroup, rigRoot, rigPelvis, rigSpine0 )  
  
    rigArmsGroup.AddChild( RightArmGroup )
    rigArmsGroup.AddChild( LeftArmGroup )
    sfmUtils.AddDagControlsToGroup( RightArmGroup,  rigHandR, rigCollarR, rigRTgun1, rigRTgun2 )
    sfmUtils.AddDagControlsToGroup( LeftArmGroup, rigHandL, rigCollarL, rigLFTgun1, rigLFTgun2)
	
    sfmUtils.AddDagControlsToGroup( rigFaceGroup, rigLidUpper, rigLidLower, rigEye, rigEyeLight )
	
    rigLegsGroup.AddChild( RightLegGroup )
    rigLegsGroup.AddChild( LeftLegGroup )
    rigLegsGroup.AddChild( MidLegGroup )
    sfmUtils.AddDagControlsToGroup( RightLegGroup, rigHipR, rigFootR, rigFootPlatformR )
    sfmUtils.AddDagControlsToGroup( LeftLegGroup, rigHipL, rigFootL, rigFootPlatformL )
    sfmUtils.AddDagControlsToGroup( MidLegGroup, rigHipM, rigFootM, rigFootPlatformM )
	
    sfmUtils.MoveControlGroup( "rig_footRoll_L", rigLegsGroup, LeftLegGroup )
    sfmUtils.MoveControlGroup( "rig_footRoll_R", rigLegsGroup, RightLegGroup )
    sfmUtils.MoveControlGroup( "rig_footRoll_M", rigLegsGroup, MidLegGroup )
	
    sfmUtils.AddDagControlsToGroup( rigHelpersGroup, rigFootHelperR, rigFootHelperL, rigFootHelperM )

    # Set the control group visiblity, this is done through the rig so it can track which
    # groups it hid, so they can be set back to being visible when the rig is detached.
    HideControlGroups( rig, rootGroup, "Body", "Arms", "Legs", "Unknown", "Other", "Root" )      
        
    #Re-order the groups
    fingersGroup = rootGroup.FindChildByName( "Fingers", False ) 
    rootGroup.MoveChildToBottom( rigBodyGroup )
    rootGroup.MoveChildToBottom( rigLegsGroup )    
    rootGroup.MoveChildToBottom( rigArmsGroup )      
    rootGroup.MoveChildToBottom( fingersGroup )  
       
    rightFingersGroup = rootGroup.FindChildByName( "RightFingers", True ) 
    if ( rightFingersGroup != None ):
        RightArmGroup.AddChild( rightFingersGroup )
        rightFingersGroup.SetSelectable( False )
                                
    leftFingersGroup = rootGroup.FindChildByName( "LeftFingers", True ) 
    if ( leftFingersGroup != None ):
        LeftArmGroup.AddChild( leftFingersGroup )
        leftFingersGroup.SetSelectable( False )
        

    #==============================================================================================
    # Set the selection groups colors
    #==============================================================================================
    topLevelColor = vs.Color( 0, 128, 255, 255 )
    RightColor = vs.Color( 225, 143, 55, 255 )
    LeftColor = vs.Color( 7, 156, 226, 255 )
    MidColor = vs.Color( 204, 0, 255, 255 )
	
    rigBodyGroup.SetGroupColor( topLevelColor, False )
    rigArmsGroup.SetGroupColor( topLevelColor, False )
    rigLegsGroup.SetGroupColor( topLevelColor, False )
    rigFaceGroup.SetGroupColor( topLevelColor, False )
    attachmentGroup.SetGroupColor( topLevelColor, False )
    rigHelpersGroup.SetGroupColor( topLevelColor, False )
    
    RightArmGroup.SetGroupColor( RightColor, False )
    LeftArmGroup.SetGroupColor( LeftColor, False )
    RightLegGroup.SetGroupColor( RightColor, False )
    LeftLegGroup.SetGroupColor( LeftColor, False )
    MidLegGroup.SetGroupColor( MidColor, False )
    
    # End the rig definition
    sfm.EndRig()
    return
    
#==================================================================================================
# Script entry
#==================================================================================================

# Construct the rig for the selected animation set
BuildRig();


    
    




