"Resource/UI/GameSettings_Commentary.res"
{
	"GameSettings"
	{
		"ControlName"				"Frame"
		"fieldName"					"GameSettings"
		"xpos"						"0"
		"ypos"						"0"
		"wide"						"f0"
		"tall"						"260"
		"autoResize"				"0"
		"pinCorner"					"0"
		"visible"					"1"
		"enabled"					"1"
		"tabPosition"				"0"
	}
	
	"ImgBackground"
	{
		"ControlName"			"L4DMenuBackground"
		"fieldName"				"ImgBackground"
		"xpos"					"0"
		"ypos"					"179"
		"zpos"					"-1"
		"wide"					"f0"
		"tall"					"144"
		"autoResize"			"0"
		"pinCorner"				"0"
		"visible"				"1"				[$WIN32]
		"visible"				"0"				[$GAMECONSOLE]
		"enabled"				"1"
		"tabPosition"			"0"
		"fillColor"				"0 0 0 0"
	} 
	
	"ImgLevelImage"
	{
		"ControlName"			"ImagePanel"
		"fieldName"				"ImgLevelImage"
		"xpos"					"c52"
		"ypos"					"125"
		"wide"					"200"
		"tall"					"100"
		"scaleImage"			"1"
		"pinCorner"				"0"
		"visible"				"1"
		"enabled"				"1"
		"tabPosition"			"0"
		"image"					"maps/any"
		"scaleImage"			"1"
	}
	"ImgLevelImageFrame"
	{
		"ControlName"			"ImagePanel"
		"fieldName"				"ImgLevelImageFrame"
		"xpos"					"c45" 
		"ypos"					"113" 
		"wide"					"246" 
		"tall"					"123" 
		"scaleImage"			"1"
		"pinCorner"				"0"
		"visible"				"1"
		"enabled"				"1"
		"tabPosition"			"0"
		"image"					"campaignFrame"
		"scaleImage"			"1"
	}		
	// Campaign dropdown
	"DrpMission"
	{
		"ControlName"			"DropDownMenu"
		"fieldName"				"DrpMission"
		"xpos"					"c-250"
		"ypos"					"115"
		"zpos"					"1"
		"wide"					"280"
		"tall"					"15"			[$WIN32]
		"tall"					"20"			[$GAMECONSOLE]
		"visible"				"1"
		"enabled"				"0"
		"navUp"					"BtnCancel"		[$WIN32]
		"navUp"					"BtnStartGame"	[$GAMECONSOLE]
		"navDown"				"DrpChapter"
		
		//button and label
		"BtnDropButton"
		{
			"ControlName"					"BaseModHybridButton"
			"fieldName"						"BtnDropButton"
			"xpos"							"0"
			"ypos"							"0"
			"zpos"							"2"
			"wide"							"280"
			"wideatopen"					"160"
			"tall"							"15"	[$WIN32]
			"tall"							"20"	[$GAMECONSOLE]
			"autoResize"					"1"
			"pinCorner"						"0"
			"visible"						"1"
			"enabled"						"0"
			"tabPosition"					"0"
			"labelText"						"#L4D360UI_GameSettings_Mission"
			"tooltiptext"					"#L4D360UI_GameSettings_Tooltip_Mission"
			"disabled_tooltiptext"			"#L4D360UI_Extras_Commentary"
			"style"							"DropDownButton"
			"command"						"FlmMission"
			"ActivationType"				"1" [$GAMECONSOLE]
			"EnableCondition"					"Never" [$DEMO]
		}
	}
	
	// Campaign flyout	
	"FlmMission"
	{
		"ControlName"			"FlyoutMenu"
		"fieldName"				"FlmMission"
		"visible"				"0"
		"wide"					"0"
		"tall"					"0"
		"zpos"					"4"
		"InitialFocus"			"BtnCampaign1"
		"ResourceFile"			"resource/UI/basemodui/DropDownMission.res"
	}
	
	// Chapter Dropdown
	"DrpChapter"
	{
		"ControlName"			"DropDownMenu"
		"fieldName"				"DrpChapter"
		"xpos"					"c-250"
		"ypos"					"135"			[$WIN32]
		"ypos"					"140"			[$GAMECONSOLE]
		"zpos"					"1"
		"wide"					"280"
		"tall"					"15"			[$WIN32]
		"tall"					"20"			[$GAMECONSOLE]
		"visible"				"1"
		"enabled"				"1"
		"navUp"					"DrpMission"
		"navDown"				"DrpDifficulty"
		
		//button and label
		"BtnDropButton"
		{
			"ControlName"					"BaseModHybridButton"
			"fieldName"						"BtnDropButton"
			"xpos"							"0"
			"ypos"							"0"
			"zpos"							"2"
			"wide"							"280"
			"wideatopen"					"160"
			"tall"							"15"	[$WIN32]
			"tall"							"20"	[$GAMECONSOLE]
			"autoResize"					"1"
			"pinCorner"						"0"
			"visible"						"1"
			"enabled"						"1"
			"tabPosition"					"0"
			"labelText"						"#L4D360UI_GameSettings_Chapter"
			"tooltiptext"					"#L4D360UI_GameSettings_Tooltip_Chapter"
			"disabled_tooltiptext"			"#L4D360UI_GameSettings_Tooltip_Chapter_Disabled"
			"style"							"DropDownButton"
			"command"						""
			"ActivationType"				"1" [$GAMECONSOLE]
		}
	}
	
	//flyouts		
	"FlmChapterXXautogenerated"
	{
		"ControlName"			"FlyoutMenu"
		"fieldName"				"FlmChapterFlyout"
		"visible"				"0"
		"wide"					"0"
		"tall"					"0"
		"zpos"					"4"
		"InitialFocus"			"BtnChapter1"
		"ResourceFile"			"resource/UI/basemodui/DropDownChapter.res"
	}

	// Difficulty dropdown
	"DrpDifficulty"
	{
		"ControlName"			"DropDownMenu"
		"fieldName"				"DrpDifficulty"
		"xpos"					"c-250"
		"ypos"					"155"			[$WIN32]
		"ypos"					"165"			[$GAMECONSOLE]
		"zpos"					"1"
		"wide"					"280"
		"tall"					"15"			[$WIN32]
		"tall"					"20"			[$GAMECONSOLE]
		"visible"				"1"
		"enabled"				"0"
		"navUp"					"DrpChapter"
		"navDown"				"DrpCharacter"
		
		// button and label
		"BtnDropButton"
		{
			"ControlName"					"BaseModHybridButton"
			"fieldName"						"BtnDropButton"
			"xpos"							"0"
			"ypos"							"0"
			"zpos"							"2"
			"wide"							"280"
			"wideatopen"					"160"
			"tall"							"15"	[$WIN32]
			"tall"							"20"	[$GAMECONSOLE]
			"autoResize"					"1"
			"pinCorner"						"0"
			"visible"						"1"
			"enabled"						"0"
			"tabPosition"					"0"
			"labelText"						"#L4D360UI_GameSettings_Difficulty"
			"tooltiptext"					"#L4D360UI_GameSettings_Tooltip_Difficulty"
			"disabled_tooltiptext"			"#L4D360UI_Extras_Commentary"
			"style"							"DropDownButton"
			"command"						"FlmDifficulty"
			"ActivationType"				"1" [$GAMECONSOLE]
		}
	}

	// Difficulty flyout		
	"FlmDifficulty"
	{
		"ControlName"			"FlyoutMenu"
		"fieldName"				"FlmDifficulty"
		"visible"				"0"
		"wide"					"0"
		"tall"					"0"
		"zpos"					"4"
		"InitialFocus"			"BtnNormal"
		"ResourceFile"			"resource/UI/basemodui/DropDownDifficulty.res"
	}
	
	// Character dropdown
	"DrpCharacter"
	{
		"ControlName"			"DropDownMenu"
		"fieldName"				"DrpCharacter"
		"xpos"					"c-250"	
		"ypos"					"175"		[$WIN32]
		"ypos"					"190"		[$GAMECONSOLE]
		"zpos"					"1"
		"wide"					"280"
		"tall"					"15"		[$WIN32]
		"tall"					"20"		[$GAMECONSOLE]
		"visible"				"1"
		"enabled"				"1"
		"navUp"					"DrpDifficulty"
		"navDown"				"BtnStartGame"
		
		//button and label
		"BtnDropButton"
		{
			"ControlName"					"BaseModHybridButton"
			"fieldName"						"BtnDropButton"
			"xpos"							"0"
			"ypos"							"0"
			"zpos"							"2"
			"wide"							"280"
			"wideatopen"					"160"
			"tall"							"15"	[$WIN32]
			"tall"							"20"	[$GAMECONSOLE]
			"autoResize"					"1"
			"pinCorner"						"0"
			"visible"						"1"
			"enabled"						"1"
			"tabPosition"					"0"
			"labelText"						"#L4D360UI_GameSettings_Character"
			"tooltiptext"					"#L4D360UI_GameSettings_Tooltip_Character"
			"disabled_tooltiptext"			"#L4D360UI_GameSettings_Tooltip_Character_Disabled"
			"style"							"DropDownButton"
			"command"						"FlmCharacterFlyout"
			"ActivationType"				"1" [$GAMECONSOLE]
		}
	}
	
	// Character flyout		
	"FlmCharacterFlyout"
	{
		"ControlName"			"FlyoutMenu"
		"fieldName"				"FlmCharacterFlyout"
		"visible"				"0"
		"wide"					"0"
		"tall"					"0"
		"zpos"					"4"
		"InitialFocus"			"BtnRandom"
		"ResourceFile"			"resource/UI/basemodui/DropDownCharacters.res"
	}
	
	"IconForwardArrow"
	{
		"ControlName"			"ImagePanel"
		"fieldName"				"IconForwardArrow"
		"xpos"					"c-265"		[$WIN32]	
		"xpos"					"c-275"		[$GAMECONSOLE]
		"ypos"					"195"		[$WIN32]
		"ypos"					"215"		[$GAMECONSOLE]
		"wide"					"15"        [$WIN32]
		"tall"					"15"        [$WIN32]
		"wide"					"20"        [$GAMECONSOLE]
		"tall"					"20"        [$GAMECONSOLE]
		"scaleImage"			"1"
		"pinCorner"				"0"
		"visible"				"1"
		"enabled"				"1"
		"tabPosition"			"0"
		"image"					"icon_button_arrow_right"
		"scaleImage"			"1"
	}
	"BtnStartGame"
	{
		"ControlName"			"BaseModHybridButton"
		"fieldName"				"BtnStartGame"
		"xpos"					"c-250"
		"ypos"					"195"		[$WIN32]
		"ypos"					"215"		[$GAMECONSOLE]
		"zpos"					"0"
		"wide"					"220"
		"tall"					"15"		[$WIN32]	
		"tall"					"20"		[$GAMECONSOLE]
		"autoResize"			"1"
		"pinCorner"				"0"
		"visible"				"1"
		"enabled"				"1"
		"tabPosition"			"1"
		"wrap"					"1"
		"navUp"					"DrpCharacter"
		"navDown"				"DrpMission"	[$GAMECONSOLE]
		"navDown"				"BtnCancel"		[$WIN32]
		"labelText"				"#L4D360UI_StartGame"
		"tooltiptext"			"#L4D360UI_GameSettings_Tooltip_StartGame"
		"disabled_tooltiptext"	"#L4D360UI_GameSettings_Tooltip_StartGame_Disabled"
		"style"					"DefaultButton"
		"command"				"Done"
		EnabledTextInsetX		"2"
		DisabledTextInsetX		"2"
		FocusTextInsetX			"2"
		OpenTextInsetX			"2"
	}
	
	"IconBackArrow" [$WIN32]
	{
		"ControlName"			"ImagePanel"
		"fieldName"				"IconBackArrow"
		"xpos"					"c-265"
		"ypos"					"215"
		"wide"					"15"
		"tall"					"15"
		"scaleImage"			"1"
		"pinCorner"				"0"
		"visible"				"1"
		"enabled"				"1"
		"tabPosition"			"0"
		"image"					"icon_button_arrow_left"
		"scaleImage"			"1"
	}
	"BtnCancel"	[$WIN32]
	{
		"ControlName"			"BaseModHybridButton"
		"fieldName"				"BtnCancel"
		"xpos"					"c-250"
		"ypos"					"215"
		"zpos"					"0"
		"wide"					"220"
		"tall"					"15"
		"autoResize"			"1"
		"pinCorner"				"0"
		"visible"				"0"
		"enabled"				"1"
		"tabPosition"			"0"
		"wrap"					"1"
		"navUp"					"BtnStartGame"
		"navDown"				"DrpMission"
		"labelText"				"#L4D360UI_Back_Caps"
		"tooltiptext"			"#L4D360UI_Tooltip_Back"
		"style"					"DefaultButton"
		"command"				"Back"
		EnabledTextInsetX		"2"
		DisabledTextInsetX		"2"
		FocusTextInsetX			"2"
		OpenTextInsetX			"2"
	}
}
