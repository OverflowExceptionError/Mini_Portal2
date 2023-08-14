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
    bonePelvis    = sfmUtils.FindFirstDag( [ "root" ], True )
	
    boneUpperLegR = sfmUtils.FindFirstDag( [ "rLeg02" ], True )
    boneLowerLegR = sfmUtils.FindFirstDag( [ "rLeg03" ], True )
    boneFootR     = sfmUtils.FindFirstDag( [ "rLeg04" ], True )
   
    boneUpperArmR = sfmUtils.FindFirstDag( [ "turretArm01" ], True ) 
    boneLowerArmR = sfmUtils.FindFirstDag( [ "turretArm02" ], True )
    boneHandR     = sfmUtils.FindFirstDag( [ "turretArm03" ], True )
   
    boneUpperLegL = sfmUtils.FindFirstDag( [ "lLeg02" ], True )
    boneLowerLegL = sfmUtils.FindFirstDag( [ "lLeg03" ], True )
    boneFootL     = sfmUtils.FindFirstDag( [ "lLeg04" ], True )
	
    boneXRotator = sfmUtils.FindFirstDag( [ "upper_telescope_01" ], True )
    boneYRotator = sfmUtils.FindFirstDag( [ "fork_base" ], True )	
    boneHinge = sfmUtils.FindFirstDag( [ "fork_turretHinge" ], True )
    boneMuzzle = sfmUtils.FindFirstDag( [ "turret_muzzle" ], True )
    boneLateralBase = sfmUtils.FindFirstDag( [ "LateralBase" ], True )
    #==============================================================================================
    # Create the rig handles and constrain them to existing bones
    #==============================================================================================
    rigRoot    = sfmUtils.CreateConstrainedHandle( "rig_root",     boneRoot,    bCreateControls=False )
    rigPelvis  = sfmUtils.CreateConstrainedHandle( "rig_pelvis",   bonePelvis,  bCreateControls=False )
    
    rigHipR   = sfmUtils.CreateConstrainedHandle( "rig_hip_R",   boneUpperLegR,   bCreateControls=False )
    rigFootR   = sfmUtils.CreateConstrainedHandle( "rig_foot_R",   boneFootR, bCreateControls=False )
    rigHandR   = sfmUtils.CreateConstrainedHandle( "rig_hand",   boneHandR,   bCreateControls=False )
    rigHipL   = sfmUtils.CreateConstrainedHandle( "rig_hip_L",   boneUpperLegL,   bCreateControls=False )
    rigFootL   = sfmUtils.CreateConstrainedHandle( "rig_foot_L",   boneFootL, bCreateControls=False )
		
    rigKneeR   = sfmUtils.CreateOffsetHandle( "rig_knee_R",  boneLowerLegR, vs.Vector( -5, 5, 0 ),  bCreateControls=False )   
    rigKneeL   = sfmUtils.CreateOffsetHandle( "rig_knee_L",  boneLowerLegL, vs.Vector( 5, 5, 0 ),  bCreateControls=False )
	  		
    rigXRotator  = sfmUtils.CreateConstrainedHandle( "rig_XRotator",   boneXRotator,  bCreateControls=False )
    rigYRotator  = sfmUtils.CreateConstrainedHandle( "rig_YRotator",   boneYRotator,  bCreateControls=False )
    rigHinge  = sfmUtils.CreateConstrainedHandle( "rig_hinge",   boneHinge,  bCreateControls=False )
    rigMuzzle  = sfmUtils.CreateConstrainedHandle( "rig_Muzzle",   boneMuzzle,  bCreateControls=False )
    rigLateralBase  = sfmUtils.CreateConstrainedHandle( "rig_LateralBase",   boneLateralBase,  bCreateControls=False )
	
    rigElbowR  = sfmUtils.CreateOffsetHandle( "rig_elbow", boneLowerArmR, vs.Vector( 0, 0, 0 ),  bCreateControls=False )
	
    # Create a helper handle which will remain constrained to the each foot position that can be used for parenting.
    rigFootHelperR = sfmUtils.CreateConstrainedHandle( "rig_footHelper_R", boneFootR, bCreateControls=False )
    rigFootHelperL = sfmUtils.CreateConstrainedHandle( "rig_footHelper_L", boneFootL, bCreateControls=False )
    #rigFootHelperM = sfmUtils.CreateConstrainedHandle( "rig_footHelper_M", boneFootM, bCreateControls=False )
    # Create a list of all of the rig dags
    # allRigHandles = [ rigRoot, rigPelvis, rigSpine0, rigSpine1, rigSpine2, rigChest, rigNeck, rigHead,
    #                   rigCollarR, rigElbowR, rigHandR, rigKneeR, rigFootR, rigToeR,
    #                   rigCollarL, rigElbowL, rigHandL, rigKneeL, rigFootL, rigToeL ];
    allRigHandles = [ rigRoot, rigPelvis,
                       rigHipR, rigKneeR, rigFootR,
                       rigHipL, rigKneeL, rigFootL,
                       rigXRotator, rigYRotator, rigHinge, rigMuzzle,
                       rigElbowR, rigHandR, rigLateralBase ];
    
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
    sfmUtils.ParentMaintainWorld( rigFootHelperR,   rigRoot )
    sfmUtils.ParentMaintainWorld( rigFootHelperL,   rigRoot )
    sfmUtils.ParentMaintainWorld( rigFootR,         rigRoot )
    sfmUtils.ParentMaintainWorld( rigFootL,         rigRoot )	
    sfmUtils.ParentMaintainWorld( rigKneeR,         rigFootR )
    sfmUtils.ParentMaintainWorld( rigKneeL,         rigFootL )	
    sfmUtils.ParentMaintainWorld( rigHipR,          rigPelvis )
    sfmUtils.ParentMaintainWorld( rigHipL,          rigPelvis )
    sfmUtils.ParentMaintainWorld( rigXRotator,         rigPelvis )
    sfmUtils.ParentMaintainWorld( rigYRotator,         rigXRotator )	
    sfmUtils.ParentMaintainWorld( rigHinge,         rigYRotator )	
    sfmUtils.ParentMaintainWorld( rigMuzzle,         rigHinge )	
    sfmUtils.ParentMaintainWorld( rigLateralBase,         rigRoot )	
    sfmUtils.ParentMaintainWorld( rigElbowR,        rigXRotator )
    sfmUtils.ParentMaintainWorld( rigHandR,	        rigHinge )
    
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
    
    footIKTargetR = rigFootR
    footIkTargetL = rigFootL
    
    if ( gameModel != None ) :
        footRollIkTargetR = CreateReverseFoot( "rig_footRoll", "R", gameModel, animSet, shot, rigHelpersGroup, rigLegsGroup )
        footRollIkTargetL = CreateReverseFoot( "rig_footRoll", "L", gameModel, animSet, shot, rigHelpersGroup, rigLegsGroup )
        if ( footRollIkTargetR != None ) :
            footIKTargetR = footRollIkTargetR
        if ( footRollIkTargetL != None ) :
            footIkTargetL = footRollIkTargetL
   
    
    #==============================================================================================
    # Create constraints to drive the bone transforms using the rig handles
    #==============================================================================================
    
    # The following bones are simply constrained directly to a rig handle
    sfmUtils.CreatePointOrientConstraint( rigRoot,      boneRoot        )
    sfmUtils.CreatePointOrientConstraint( rigPelvis,    bonePelvis      )
    sfmUtils.CreatePointOrientConstraint( rigHipR,      boneUpperLegR   )
    sfmUtils.CreatePointOrientConstraint( rigHipL,      boneUpperLegL   )
	
    sfmUtils.CreatePointOrientConstraint( rigXRotator,         boneXRotator )
    sfmUtils.CreatePointOrientConstraint( rigYRotator,         boneYRotator )	
    sfmUtils.CreatePointOrientConstraint( rigHinge,         boneHinge )	
    sfmUtils.CreatePointOrientConstraint( rigMuzzle,         boneMuzzle )	
    sfmUtils.CreatePointOrientConstraint( rigLateralBase,         boneLateralBase )
    # Create ik constraints for the arms and legs that will control the rotation of the hip / knee and 
    # upper arm / elbow joints based on the position of the foot and hand respectively.
    sfmUtils.BuildArmLeg( rigKneeR,  footIKTargetR, boneUpperLegR,  boneFootR, True )
    sfmUtils.BuildArmLeg( rigKneeL,  footIkTargetL, boneUpperLegL,  boneFootL, True )
    sfmUtils.BuildArmLeg( rigElbowR, rigHandR, boneUpperArmR,  boneHandR, True )
    
    
    #==============================================================================================
    # Create handles for the important attachment points 
    #==============================================================================================    
    attachmentGroup = rootGroup.CreateControlGroup( "Attachments" )  
    attachmentGroup.SetVisible( False )
    
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_heel_R",       attachmentGroup )
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_toe_R",        attachmentGroup )
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_outerFoot_R",  attachmentGroup )
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_innerFoot_R",  attachmentGroup )
    
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_heel_L",       attachmentGroup )
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_toe_L",        attachmentGroup )
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_outerFoot_L",  attachmentGroup )
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_innerFoot_L",  attachmentGroup )
       
    
    
    #==============================================================================================
    # Re-organize the selection groups
    #==============================================================================================  
    rigBodyGroup = rootGroup.CreateControlGroup( "RigBody" )
    rigArmsGroup = rootGroup.CreateControlGroup( "RigArms" )
    
    RightArmGroup = rootGroup.CreateControlGroup( "RightArm" )
    LeftArmGroup = rootGroup.CreateControlGroup( "LeftArm" )
    BackArmGroup = rootGroup.CreateControlGroup( "BackArm" )
    RightLegGroup = rootGroup.CreateControlGroup( "RightLeg" )
    LeftLegGroup = rootGroup.CreateControlGroup( "LeftLeg" )     
    sfmUtils.AddDagControlsToGroup( rigBodyGroup, rigRoot, rigPelvis, rigXRotator, rigYRotator, rigHinge, rigMuzzle, rigLateralBase )  
  
    rigArmsGroup.AddChild( BackArmGroup )
    sfmUtils.AddDagControlsToGroup( BackArmGroup, rigHandR, rigElbowR )  
	
    rigLegsGroup.AddChild( RightLegGroup )
    rigLegsGroup.AddChild( LeftLegGroup )
    sfmUtils.AddDagControlsToGroup( RightLegGroup, rigHipR, rigKneeR, rigFootR )
    sfmUtils.AddDagControlsToGroup( LeftLegGroup, rigHipL, rigKneeL, rigFootL )
	
    sfmUtils.MoveControlGroup( "rig_footRoll_L", rigLegsGroup, LeftLegGroup )
    sfmUtils.MoveControlGroup( "rig_footRoll_R", rigLegsGroup, RightLegGroup )
	
    sfmUtils.AddDagControlsToGroup( rigHelpersGroup, rigFootHelperR, rigFootHelperL )

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
    RightColor = vs.Color( 255, 0, 0, 255 )
    LeftColor = vs.Color( 0, 255, 0, 255 )
    MidColor = vs.Color( 0, 0, 255, 255 )
	
    rigBodyGroup.SetGroupColor( topLevelColor, False )
    rigArmsGroup.SetGroupColor( topLevelColor, False )
    rigLegsGroup.SetGroupColor( topLevelColor, False )
    attachmentGroup.SetGroupColor( topLevelColor, False )
    rigHelpersGroup.SetGroupColor( topLevelColor, False )
    

    RightLegGroup.SetGroupColor( RightColor, False )
    LeftLegGroup.SetGroupColor( LeftColor, False )
    BackArmGroup.SetGroupColor( MidColor, False )
    
    # End the rig definition
    sfm.EndRig()
    return
    
#==================================================================================================
# Script entry
#==================================================================================================

# Construct the rig for the selected animation set
BuildRig();


    
    



