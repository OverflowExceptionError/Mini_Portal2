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
    boneRoot      = sfmUtils.FindFirstDag( [ "sphere_root" ], True )
    boneaxelZ   = sfmUtils.FindFirstDag( [ "axel_center_z" ], True )
    boneaxelY    = sfmUtils.FindFirstDag( [ "axel_center_y" ], True )
    boneaxelX    = sfmUtils.FindFirstDag( [ "axel_center_x" ], True )
    boneBandY    = sfmUtils.FindFirstDag( [ "bandY_joint" ], True ) 
    boneBandZ    = sfmUtils.FindFirstDag( [ "bandZ_joint" ], True )
    boneEye      = sfmUtils.FindFirstDag( [ "eyeball_eye" ], True )
    bonePupil      = sfmUtils.FindFirstDag( [ "eyelight_aimjoint" ], True )
    
    bonePistBKJ_01 = sfmUtils.FindFirstDag( [ "eyeball_pistons_backjoint_01" ], True )
    bonePistBKJ_02 = sfmUtils.FindFirstDag( [ "eyeball_pistons_backjoint_02" ], True )
    bonePistBKJ_03 = sfmUtils.FindFirstDag( [ "eyeball_pistons_backjoint_03" ], True )    
    bonePistBKJ_04 = sfmUtils.FindFirstDag( [ "eyeball_pistons_backjoint_04" ], True )
    bonePistBKJ_05 = sfmUtils.FindFirstDag( [ "eyeball_pistons_backjoint_05" ], True )
    bonePistBKJ_06 = sfmUtils.FindFirstDag( [ "eyeball_pistons_backjoint_06" ], True )
	
    bonePistFRJ_01 = sfmUtils.FindFirstDag( [ "eyeball_pistons_frontjoint_01" ], True )
    bonePistFRJ_02 = sfmUtils.FindFirstDag( [ "eyeball_pistons_frontjoint_02" ], True )
    bonePistFRJ_03 = sfmUtils.FindFirstDag( [ "eyeball_pistons_frontjoint_03" ], True )    
    bonePistFRJ_04 = sfmUtils.FindFirstDag( [ "eyeball_pistons_frontjoint_04" ], True )
    bonePistFRJ_05 = sfmUtils.FindFirstDag( [ "eyeball_pistons_frontjoint_05" ], True )
    bonePistFRJ_06 = sfmUtils.FindFirstDag( [ "eyeball_pistons_frontjoint_06" ], True )
   
    boneCOG = sfmUtils.FindFirstDag( [ "cog_rotation" ], True )  

    #==============================================================================================
    # Create the rig handles and constrain them to existing bones
    #==============================================================================================
    rigRoot    = sfmUtils.CreateConstrainedHandle( "rig_root",     boneRoot,    bCreateControls=False )
    rigRotator    = sfmUtils.CreateConstrainedHandle( "rig_rotator",     boneRoot,    bCreateControls=False )
    rigaxelZ  = sfmUtils.CreateConstrainedHandle( "rig_axel_z",   boneaxelZ,  bCreateControls=False )
    rigaxelX  = sfmUtils.CreateConstrainedHandle( "rig_axel_x",   boneaxelX,  bCreateControls=False )
    rigaxelY  = sfmUtils.CreateConstrainedHandle( "rig_axel_y",   boneaxelY,  bCreateControls=False )
    rigbandZ  = sfmUtils.CreateConstrainedHandle( "rig_band_z",  boneBandZ,  bCreateControls=False )	
    rigbandY  = sfmUtils.CreateConstrainedHandle( "rig_band_y",  boneBandY,  bCreateControls=False )

    rigEye   = sfmUtils.CreateConstrainedHandle( "rig_outer_eye",    boneEye,  bCreateControls=False )
    rigPupil    = sfmUtils.CreateConstrainedHandle( "rig_inner_eye",     bonePupil,    bCreateControls=False )
       
    rigPistFRJ_01 = CreateAimConstraint( bonePistBKJ_01, bonePistFRJ_01, bCreateControls=True )
    rigPistFRJ_02 = CreateAimConstraint( bonePistBKJ_02, bonePistFRJ_02, bCreateControls=True )	
    rigPistFRJ_03 = CreateAimConstraint( bonePistBKJ_03, bonePistFRJ_03, bCreateControls=True )
    rigPistFRJ_04 = CreateAimConstraint( bonePistBKJ_04, bonePistFRJ_04, bCreateControls=True )	
    rigPistFRJ_05 = CreateAimConstraint( bonePistBKJ_05, bonePistFRJ_05, bCreateControls=True )
    rigPistFRJ_06 = CreateAimConstraint( bonePistBKJ_06, bonePistFRJ_06, bCreateControls=True )
	
    rigPistBKJ_01 = CreateAimConstraint( bonePistFRJ_01, bonePistBKJ_01, bCreateControls=True )
    rigPistBKJ_02 = CreateAimConstraint( bonePistFRJ_02, bonePistBKJ_02, bCreateControls=True )	
    rigPistBKJ_03 = CreateAimConstraint( bonePistFRJ_03, bonePistBKJ_03, bCreateControls=True )
    rigPistBKJ_04 = CreateAimConstraint( bonePistFRJ_04, bonePistBKJ_04, bCreateControls=True )	
    rigPistBKJ_05 = CreateAimConstraint( bonePistFRJ_05, bonePistBKJ_05, bCreateControls=True )
    rigPistBKJ_06 = CreateAimConstraint( bonePistFRJ_06, bonePistBKJ_06, bCreateControls=True )
	
	# Create a list of all of the rig dags
    allRigHandles = [ rigRoot, rigaxelZ, rigaxelX, rigaxelY, rigbandZ, rigbandY, rigEye, rigPupil ];
 
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
    sfmUtils.ParentMaintainWorld( rigaxelZ,        rigRotator )
    sfmUtils.ParentMaintainWorld( rigaxelX,        rigRotator )
    sfmUtils.ParentMaintainWorld( rigaxelY,        rigRotator )
    #sfmUtils.ParentMaintainWorld( rigbandZ,        rigRoot )
    #sfmUtils.ParentMaintainWorld( rigbandY,         rigRoot )
    sfmUtils.ParentMaintainWorld( rigEye,          rigaxelX )
    sfmUtils.ParentMaintainWorld( rigPupil,          rigEye )

    # Set the defaults of the rig transforms to the current locations. Defaults are stored in local
    # space, so while the parent operation tries to preserve default values it is cleaner to just
    # set them once the final hierarchy is constructed.
    sfm.SetDefault()    
    
    #==============================================================================================
    # Create constraints to drive the bone transforms using the rig handles
    #==============================================================================================
    
    # The following bones are simply constrained directly to a rig handle
    sfmUtils.CreatePointOrientConstraint( rigRoot,      boneRoot        )
    sfmUtils.CreatePointOrientConstraint( rigaxelZ,      boneaxelZ        )
    sfmUtils.CreatePointOrientConstraint( rigaxelX,      boneaxelX        )
    sfmUtils.CreatePointOrientConstraint( rigaxelY,      boneaxelY        )
        
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
    
    sfmUtils.AddDagControlsToGroup( rigBodyGroup, rigaxelZ, rigaxelX, rigaxelY, rigbandZ, rigbandY, rigEye, rigPupil )  

    # Set the control group visiblity, this is done through the rig so it can track which
    # groups it hid, so they can be set back to being visible when the rig is detached.
    HideControlGroups( rig, rootGroup, "Body", "Arms", "Legs", "Unknown", "Other", "Root" )      
        
    #Re-order the groups
    rootGroup.MoveChildToBottom( rigBodyGroup )
     
        

    #==============================================================================================
    # Set the selection groups colors
    #==============================================================================================
    topLevelColor = vs.Color( 0, 128, 255, 255 )
    
    rigBodyGroup.SetGroupColor( topLevelColor, False )
    attachmentGroup.SetGroupColor( topLevelColor, False )
    
    
    # End the rig definition
    sfm.EndRig()
    return
    
#==================================================================================================
# Script entry
#==================================================================================================

# Construct the rig for the selected animation set
BuildRig();


    
    




