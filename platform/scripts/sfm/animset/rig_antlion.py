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
    boneRoot      = sfmUtils.FindFirstDag( [ "RootTransform" ], True )
    bonePelvis    = sfmUtils.FindFirstDag( [ "Antlion.Body_Bone" ], True )
    boneSpine0    = sfmUtils.FindFirstDag( [ "Antlion.Back_Bone" ], True )
    boneSpine1    = sfmUtils.FindFirstDag( [ "Antlion.Chest_Bone" ], True )
    #boneSpine2    = sfmUtils.FindFirstDag( [ "ValveBiped.Bip01_Spine2",		"Bip01_Spine2",		"bip_spine_2" ], True ) 
    #boneSpine3    = sfmUtils.FindFirstDag( [ "ValveBiped.Bip01_Spine3",		"Bip01_Spine3",		"bip_spine_3",	"ValveBiped.Bip01_Spine4" ], True )
    #boneNeck      = sfmUtils.FindFirstDag( [ "ValveBiped.Bip01_Neck",		"Bip01_Neck",		"bip_neck_0",	"bip_neck", "ValveBiped.Bip01_Neck1" ], True )
    boneHead      = sfmUtils.FindFirstDag( [ "Antlion.Head_Bone" ], True )
    
    boneUpperLegFR = sfmUtils.FindFirstDag( [ "Antlion.LegR1_Bone" ], True )
    boneLowerLegFR = sfmUtils.FindFirstDag( [ "Antlion.LegR2_Bone" ], True )
    boneFootFR     = sfmUtils.FindFirstDag( [ "Antlion.LegR3_Bone" ], True )
   #boneToeFR      = sfmUtils.FindFirstDag( [ "ValveBiped.Bip01_R_Toe0",     "Bip01_L_Toe0",     "bip_toe_L" ], True ) 
    boneUpperLegBR = sfmUtils.FindFirstDag( [ "Antlion.LegMidR1_Bone" ], True )
    boneLowerLegBR = sfmUtils.FindFirstDag( [ "Antlion.LegMidR2_Bone" ], True )
    boneFootBR     = sfmUtils.FindFirstDag( [ "Antlion.LegMidR3_Bone" ], True )
   #boneToeBR      = sfmUtils.FindFirstDag( [ "ValveBiped.Bip01_R_Toe0",     "Bip01_L_Toe0",     "bip_toe_L" ], True ) 
   #boneCollarR   = sfmUtils.FindFirstDag( [ "Antlion.ArmR1_Bone" ], True )        
    boneUpperArmR = sfmUtils.FindFirstDag( [ "Antlion.ArmR1_Bone" ], True ) 
    boneLowerArmR = sfmUtils.FindFirstDag( [ "Antlion.ArmR2_Bone" ], True ) 
    boneHandR     = sfmUtils.FindFirstDag( [ "Antlion.ArmR3_Bone" ], True )
   
    boneUpperLegFL = sfmUtils.FindFirstDag( [ "Antlion.LegL1_Bone" ], True )
    boneLowerLegFL = sfmUtils.FindFirstDag( [ "Antlion.LegL2_Bone" ], True )
    boneFootFL     = sfmUtils.FindFirstDag( [ "Antlion.LegL3_Bone" ], True )
   #boneToeFL      = sfmUtils.FindFirstDag( [ "ValveBiped.Bip01_L_Toe0",     "Bip01_L_Toe0",     "bip_toe_L" ], True ) 
    boneUpperLegBL = sfmUtils.FindFirstDag( [ "Antlion.LegMidL1_Bone" ], True )
    boneLowerLegBL = sfmUtils.FindFirstDag( [ "Antlion.LegMidL2_Bone" ], True )
    boneFootBL     = sfmUtils.FindFirstDag( [ "Antlion.LegMidL3_Bone" ], True )
   #boneToeBL      = sfmUtils.FindFirstDag( [ "ValveBiped.Bip01_L_Toe0",     "Bip01_L_Toe0",     "bip_toe_L" ], True ) 
   #boneCollarL   = sfmUtils.FindFirstDag( [ "Antlion.ArmL1_Bone" ], True )        
    boneUpperArmL = sfmUtils.FindFirstDag( [ "Antlion.ArmL1_Bone" ], True ) 
    boneLowerArmL = sfmUtils.FindFirstDag( [ "Antlion.ArmL2_Bone" ], True ) 
    boneHandL     = sfmUtils.FindFirstDag( [ "Antlion.ArmL3_Bone" ], True )
    

    #==============================================================================================
    # Create the rig handles and constrain them to existing bones
    #==============================================================================================
    rigRoot    = sfmUtils.CreateConstrainedHandle( "rig_root",     boneRoot,    bCreateControls=False )
    rigPelvis  = sfmUtils.CreateConstrainedHandle( "rig_pelvis",   bonePelvis,  bCreateControls=False )
    rigSpine0  = sfmUtils.CreateConstrainedHandle( "rig_spine_0",  boneSpine0,  bCreateControls=False )
    rigSpine1  = sfmUtils.CreateConstrainedHandle( "rig_spine_1",  boneSpine1,  bCreateControls=False )
   #rigSpine2  = sfmUtils.CreateConstrainedHandle( "rig_spine_2",  boneSpine2,  bCreateControls=False )
   #rigChest   = sfmUtils.CreateConstrainedHandle( "rig_chest",    boneSpine3,  bCreateControls=False )
   #rigNeck    = sfmUtils.CreateConstrainedHandle( "rig_neck",     boneNeck,    bCreateControls=False )
    rigHead    = sfmUtils.CreateConstrainedHandle( "rig_head",     boneHead,    bCreateControls=False )
    
    rigFootBR   = sfmUtils.CreateConstrainedHandle( "rig_foot_BR",   boneFootBR,   bCreateControls=False )
    rigFootFR   = sfmUtils.CreateConstrainedHandle( "rig_foot_FR",   boneFootFR,   bCreateControls=False )
   #rigToeR    = sfmUtils.CreateConstrainedHandle( "rig_toe_R",    boneToeR,    bCreateControls=False )
   #rigCollarR = sfmUtils.CreateConstrainedHandle( "rig_collar_R", boneCollarR, bCreateControls=False )
    rigHandR   = sfmUtils.CreateConstrainedHandle( "rig_hand_R",   boneHandR,   bCreateControls=False )
    rigFootBL   = sfmUtils.CreateConstrainedHandle( "rig_foot_BL",   boneFootBL,   bCreateControls=False )	
    rigFootFL   = sfmUtils.CreateConstrainedHandle( "rig_foot_FL",   boneFootFL,   bCreateControls=False )
   #rigToeL    = sfmUtils.CreateConstrainedHandle( "rig_toe_L",    boneToeL,    bCreateControls=False )
   #rigCollarL = sfmUtils.CreateConstrainedHandle( "rig_collar_L", boneCollarL, bCreateControls=False )
    rigHandL   = sfmUtils.CreateConstrainedHandle( "rig_hand_L",   boneHandL,   bCreateControls=False )
        
    
    # Use the direction from the heel to the toe to compute the knee offsets, 
    # this makes the knee offset indpendent of the inital orientation of the model.
    vKneeOffsetBR = ComputeVectorBetweenBones( boneFootBR, boneLowerLegBR, 10 )
    vKneeOffsetBL = ComputeVectorBetweenBones( boneFootBL, boneLowerLegBL, 10 )
    vKneeOffsetFR = ComputeVectorBetweenBones( boneFootFR, boneLowerLegFR, 10 )
    vKneeOffsetFL = ComputeVectorBetweenBones( boneFootFL, boneLowerLegFL, 10 )
    
    
    rigKneeFR   = sfmUtils.CreateOffsetHandle( "rig_knee_FR",  boneLowerLegFR, vKneeOffsetFR,  bCreateControls=False )   
    rigKneeFL   = sfmUtils.CreateOffsetHandle( "rig_knee_FL",  boneLowerLegFL, vKneeOffsetFL,  bCreateControls=False )
    rigKneeBR   = sfmUtils.CreateOffsetHandle( "rig_knee_BR",  boneLowerLegBR, vKneeOffsetBR,  bCreateControls=False )   
    rigKneeBL   = sfmUtils.CreateOffsetHandle( "rig_knee_BL",  boneLowerLegBL, vKneeOffsetBL,  bCreateControls=False )
    rigElbowR  = sfmUtils.CreateOffsetHandle( "rig_elbow_R", boneLowerArmR, -vKneeOffsetBR,  bCreateControls=False )
    rigElbowL  = sfmUtils.CreateOffsetHandle( "rig_elbow_L", boneLowerArmL, -vKneeOffsetBL,  bCreateControls=False )
    
    # Create a helper handle which will remain constrained to the each foot position that can be used for parenting.
    rigFootHelperBR = sfmUtils.CreateConstrainedHandle( "rig_footHelper_BR", boneFootBR, bCreateControls=False )
    rigFootHelperBL = sfmUtils.CreateConstrainedHandle( "rig_footHelper_BL", boneFootBL, bCreateControls=False )
    rigFootHelperFR = sfmUtils.CreateConstrainedHandle( "rig_footHelper_FR", boneFootFR, bCreateControls=False )
    rigFootHelperFL = sfmUtils.CreateConstrainedHandle( "rig_footHelper_FL", boneFootFL, bCreateControls=False )
    
    # Create a list of all of the rig dags
    allRigHandles = [ rigRoot, rigPelvis, rigSpine0, rigSpine1, rigHead,
                      rigElbowR, rigHandR, rigKneeBR, rigFootBR, rigKneeFR, rigFootFR,
                      rigElbowL, rigHandL, rigKneeBL, rigFootBL, rigKneeFL, rigFootFL ];
    
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
    sfmUtils.ParentMaintainWorld( rigSpine1,        rigSpine0 )
   #sfmUtils.ParentMaintainWorld( rigSpine2,        rigSpine1 )
   #sfmUtils.ParentMaintainWorld( rigChest,         rigSpine2 )
   #sfmUtils.ParentMaintainWorld( rigNeck,          rigChest )
    sfmUtils.ParentMaintainWorld( rigHead,          rigSpine1 )
    
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
   #sfmUtils.ParentMaintainWorld( rigToeR,          rigFootHelperR )
   #sfmUtils.ParentMaintainWorld( rigToeL,          rigFootHelperL )
    
   #sfmUtils.ParentMaintainWorld( rigCollarR,       rigSpine1 )
    sfmUtils.ParentMaintainWorld( rigElbowR,        rigSpine1 )
    sfmUtils.ParentMaintainWorld( rigHandR,	    rigRoot )
   #sfmUtils.ParentMaintainWorld( rigCollarL,       rigSpine1 )
    sfmUtils.ParentMaintainWorld( rigElbowL,        rigSpine1 )
    sfmUtils.ParentMaintainWorld( rigHandL,	    rigRoot )
    
    # Create the hips control, this allows a pelvis rotation that does not effect the spine,
    # it is only used for rotation so a position control is not created. Additionally add the
    # new control to the selection so the that set default call operates on it too.
    rigHips = sfmUtils.CreateHandleAt( "rig_hips", rigPelvis, False, True )
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
    sfmUtils.CreatePointOrientConstraint( rigSpine1,    boneSpine1      )
   #sfmUtils.CreatePointOrientConstraint( rigSpine2,    boneSpine2      )
   #sfmUtils.CreatePointOrientConstraint( rigChest,     boneSpine3      )
   #sfmUtils.CreatePointOrientConstraint( rigNeck,      boneNeck        )
    sfmUtils.CreatePointOrientConstraint( rigHead,      boneHead        )
   #sfmUtils.CreatePointOrientConstraint( rigCollarR,   boneCollarR     )
   #sfmUtils.CreatePointOrientConstraint( rigCollarL,   boneCollarL     )
   #sfmUtils.CreatePointOrientConstraint( rigToeFR,      boneToeFR        )
   #sfmUtils.CreatePointOrientConstraint( rigToeFL,      boneToeFL        )
   #sfmUtils.CreatePointOrientConstraint( rigToeBR,      boneToeBR        )
   #sfmUtils.CreatePointOrientConstraint( rigToeBL,      boneToeBL        )
    
    # Create ik constraints for the arms and legs that will control the rotation of the hip / knee and 
    # upper arm / elbow joints based on the position of the foot and hand respectively.
    sfmUtils.BuildArmLeg( rigKneeBR,  footIKTargetBR, boneUpperLegBR,  boneFootBR, True )
    sfmUtils.BuildArmLeg( rigKneeBL,  footIkTargetBL, boneUpperLegBL,  boneFootBL, True )
    sfmUtils.BuildArmLeg( rigKneeFR,  footIKTargetFR, boneUpperLegFR,  boneFootFR, True )
    sfmUtils.BuildArmLeg( rigKneeFL,  footIkTargetFL, boneUpperLegFL,  boneFootFL, True )
    sfmUtils.BuildArmLeg( rigElbowR, rigHandR, boneUpperArmR,  boneHandR, True )
    sfmUtils.BuildArmLeg( rigElbowL, rigHandL, boneUpperArmL,  boneHandL, True )
    
    
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
    rigArmsGroup = rootGroup.CreateControlGroup( "RigArms" )
    
    RightArmGroup = rootGroup.CreateControlGroup( "RightArm" )
    LeftArmGroup = rootGroup.CreateControlGroup( "LeftArm" )
    BackRightLegGroup = rootGroup.CreateControlGroup( "BackRightLeg" )
    BackLeftLegGroup = rootGroup.CreateControlGroup( "BackLeftLeg" ) 
    FrontRightLegGroup = rootGroup.CreateControlGroup( "FrontRightLeg" )
    FrontLeftLegGroup = rootGroup.CreateControlGroup( "FrontLeftLeg" )   	
    
    sfmUtils.AddDagControlsToGroup( rigBodyGroup, rigRoot, rigPelvis, rigHips, rigSpine0, rigSpine1, rigHead )  
      
    rigArmsGroup.AddChild( RightArmGroup )
    rigArmsGroup.AddChild( LeftArmGroup )
    sfmUtils.AddDagControlsToGroup( RightArmGroup, rigElbowR, rigHandR )
    sfmUtils.AddDagControlsToGroup( LeftArmGroup, rigElbowL, rigHandL )
    
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
    
    rigBodyGroup.SetGroupColor( topLevelColor, False )
    rigArmsGroup.SetGroupColor( topLevelColor, False )
    rigLegsGroup.SetGroupColor( topLevelColor, False )
    attachmentGroup.SetGroupColor( topLevelColor, False )
    rigHelpersGroup.SetGroupColor( topLevelColor, False )
    
    RightArmGroup.SetGroupColor( RightColor, False )
    LeftArmGroup.SetGroupColor( LeftColor, False )
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


    
    




