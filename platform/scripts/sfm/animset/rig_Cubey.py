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
# The piston aiming method
#==================================================================================================
def CreateAimConstraint( target, slave, bCreateControls=True, group=None ) :
    ''' Method for creating a single target orient constraint '''
    
    if ( target == None ):
        return

    targetDag = sfmUtils.GetDagFromNameOrObject( target )
    slaveDag = sfmUtils.GetDagFromNameOrObject( slave )
    
    sfm.PushSelection()
    sfmUtils.SelectDagList( [ targetDag, slaveDag ] )
    
    orientConstraintTarget = sfm.AimConstraint( controls=bCreateControls, mo=True )
    
    if ( group != None ):

        if ( orientConstraintTarget != None ):
            orientWeightControl = orientConstraintTarget.FindWeightControl()
            if ( orientWeightControl != None ):
                group.AddControl( orientWeightControl )
            
    sfm.PopSelection()
    return
	
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
    boneRoot      = sfmUtils.FindFirstDag( [ "Body" ], True )
    bonePelvis    = sfmUtils.FindFirstDag( [ "legbase_bone" ], True )
    boneSpine0    = sfmUtils.FindFirstDag( [ "Box_Rotator" ], True )
    
    boneUpperLegFR = sfmUtils.FindFirstDag( [ "FR_Thigh" ], True )
    boneLowerLegFR = sfmUtils.FindFirstDag( [ "FR_LowerLeg" ], True )
    boneFootFR     = sfmUtils.FindFirstDag( [ "FR_Foot" ], True )
    boneUpperLegBR = sfmUtils.FindFirstDag( [ "BR_Thigh" ], True )
    boneLowerLegBR = sfmUtils.FindFirstDag( [ "BR_LowerLeg" ], True )
    boneFootBR     = sfmUtils.FindFirstDag( [ "BR_Foot" ], True )
   
    boneUpperLegFL = sfmUtils.FindFirstDag( [ "FL_Thigh" ], True )
    boneLowerLegFL = sfmUtils.FindFirstDag( [ "FL_LowerLeg" ], True )
    boneFootFL     = sfmUtils.FindFirstDag( [ "FL_Foot" ], True )
    boneUpperLegBL = sfmUtils.FindFirstDag( [ "BL_Thigh" ], True )
    boneLowerLegBL = sfmUtils.FindFirstDag( [ "BL_LowerLeg" ], True )
    boneFootBL     = sfmUtils.FindFirstDag( [ "BL_Foot" ], True )
    
    boneFRPistonEnd = sfmUtils.FindFirstDag( [ "FR_PistonEnd" ], True )   
    boneFRPistonTop = sfmUtils.FindFirstDag( [ "FR_PistonTop" ], True )	
    boneFLPistonEnd = sfmUtils.FindFirstDag( [ "FL_PistonEnd" ], True )
    boneFLPistonTop = sfmUtils.FindFirstDag( [ "FL_PistonTop" ], True )	
    boneBRPistonEnd = sfmUtils.FindFirstDag( [ "BR_PistonEnd" ], True ) 
    boneBRPistonTop = sfmUtils.FindFirstDag( [ "BR_PistonTop" ], True ) 	
    boneBLPistonEnd = sfmUtils.FindFirstDag( [ "BL_PistonEnd" ], True ) 
    boneBLPistonTop = sfmUtils.FindFirstDag( [ "BL_PistonTop" ], True )
    

    #==============================================================================================
    # Create the rig handles and constrain them to existing bones
    #==============================================================================================
    rigRoot    = sfmUtils.CreateConstrainedHandle( "rig_root",     boneRoot,    bCreateControls=False )
    rigPelvis  = sfmUtils.CreateConstrainedHandle( "rig_rotator",   bonePelvis,  bCreateControls=False )
    rigSpine0  = sfmUtils.CreateConstrainedHandle( "rig_box_rotator",  boneSpine0,  bCreateControls=False )
    
    rigFootBR   = sfmUtils.CreateConstrainedHandle( "rig_foot_BR",   boneFootBR,   bCreateControls=False )
    rigFootFR   = sfmUtils.CreateConstrainedHandle( "rig_foot_FR",   boneFootFR,   bCreateControls=False )

    rigFootBL   = sfmUtils.CreateConstrainedHandle( "rig_foot_BL",   boneFootBL,   bCreateControls=False )	
    rigFootFL   = sfmUtils.CreateConstrainedHandle( "rig_foot_FL",   boneFootFL,   bCreateControls=False )
        
    
    # Use the direction from the heel to the toe to compute the knee offsets, 
    # this makes the knee offset indpendent of the inital orientation of the model.
    vKneeOffsetBR = ComputeVectorBetweenBones( boneFootBR, boneLowerLegBR, 10 )
    vKneeOffsetBL = ComputeVectorBetweenBones( boneFootBL, boneLowerLegBL, 10 )
    vKneeOffsetFR = ComputeVectorBetweenBones( boneFootFR, boneLowerLegFR, 10 )
    vKneeOffsetFL = ComputeVectorBetweenBones( boneFootFL, boneLowerLegFL, 10 )
	
    rigPistonTFR = CreateAimConstraint( boneFRPistonEnd, boneFRPistonTop, bCreateControls=True )
    rigPistonEFR = CreateAimConstraint( boneFRPistonTop, boneFRPistonEnd, bCreateControls=True )	
    rigPistonTFL = CreateAimConstraint( boneFLPistonEnd, boneFLPistonTop, bCreateControls=True )
    rigPistonEFL = CreateAimConstraint( boneFLPistonTop, boneFLPistonEnd, bCreateControls=True )	
    rigPistonTBR = CreateAimConstraint( boneBRPistonEnd, boneBRPistonTop, bCreateControls=True )
    rigPistonEBR = CreateAimConstraint( boneBRPistonTop, boneBRPistonEnd, bCreateControls=True )	
    rigPistonTBL = CreateAimConstraint( boneBLPistonEnd, boneBLPistonTop, bCreateControls=True )
    rigPistonEBL = CreateAimConstraint( boneBLPistonTop, boneBLPistonEnd, bCreateControls=True )
    
    rigKneeFR   = sfmUtils.CreateOffsetHandle( "rig_knee_FR",  boneLowerLegFR, vKneeOffsetFR,  bCreateControls=False )   
    rigKneeFL   = sfmUtils.CreateOffsetHandle( "rig_knee_FL",  boneLowerLegFL, vKneeOffsetFL,  bCreateControls=False )
    rigKneeBR   = sfmUtils.CreateOffsetHandle( "rig_knee_BR",  boneLowerLegBR, vKneeOffsetBR,  bCreateControls=False )   
    rigKneeBL   = sfmUtils.CreateOffsetHandle( "rig_knee_BL",  boneLowerLegBL, vKneeOffsetBL,  bCreateControls=False )
   
    # Create a helper handle which will remain constrained to the each foot position that can be used for parenting.
    rigFootHelperBR = sfmUtils.CreateConstrainedHandle( "rig_footHelper_BR", boneFootBR, bCreateControls=False )
    rigFootHelperBL = sfmUtils.CreateConstrainedHandle( "rig_footHelper_BL", boneFootBL, bCreateControls=False )
    rigFootHelperFR = sfmUtils.CreateConstrainedHandle( "rig_footHelper_FR", boneFootFR, bCreateControls=False )
    rigFootHelperFL = sfmUtils.CreateConstrainedHandle( "rig_footHelper_FL", boneFootFL, bCreateControls=False )
    
    # Create a list of all of the rig dags
    allRigHandles = [ rigRoot, rigPelvis, rigSpine0,
                      rigKneeBR, rigFootBR, rigKneeFR, rigFootFR,
                      rigKneeBL, rigFootBL, rigKneeFL, rigFootFL ];
    
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
    
    sfmUtils.ParentMaintainWorld( rigFootHelperBR,   rigRoot )
    sfmUtils.ParentMaintainWorld( rigFootHelperBL,   rigRoot )
    sfmUtils.ParentMaintainWorld( rigFootHelperFR,   rigRoot )
    sfmUtils.ParentMaintainWorld( rigFootHelperFL,   rigRoot )
    sfmUtils.ParentMaintainWorld( rigFootBR,         rigRoot )
    sfmUtils.ParentMaintainWorld( rigFootBL,         rigRoot )
    sfmUtils.ParentMaintainWorld( rigFootFR,         rigRoot )
    sfmUtils.ParentMaintainWorld( rigFootFL,         rigRoot )
    sfmUtils.ParentMaintainWorld( rigKneeBR,         rigFootBR )
    sfmUtils.ParentMaintainWorld( rigKneeBL,         rigFootBL )
    sfmUtils.ParentMaintainWorld( rigKneeFR,         rigFootFR )
    sfmUtils.ParentMaintainWorld( rigKneeFL,         rigFootFL )
    
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
    
    footIKTargetBR = rigFootBR
    footIkTargetBL = rigFootBL
    footIKTargetFR = rigFootFR
    footIkTargetFL = rigFootFL
    
    if ( gameModel != None ) :
        footRollIkTargetBR = CreateReverseFoot( "rig_footRoll", "BR", gameModel, animSet, shot, rigHelpersGroup, rigLegsGroup )
        footRollIkTargetBL = CreateReverseFoot( "rig_footRoll", "BL", gameModel, animSet, shot, rigHelpersGroup, rigLegsGroup )
        footRollIkTargetFR = CreateReverseFoot( "rig_footRoll", "FR", gameModel, animSet, shot, rigHelpersGroup, rigLegsGroup )
        footRollIkTargetFL = CreateReverseFoot( "rig_footRoll", "FL", gameModel, animSet, shot, rigHelpersGroup, rigLegsGroup )
        if ( footRollIkTargetBR != None ) :
            footIKTargetBR = footRollIkTargetBR
        if ( footRollIkTargetBL != None ) :
            footIkTargetBL = footRollIkTargetBL
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
    sfmUtils.CreatePointOrientConstraint( rigSpine0,    boneSpine0      )
    
    # Create ik constraints for the arms and legs that will control the rotation of the hip / knee and 
    # upper arm / elbow joints based on the position of the foot and hand respectively.
    sfmUtils.BuildArmLeg( rigKneeBR,  footIKTargetBR, boneUpperLegBR,  boneFootBR, True )
    sfmUtils.BuildArmLeg( rigKneeBL,  footIkTargetBL, boneUpperLegBL,  boneFootBL, True )
    sfmUtils.BuildArmLeg( rigKneeFR,  footIKTargetFR, boneUpperLegFR,  boneFootFR, True )
    sfmUtils.BuildArmLeg( rigKneeFL,  footIkTargetFL, boneUpperLegFL,  boneFootFL, True )   
    
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
    
    sfmUtils.AddDagControlsToGroup( rigBodyGroup, rigRoot, rigPelvis, rigHips, rigSpine0 )  
    
    rigLegsGroup.AddChild( FrontRightLegGroup )
    rigLegsGroup.AddChild( FrontLeftLegGroup )
    rigLegsGroup.AddChild( BackRightLegGroup )
    rigLegsGroup.AddChild( BackLeftLegGroup )
    sfmUtils.AddDagControlsToGroup( FrontRightLegGroup, rigKneeFR, rigFootFR )
    sfmUtils.AddDagControlsToGroup( FrontLeftLegGroup, rigKneeFL, rigFootFL )
    sfmUtils.AddDagControlsToGroup( BackRightLegGroup, rigKneeBR, rigFootBR )
    sfmUtils.AddDagControlsToGroup( BackLeftLegGroup, rigKneeBL, rigFootBL )
    
    sfmUtils.MoveControlGroup( "rig_footRoll_BL", rigLegsGroup, BackLeftLegGroup )
    sfmUtils.MoveControlGroup( "rig_footRoll_BR", rigLegsGroup, BackRightLegGroup )
	
    sfmUtils.MoveControlGroup( "rig_footRoll_FL", rigLegsGroup, FrontLeftLegGroup )
    sfmUtils.MoveControlGroup( "rig_footRoll_FR", rigLegsGroup, FrontRightLegGroup )
    

 
    sfmUtils.AddDagControlsToGroup( rigHelpersGroup, rigFootHelperBR, rigFootHelperBL, rigFootHelperFR, rigFootHelperFL )

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


    
    




