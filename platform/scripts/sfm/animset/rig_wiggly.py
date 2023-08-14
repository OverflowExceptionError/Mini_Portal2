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
# Compute the direction from boneA to boneB
#==================================================================================================
def ComputeVectorBetweenBones( boneA, boneB, scaleFactor ):
    
    vPosA = vs.Vector( 0, 0, 0 )
    boneA.GetAbsPosition( vPosA )
    
    vPosB = vs.Vector( 0, 0, 0 )
    boneB.GetAbsPosition( vPosB )
    
    vDir = vs.Vector( 0, 0, 0 )
    vs.mathlib.VectorSubtract( vPosB, vPosA, vDir )
    vDir.NormalizeInPlace()
    
    vScaledDir = vs.Vector( 0, 0, 0 )
    vs.mathlib.VectorScale( vDir, scaleFactor, vScaledDir )    
    
    return vScaledDir
    
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
    boneRoot      = sfmUtils.FindFirstDag( [ "rootTransform" ], True )

    boneSpine1 = sfmUtils.FindFirstDag( [ "Bone01" ], True )
    boneSpine2 = sfmUtils.FindFirstDag( [ "Bone02" ], True )
    boneSpine3  = sfmUtils.FindFirstDag( [ "Bone03" ], True )

    boneSpine4 = sfmUtils.FindFirstDag( [ "Bone04" ], True )
    boneSpine5 = sfmUtils.FindFirstDag( [ "Bone05" ], True )
    boneSpine6  = sfmUtils.FindFirstDag( [ "Bone06" ], True )

    boneSpine7 = sfmUtils.FindFirstDag( [ "Bone07" ], True )
    boneSpine8 = sfmUtils.FindFirstDag( [ "Bone08" ], True )
    boneSpine9  = sfmUtils.FindFirstDag( [ "Bone09" ], True )

    boneSpine10 = sfmUtils.FindFirstDag( [ "Bone10" ], True )
    boneSpine11= sfmUtils.FindFirstDag( [ "Bone11" ], True )
    boneSpine12  = sfmUtils.FindFirstDag( [ "Bone12" ], True )

    boneSpine13 = sfmUtils.FindFirstDag( [ "Bone13" ], True )
    boneSpine14 = sfmUtils.FindFirstDag( [ "Bone14" ], True )
    boneSpine15  = sfmUtils.FindFirstDag( [ "Bone15" ], True )

    boneHead     = sfmUtils.FindFirstDag( [ "Bone16" ], True )
   

    #==============================================================================================
    # Create the rig handles and constrain them to existing bones
    #==============================================================================================
    rigRoot    = sfmUtils.CreateConstrainedHandle( "rig_root",     boneRoot,    bCreateControls=False )
	
    rigSpine1  = sfmUtils.CreateConstrainedHandle( "rig_spine1",   boneSpine1,  bCreateControls=False )
    rigSpine3   = sfmUtils.CreateConstrainedHandle( "rig_spine3",   boneSpine3,   bCreateControls=False )
	
    rigSpine4  = sfmUtils.CreateConstrainedHandle( "rig_spine4",   boneSpine4,  bCreateControls=False )
    rigSpine6   = sfmUtils.CreateConstrainedHandle( "rig_spine6",   boneSpine6,   bCreateControls=False )

    rigSpine7  = sfmUtils.CreateConstrainedHandle( "rig_spine7",   boneSpine7,  bCreateControls=False )
    rigSpine9   = sfmUtils.CreateConstrainedHandle( "rig_spine9",   boneSpine9,   bCreateControls=False )	
	
    rigSpine10  = sfmUtils.CreateConstrainedHandle( "rig_spine10",   boneSpine10,  bCreateControls=False )
    rigSpine12   = sfmUtils.CreateConstrainedHandle( "rig_spine12",   boneSpine12,   bCreateControls=False )
	
    rigSpine13  = sfmUtils.CreateConstrainedHandle( "rig_spine13",   boneSpine13,  bCreateControls=False )
    rigSpine15   = sfmUtils.CreateConstrainedHandle( "rig_spine15",   boneSpine15,   bCreateControls=False )
	
    rigHead   = sfmUtils.CreateConstrainedHandle( "rig_Head",   boneHead,   bCreateControls=False )
  
    
    # Use the direction from the heel to the toe to compute the knee offsets, 
    # this makes the knee offset indpendent of the inital orientation of the model.
    vOffset1 = ComputeVectorBetweenBones( boneSpine3, boneSpine2, 10 )
    vOffset2 = ComputeVectorBetweenBones( boneSpine6, boneSpine5, 10 )
    vOffset3 = ComputeVectorBetweenBones( boneSpine9, boneSpine8, 10 )
    vOffset4 = ComputeVectorBetweenBones( boneSpine12, boneSpine11, 10 )
    vOffset5 = ComputeVectorBetweenBones( boneSpine15, boneSpine14, 10 )	
	
    rigJoint1   = sfmUtils.CreateOffsetHandle( "rig_joint1",  boneSpine2, vOffset1,  bCreateControls=False )   
    rigJoint2   = sfmUtils.CreateOffsetHandle( "rig_joint2",  boneSpine5, vOffset2,  bCreateControls=False )
    rigJoint3   = sfmUtils.CreateOffsetHandle( "rig_joint3",  boneSpine8, vOffset3,  bCreateControls=False )   
    rigJoint4   = sfmUtils.CreateOffsetHandle( "rig_joint4",  boneSpine11, vOffset4,  bCreateControls=False )
    rigJoint5   = sfmUtils.CreateOffsetHandle( "rig_joint5",  boneSpine14, vOffset5,  bCreateControls=False )  
	
    # Create a helper handle which will remain constrained to the each foot position that can be used for parenting.
    rigFootHelper1 = sfmUtils.CreateConstrainedHandle( "rig_footHelper_1", boneSpine3, bCreateControls=False )
    rigFootHelper2 = sfmUtils.CreateConstrainedHandle( "rig_footHelper_2", boneSpine6, bCreateControls=False )
    rigFootHelper3 = sfmUtils.CreateConstrainedHandle( "rig_footHelper_3", boneSpine9, bCreateControls=False )
    rigFootHelper4 = sfmUtils.CreateConstrainedHandle( "rig_footHelper_4", boneSpine12, bCreateControls=False )
    rigFootHelper5 = sfmUtils.CreateConstrainedHandle( "rig_footHelper_5", boneSpine15, bCreateControls=False )	
	
    # Create a list of all of the rig dags
    allRigHandles = [ rigRoot, rigPelvis,
    rigJoint1, rigSpine3, rigJoint2, rigSpine6, rigJoint3, rigSpine9, rigJoint4, rigSpine12, rigJoint5, rigSpine15 ];
    
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
   
    sfmUtils.ParentMaintainWorld( rigFootHelperFR,   rigRoot )
    sfmUtils.ParentMaintainWorld( rigFootHelperFL,   rigRoot )
	
    sfmUtils.ParentMaintainWorld( rigHead,         rigRoot )
    sfmUtils.ParentMaintainWorld( rigSpine3,         rigPelvis )
    sfmUtils.ParentMaintainWorld( rigUjoint,         rigHead )
    sfmUtils.ParentMaintainWorld( rigLjoint,         rigSpine3 )
    
    # Create the hips control, this allows a pelvis rotation that does not effect the spine,
    # it is only used for rotation so a position control is not created. Additionally add the
    # new control to the selection so the that set default call operates on it too.
    rigHips = sfmUtils.CreateHandleAt( "rig_axel", rigPelvis, False, True )
    sfmUtils.Parent( rigHips, rigPelvis, vs.REPARENT_LOGS_OVERWRITE )
    sfm.SelectDag( rigHips )

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
    
	
    footIKTargetFR = rigHead
    footIkTargetFL = rigSpine3
    
    if ( gameModel != None ) :
        footRollIkTargetFR = CreateReverseFoot( "rig_footRoll", "FR", gameModel, animSet, shot, rigHelpersGroup, rigLegsGroup )
        footRollIkTargetFL = CreateReverseFoot( "rig_footRoll", "FL", gameModel, animSet, shot, rigHelpersGroup, rigLegsGroup )
        if ( footRollIkTargetFR != None ) :
            footIKTargetFR = footRollIkTargetFR
        if ( footRollIkTargetFL != None ) :
            footIkTargetFL = footRollIkTargetFL
    
    
    #==============================================================================================
    # Create constraints to drive the bone transforms using the rig handles
    #==============================================================================================
    
    # The following bones are simply constrained directly to a rig handle
    sfmUtils.CreatePointOrientConstraint( rigRoot,      boneRoot        )
    sfmUtils.CreatePointOrientConstraint( rigHips,      bonePelvis      )
    
    # Create ik constraints for the arms and legs that will control the rotation of the hip / knee and 
    # upper arm / elbow joints based on the position of the foot and hand respectively.
    sfmUtils.BuildArmLeg( rigUjoint,  footIKTargetFR, boneSpine4,  boneHead, True )
    sfmUtils.BuildArmLeg( rigLjoint,  footIkTargetFL, boneSpine1,  boneSpine3, True )
    
    
    #==============================================================================================
    # Create handles for the important attachment points 
    #==============================================================================================    
    attachmentGroup = rootGroup.CreateControlGroup( "Attachments" )  
    attachmentGroup.SetVisible( False )
    
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_heel_BR",       attachmentGroup )
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_toe_BR",        attachmentGroup )
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_outerFoot_BR",  attachmentGroup )
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_innerFoot_BR",  attachmentGroup )
    
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_heel_BL",       attachmentGroup )
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_toe_BL",        attachmentGroup )
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_outerFoot_BL",  attachmentGroup )
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_innerFoot_BL",  attachmentGroup )
    
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_heel_FR",       attachmentGroup )
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_toe_FR",        attachmentGroup )
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_outerFoot_FR",  attachmentGroup )
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_innerFoot_FR",  attachmentGroup )
    
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_heel_FL",       attachmentGroup )
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_toe_FL",        attachmentGroup )
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_outerFoot_FL",  attachmentGroup )
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_innerFoot_FL",  attachmentGroup )
    
    #==============================================================================================
    # Re-organize the selection groups
    #==============================================================================================  
    rigBodyGroup = rootGroup.CreateControlGroup( "RigBody" )
    
    BackRightLegGroup = rootGroup.CreateControlGroup( "BackRightLeg" )
    BackLeftLegGroup = rootGroup.CreateControlGroup( "BackLeftLeg" ) 
    FrontRightLegGroup = rootGroup.CreateControlGroup( "FrontRightLeg" )
    FrontLeftLegGroup = rootGroup.CreateControlGroup( "FrontLeftLeg" )   	
    
    sfmUtils.AddDagControlsToGroup( rigBodyGroup, rigRoot, rigPelvis, rigHips )  
    
    rigLegsGroup.AddChild( FrontRightLegGroup )
    rigLegsGroup.AddChild( FrontLeftLegGroup )
    rigLegsGroup.AddChild( BackRightLegGroup )
    rigLegsGroup.AddChild( BackLeftLegGroup )
    sfmUtils.AddDagControlsToGroup( FrontRightLegGroup, rigUjoint, rigHead )
    sfmUtils.AddDagControlsToGroup( FrontLeftLegGroup, rigLjoint, rigSpine3 )

	
    sfmUtils.MoveControlGroup( "rig_footRoll_FL", rigLegsGroup, FrontLeftLegGroup )
    sfmUtils.MoveControlGroup( "rig_footRoll_FR", rigLegsGroup, FrontRightLegGroup )
    

 
    sfmUtils.AddDagControlsToGroup( rigHelpersGroup, rigFootHelperFR,  rigFootHelperFL)

    # Set the control group visiblity, this is done through the rig so it can track which
    # groups it hid, so they can be set back to being visible when the rig is detached.
    HideControlGroups( rig, rootGroup, "Body", "Arms", "Legs", "Unknown", "Other", "Root" )      
        
    #Re-order the groups
    fingersGroup = rootGroup.FindChildByName( "Fingers", False ) 
    rootGroup.MoveChildToBottom( rigBodyGroup )
    rootGroup.MoveChildToBottom( rigLegsGroup )    
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
	
    rigBodyGroup.SetGroupColor( topLevelColor, False )
    rigLegsGroup.SetGroupColor( topLevelColor, False )
    attachmentGroup.SetGroupColor( topLevelColor, False )
    rigHelpersGroup.SetGroupColor( topLevelColor, False )
    
    FrontRightLegGroup.SetGroupColor( RightColor, False )
    FrontLeftLegGroup.SetGroupColor( LeftColor, False )
    BackRightLegGroup.SetGroupColor( RightColor, False )
    BackLeftLegGroup.SetGroupColor( LeftColor, False )
    
    # End the rig definition
    sfm.EndRig()
    return
    
#==================================================================================================
# Script entry
#==================================================================================================

# Construct the rig for the selected animation set
BuildRig();


    
    




