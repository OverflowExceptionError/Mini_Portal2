"Resource/UI/CustomMissionFlyout.res"
{
	"BtnPlayCoopWithFriends"
	{
		"ControlName"			"BaseModHybridButton"
		"fieldName"				"BtnPlayCoopWithFriends"
		"xpos"					"2"
		"ypos"					"2"
		"wide"					"150"
		"tall"					"20"
		"autoResize"			"1"
		"pinCorner"				"0"
		"visible"				"1"
		"enabled"				"1"
		"tabPosition"			"0"
		"wrap"					"1"
		"navUp"					"BtnPlaySolo"
		"navDown"				"BtnPlayCoopWithAnyone"
		"labelText"				"#L4D360UI_MainMenu_PlayCoopWithFriends"
		"tooltiptext"			"#L4D360UI_MainMenu_PlayCoopWithFriends_Tip"
		"style"					"FlyoutMenuButton"
		"command"				"PlayCoopWithFriends"
		"proportionalToParent"	"1"
		"usetitlesafe" 			"1"
		"EnableCondition" 		"LiveRequired"		
	}	
	
	"BtnPlayCoopWithAnyone"
	{
		"ControlName"			"BaseModHybridButton"
		"fieldName"				"BtnPlayCoopWithAnyone"
		"xpos"					"2"
		"ypos"					"22"
		"wide"					"150"
		"tall"					"20"
		"autoResize"			"1"
		"pinCorner"				"0"
		"visible"				"1"
		"enabled"				"0"
		"tabPosition"			"0"
		"wrap"					"1"
		"navUp"					"BtnPlayCoopWithFriends"
		"navDown"				"BtnPlaySystemLink"
		"labelText"				"#L4D360UI_MainMenu_PlayCoopWithAnyone"
		"tooltiptext"			"#L4D360UI_MainMenu_PlayCoopWithAnyone_Tip"
		"style"					"FlyoutMenuButton"
		"command"				"PlayCoopWithAnyone"
		"proportionalToParent"	"1"
		"usetitlesafe" 			"1"
		"EnableCondition" 		"LiveRequired"		
	}	
	
	"BtnPlaySystemLink"
	{
		"ControlName"			"BaseModHybridButton"
		"fieldName"				"BtnPlaySystemLink"
		"xpos"					"2"
		"ypos"					"44"
		"wide"					"150"
		"tall"					"20"
		"autoResize"			"1"
		"pinCorner"				"0"
		"visible"				"1"
		"enabled"				"1"
		"tabPosition"			"0"
		"wrap"					"1"
		"navUp"					"BtnPlayCoopWithAnyone"
		"navDown"				"BtnPlaySolo"
		"labelText"				"#L4D360UI_MainMenu_PlayCoopWithSystemLink" [$GAMECONSOLE]
		"labelText"				"#L4D360UI_MainMenu_PlayCoopLAN" [$WIN32]
		"tooltiptext"			"#L4D360UI_MainMenu_PlayCoopWithSystemLink_Tip" [$GAMECONSOLE]
		"tooltiptext"			"#L4D360UI_MainMenu_PlayCoopLAN_Tip" [$WIN32]
		"style"					"FlyoutMenuButton"
		"command"				"PlaySysLink"
		"proportionalToParent"	"1"
		"usetitlesafe" 			"1"
	}	
		
	"BtnPlaySolo"
	{
		"ControlName"			"BaseModHybridButton"
		"fieldName"				"BtnPlaySolo"
		"xpos"					"2"
		"ypos"					"66"
		"wide"					"150"
		"tall"					"20"
		"autoResize"			"1"
		"pinCorner"				"0"
		"visible"				"1"
		"enabled"				"1"
		"tabPosition"			"0"
		"wrap"					"1"
		"navUp"					"BtnPlaySystemLink"
		"navDown"				"BtnPlayCoopWithFriends"
		"labelText"				"#L4D360UI_MainMenu_PlaySolo"
		"tooltiptext"			"#L4D360UI_MainMenu_PlaySolo_Tip"
		"style"					"FlyoutMenuButton"
		"command"				"SoloPlay"
		"proportionalToParent"	"1"
		"usetitlesafe" 			"1"
	}	
			
	"PnlBackground"
	{
		"ControlName"		"Panel"
		"fieldName"			"PnlBackground"
		"xpos"				"0"
		"ypos"				"0"
		"zpos"				"-1"
		"wide"				"154"
		"tall"				"89"
		"visible"			"1"
		"enabled"			"1"
		"paintbackground"	"1"
		"paintborder"		"1"
		"proportionalToParent"	"1"
		"usetitlesafe" 			"1"
	}
}