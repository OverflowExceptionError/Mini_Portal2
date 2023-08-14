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
    #boneSpine0    = sfmUtils.FindFirstDag( [ "Aim_LR" ], True )
    #boneSpine1    = sfmUtils.FindFirstDag( [ "ValveBiped.Bip01_Spine1",		"Bip01_Spine1",		"bip_spine_1" ], True )
    #boneSpine2    = sfmUtils.FindFirstDag( [ "ValveBiped.Bip01_Spine2",		"Bip01_Spine2",		"bip_spine_2" ], True ) 
    #boneSpine3    = sfmUtils.FindFirstDag( [ "ValveBiped.Bip01_Spine3",		"Bip01_Spine3",		"bip_spine_3",	"ValveBiped.Bip01_Spine4" ], True )
    #boneNeck      = sfmUtils.FindFirstDag( [ "ValveBiped.Bip01_Neck",		"Bip01_Neck",		"bip_neck_0",	"bip_neck", "ValveBiped.Bip01_Neck1" ], True )
    #boneHead      = sfmUtils.FindFirstDag( [ "Body_ball" ], True )
    #boneHeadYZ    = sfmUtils.FindFirstDag( [ "body_yz" ], True )
    #boneHeadZ    = sfmUtils.FindFirstDag( [ "body_z" ], True )
	
    boneUpperLegR = sfmUtils.FindFirstDag( [ "r_thigh" ], True )
    boneLowerLegR = sfmUtils.FindFirstDag( [ "r_knee" ], True )
    boneFootR     = sfmUtils.FindFirstDag( [ "r_ankle" ], True )
    #boneToeR      = sfmUtils.FindFirstDag( [ "R_toe" ], True ) 
    #boneCollarR   = sfmUtils.FindFirstDag( [ "RT_Wing_Rotator" ], True )   
    #boneUpperArmR = sfmUtils.FindFirstDag( [ "bicep_R" ], True ) 
    #boneLowerArmR = sfmUtils.FindFirstDag( [ "elbow_R" ], True )
    #boneHandR     = sfmUtils.FindFirstDag( [ "RT_Wing" ], True )
   
    boneUpperLegL = sfmUtils.FindFirstDag( [ "l_thigh" ], True )
    boneLowerLegL = sfmUtils.FindFirstDag( [ "l_knee" ], True )
    boneFootL     = sfmUtils.FindFirstDag( [ "l_ankle" ], True )
    #boneToeL      = sfmUtils.FindFirstDag( [ "L_toe" ], True ) 
    #boneCollarL   = sfmUtils.FindFirstDag( [ "LFT_Wing_Rotator" ], True )   
    #boneUpperArmL = sfmUtils.FindFirstDag( [ "bicep_L" ], True ) 
    #boneLowerArmL = sfmUtils.FindFirstDag( [ "elbow_L" ], True )
    #boneHandL     = sfmUtils.FindFirstDag( [ "LFT_Wing" ], True )
    
    boneUpperLegM = sfmUtils.FindFirstDag( [ "b_thigh" ], True )
    boneLowerLegM = sfmUtils.FindFirstDag( [ "b_knee" ], True )
    boneFootM     = sfmUtils.FindFirstDag( [ "b_ankle" ], True )
    #boneToeM      = sfmUtils.FindFirstDag( [ "R_toe" ], True ) 
	
    boneArm1R = sfmUtils.FindFirstDag( [ "r_arm1" ], True )
    boneArm2R = sfmUtils.FindFirstDag( [ "r_arm2" ], True )
    boneArm3R = sfmUtils.FindFirstDag( [ "r_arm3" ], True )
	
    boneArm1L = sfmUtils.FindFirstDag( [ "l_arm1" ], True )
    boneArm2L = sfmUtils.FindFirstDag( [ "l_arm3" ], True )
	
    boneArm1B = sfmUtils.FindFirstDag( [ "b_arm1" ], True )
    boneArm2B = sfmUtils.FindFirstDag( [ "b_arm2" ], True )
    boneArm3B = sfmUtils.FindFirstDag( [ "b_arm3" ], True )
	
    boneHeatRay = sfmUtils.FindFirstDag( [ "heatray" ], True )   
    #==============================================================================================
    # Create the rig handles and constrain them to existing bones
    #==============================================================================================
    rigRoot    = sfmUtils.CreateConstrainedHandle( "rig_root",     boneRoot,    bCreateControls=False )
    rigPelvis  = sfmUtils.CreateConstrainedHandle( "rig_pelvis",   bonePelvis,  bCreateControls=False )
    #rigSpine0  = sfmUtils.CreateConstrainedHandle( "rig_spine_0",  boneSpine0,  bCreateControls=False )
    #rigSpine1  = sfmUtils.CreateConstrainedHandle( "rig_spine_1",  boneSpine1,  bCreateControls=False )
    #rigSpine2  = sfmUtils.CreateConstrainedHandle( "rig_spine_2",  boneSpine2,  bCreateControls=False )
    #rigChest   = sfmUtils.CreateConstrainedHandle( "rig_chest",    boneSpine3,  bCreateControls=False )
    #rigNeck    = sfmUtils.CreateConstrainedHandle( "rig_neck",     boneNeck,    bCreateControls=False )
    #rigHead    = sfmUtils.CreateConstrainedHandle( "rig_head",     boneHead,    bCreateControls=False )
    
    rigHipR   = sfmUtils.CreateConstrainedHandle( "rig_hip_R",   boneUpperLegR,   bCreateControls=False )
    rigFootR   = sfmUtils.CreateConstrainedHandle( "rig_foot_R",   boneFootR, bCreateControls=False )
    #rigToeR    = sfmUtils.CreateConstrainedHandle( "rig_toe_R",    boneToeR,    bCreateControls=False )
    #rigCollarR = sfmUtils.CreateConstrainedHandle( "rig_collar_R", boneCollarR, bCreateControls=False )
    #rigHandR   = sfmUtils.CreateConstrainedHandle( "rig_hand_R",   boneHandR,   bCreateControls=False )
	
    rigHipL   = sfmUtils.CreateConstrainedHandle( "rig_hip_L",   boneUpperLegL,   bCreateControls=False )
    rigFootL   = sfmUtils.CreateConstrainedHandle( "rig_foot_L",   boneFootL, bCreateControls=False )
    #rigToeL    = sfmUtils.CreateConstrainedHandle( "rig_toe_L",    boneToeL,    bCreateControls=False )
    #rigCollarL = sfmUtils.CreateConstrainedHandle( "rig_collar_L", boneCollarL, bCreateControls=False )
    #rigHandL   = sfmUtils.CreateConstrainedHandle( "rig_hand_L",   boneHandL,   bCreateControls=False )
        
    rigHipM   = sfmUtils.CreateConstrainedHandle( "rig_hip_M",   boneUpperLegM,   bCreateControls=False )
    rigFootM   = sfmUtils.CreateConstrainedHandle( "rig_foot_M",   boneFootM, bCreateControls=False )
    #rigToeM    = sfmUtils.CreateConstrainedHandle( "rig_toe_M",    boneToeM,    bCreateControls=False )
		
    rigKneeR   = sfmUtils.CreateOffsetHandle( "rig_knee_R",  boneLowerLegR, vs.Vector( 0, 0,  10 ),  bCreateControls=False )   
    rigKneeL   = sfmUtils.CreateOffsetHandle( "rig_knee_L",  boneLowerLegL, vs.Vector( 0, 0,  10 ),  bCreateControls=False )
    rigKneeM   = sfmUtils.CreateOffsetHandle( "rig_knee_M",  boneLowerLegM, vs.Vector( 0, 0,  10 ),  bCreateControls=False ) 
  	
    rigArm1R  = sfmUtils.CreateConstrainedHandle( "rig_R_Arm1",   boneArm1R,  bCreateControls=False )
    rigArm2R  = sfmUtils.CreateConstrainedHandle( "rig_R_Arm2",   boneArm2R,  bCreateControls=False )
    rigArm3R  = sfmUtils.CreateConstrainedHandle( "rig_R_Arm3",   boneArm3R,  bCreateControls=False )
	
    rigArm1L  = sfmUtils.CreateConstrainedHandle( "rig_L_Arm1",   boneArm1L,  bCreateControls=False )
    rigArm2L  = sfmUtils.CreateConstrainedHandle( "rig_L_Arm2",   boneArm2L,  bCreateControls=False )
	
    rigArm1B  = sfmUtils.CreateConstrainedHandle( "rig_B_Arm1",   boneArm1B,  bCreateControls=False )
    rigArm2B  = sfmUtils.CreateConstrainedHandle( "rig_B_Arm2",   boneArm2B,  bCreateControls=False )
    rigArm3B  = sfmUtils.CreateConstrainedHandle( "rig_B_Arm3",   boneArm3B,  bCreateControls=False )
	
    rigHeatRay  = sfmUtils.CreateConstrainedHandle( "rig_HeatRay",   boneHeatRay,  bCreateControls=False )	
    #rigElbowR  = sfmUtils.CreateOffsetHandle( "rig_elbow_R", boneLowerArmR, vs.Vector( 0, 0, -10 ),  bCreateControls=False )
    #rigElbowL  = sfmUtils.CreateOffsetHandle( "rig_elbow_L", boneLowerArmL, vs.Vector( 0, 0, -10 ),  bCreateControls=False )
    
    # Create a helper handle which will remain constrained to the each foot position that can be used for parenting.
    rigFootHelperR = sfmUtils.CreateConstrainedHandle( "rig_footHelper_R", boneFootR, bCreateControls=False )
    rigFootHelperL = sfmUtils.CreateConstrainedHandle( "rig_footHelper_L", boneFootL, bCreateControls=False )
    rigFootHelperM = sfmUtils.CreateConstrainedHandle( "rig_footHelper_M", boneFootM, bCreateControls=False )
    # Create a list of all of the rig dags
    # allRigHandles = [ rigRoot, rigPelvis, rigSpine0, rigSpine1, rigSpine2, rigChest, rigNeck, rigHead,
    #                   rigCollarR, rigElbowR, rigHandR, rigKneeR, rigFootR, rigToeR,
    #                   rigCollarL, rigElbowL, rigHandL, rigKneeL, rigFootL, rigToeL ];
    allRigHandles = [ rigRoot, rigPelvis,
                       rigHipR, rigKneeR, rigFootR, rigArm1R, rigArm2R, rigArm3R,
                       rigHipL, rigKneeL, rigFootL, rigArm1L, rigArm2L,
                       rigHipM, rigKneeM, rigFootM, rigArm1B, rigArm2B, rigArm3B, rigHeatRay ];
    
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
    #sfmUtils.ParentMaintainWorld( rigSpine0,        rigPelvis )
    #sfmUtils.ParentMaintainWorld( rigSpine1,        rigSpine0 )
    #sfmUtils.ParentMaintainWorld( rigSpine2,        rigSpine1 )
    #sfmUtils.ParentMaintainWorld( rigChest,         rigSpine2 )
    #sfmUtils.ParentMaintainWorld( rigNeck,          rigChest )
    #sfmUtils.ParentMaintainWorld( rigHead,          rigPelvis )
    
    sfmUtils.ParentMaintainWorld( rigFootHelperR,   rigRoot )
    sfmUtils.ParentMaintainWorld( rigFootHelperL,   rigRoot )
    sfmUtils.ParentMaintainWorld( rigFootHelperM,   rigRoot )
    sfmUtils.ParentMaintainWorld( rigHipR,          rigPelvis )
    sfmUtils.ParentMaintainWorld( rigHipL,          rigPelvis )	
    sfmUtils.ParentMaintainWorld( rigHipM,          rigPelvis )
    sfmUtils.ParentMaintainWorld( rigFootR,         rigRoot )
    sfmUtils.ParentMaintainWorld( rigFootL,         rigRoot )	
    sfmUtils.ParentMaintainWorld( rigFootM,         rigRoot )
    sfmUtils.ParentMaintainWorld( rigKneeR,         rigFootR )
    sfmUtils.ParentMaintainWorld( rigKneeL,         rigFootL )	
    sfmUtils.ParentMaintainWorld( rigKneeM,         rigFootM )
    #sfmUtils.ParentMaintainWorld( rigToeR,          rigFootHelperR )
    #sfmUtils.ParentMaintainWorld( rigToeL,          rigFootHelperL )
    sfmUtils.ParentMaintainWorld( rigArm1R,         rigPelvis )	
    sfmUtils.ParentMaintainWorld( rigArm2R,         rigArm1R )	
    sfmUtils.ParentMaintainWorld( rigArm3R,         rigArm2R )	

    sfmUtils.ParentMaintainWorld( rigArm1L,         rigPelvis )	
    sfmUtils.ParentMaintainWorld( rigArm2L,         rigArm1L )	
	
    sfmUtils.ParentMaintainWorld( rigArm1B,         rigPelvis )	
    sfmUtils.ParentMaintainWorld( rigArm2B,         rigArm1B )	
    sfmUtils.ParentMaintainWorld( rigArm3B,         rigArm2B )
	
    sfmUtils.ParentMaintainWorld( rigHeatRay,         rigPelvis )   
    #sfmUtils.ParentMaintainWorld( rigCollarR,       rigPelvis )
    #sfmUtils.ParentMaintainWorld( rigElbowR,        rigCollarR )
    #sfmUtils.ParentMaintainWorld( rigHandR,	        rigRoot )
    #sfmUtils.ParentMaintainWorld( rigCollarL,       rigPelvis )
    #sfmUtils.ParentMaintainWorld( rigElbowL,        rigCollarL )
    #sfmUtils.ParentMaintainWorld( rigHandL,	        rigRoot )
    
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
    footIkTargetM = rigFootM
    
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
    #sfmUtils.CreatePointOrientConstraint( rigSpine0,    boneSpine0      )
    #sfmUtils.CreatePointOrientConstraint( rigSpine1,    boneSpine1     )
    #sfmUtils.CreatePointOrientConstraint( rigSpine2,    boneSpine2     )
    #sfmUtils.CreatePointOrientConstraint( rigChest,     boneSpine3     )
    #sfmUtils.CreatePointOrientConstraint( rigNeck,      boneNeck       )
    #sfmUtils.CreatePointOrientConstraint( rigHead,      boneHead        )
    #sfmUtils.CreatePointOrientConstraint( boneHead,      boneHeadYZ     )
    #sfmUtils.CreatePointOrientConstraint( boneHead,      boneHeadZ      )
    sfmUtils.CreatePointOrientConstraint( rigHipR,      boneUpperLegR   )
    sfmUtils.CreatePointOrientConstraint( rigHipL,      boneUpperLegL   )
    sfmUtils.CreatePointOrientConstraint( rigHipM,      boneUpperLegM   )
    #sfmUtils.CreatePointOrientConstraint( rigCollarR,   boneCollarR     )
    #sfmUtils.CreatePointOrientConstraint( rigCollarL,   boneCollarL     )
    #sfmUtils.CreatePointOrientConstraint( rigToeR,      boneToeR        )
    #sfmUtils.CreatePointOrientConstraint( rigToeL,      boneToeL        )
 
    sfmUtils.CreatePointOrientConstraint( rigArm1R,      boneArm1R   )
    sfmUtils.CreatePointOrientConstraint( rigArm2R,      boneArm2R   )
    sfmUtils.CreatePointOrientConstraint( rigArm3R,      boneArm3R   )
    sfmUtils.CreatePointOrientConstraint( rigArm1L,      boneArm1L   )
    sfmUtils.CreatePointOrientConstraint( rigArm2L,      boneArm2L   )
    sfmUtils.CreatePointOrientConstraint( rigArm1B,      boneArm1B   )
    sfmUtils.CreatePointOrientConstraint( rigArm2B,      boneArm2B   )
    sfmUtils.CreatePointOrientConstraint( rigArm3B,      boneArm3B   )
    sfmUtils.CreatePointOrientConstraint( rigHeatRay,    boneHeatRay   )	
    # Create ik constraints for the arms and legs that will control the rotation of the hip / knee and 
    # upper arm / elbow joints based on the position of the foot and hand respectively.
    sfmUtils.BuildArmLeg( rigKneeR,  footIKTargetR, boneUpperLegR,  boneFootR, True )
    sfmUtils.BuildArmLeg( rigKneeL,  footIkTargetL, boneUpperLegL,  boneFootL, True )
    sfmUtils.BuildArmLeg( rigKneeM,  footIkTargetM, boneUpperLegM,  boneFootM, True )
    #sfmUtils.BuildArmLeg( rigHandR,  boneHandR, True )
    #sfmUtils.BuildArmLeg( rigHandL,  boneHandL, True )
    
    
    #==============================================================================================
    # Create handles for the important attachment points 
    #==============================================================================================    
    attachmentGroup = rootGroup.CreateControlGroup( "Attachments" )  
    attachmentGroup.SetVisible( False )
    
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_heel_R",       attachmentGroup )
    #sfmUtils.CreateAttachmentHandleInGroup( "pvt_toe_R",        attachmentGroup )
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_outerFoot_R",  attachmentGroup )
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_innerFoot_R",  attachmentGroup )
    
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_heel_L",       attachmentGroup )
    #sfmUtils.CreateAttachmentHandleInGroup( "pvt_toe_L",        attachmentGroup )
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_outerFoot_L",  attachmentGroup )
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_innerFoot_L",  attachmentGroup )
     
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_heel_M",       attachmentGroup )
    #sfmUtils.CreateAttachmentHandleInGroup( "pvt_toe_M",        attachmentGroup )
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_outerFoot_M",  attachmentGroup )
    sfmUtils.CreateAttachmentHandleInGroup( "pvt_innerFoot_M",  attachmentGroup )
    
    
    
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
    MidLegGroup = rootGroup.CreateControlGroup( "MidLeg" )   
    #sfmUtils.AddDagControlsToGroup( rigBodyGroup, rigRoot, rigPelvis, rigHips, rigSpine0, rigSpine1, rigSpine2, rigChest, rigNeck, rigHead )  
    sfmUtils.AddDagControlsToGroup( rigBodyGroup, rigRoot, rigPelvis )  
  
    rigArmsGroup.AddChild( RightArmGroup )
    rigArmsGroup.AddChild( LeftArmGroup )
    rigArmsGroup.AddChild( BackArmGroup )
    sfmUtils.AddDagControlsToGroup( RightArmGroup,  rigArm1R, rigArm2R, rigArm3R )
    sfmUtils.AddDagControlsToGroup( LeftArmGroup, rigArm1L, rigArm2L )
    sfmUtils.AddDagControlsToGroup( BackArmGroup,  rigArm1B, rigArm2B, rigArm3B, rigHeatRay )  
	
    rigLegsGroup.AddChild( RightLegGroup )
    rigLegsGroup.AddChild( LeftLegGroup )
    rigLegsGroup.AddChild( MidLegGroup )
    sfmUtils.AddDagControlsToGroup( RightLegGroup, rigHipR, rigKneeR, rigFootR )
    sfmUtils.AddDagControlsToGroup( LeftLegGroup, rigHipL, rigKneeL, rigFootL )
    sfmUtils.AddDagControlsToGroup( MidLegGroup, rigHipM, rigKneeM, rigFootM )
	
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
    RightColor = vs.Color( 255, 0, 0, 255 )
    LeftColor = vs.Color( 0, 255, 0, 255 )
    MidColor = vs.Color( 0, 0, 255, 255 )
	
    rigBodyGroup.SetGroupColor( topLevelColor, False )
    rigArmsGroup.SetGroupColor( topLevelColor, False )
    rigLegsGroup.SetGroupColor( topLevelColor, False )
    attachmentGroup.SetGroupColor( topLevelColor, False )
    rigHelpersGroup.SetGroupColor( topLevelColor, False )
    
    RightArmGroup.SetGroupColor( RightColor, False )
    LeftArmGroup.SetGroupColor( LeftColor, False )
    RightLegGroup.SetGroupColor( RightColor, False )
    LeftLegGroup.SetGroupColor( LeftColor, False )
    BackArmGroup.SetGroupColor( MidColor, False )
    MidLegGroup.SetGroupColor( MidColor, False )
    
    # End the rig definition
    sfm.EndRig()
    return
    
#==================================================================================================
# Script entry
#==================================================================================================

# Construct the rig for the selected animation set
BuildRig();


    
    




