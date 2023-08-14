"Resource/UI/MainMenu_TSP.res"
{
	"MainMenu"
	{
		"ControlName"				"Frame"
		"fieldName"					"MainMenu"
		"xpos"						"0"
		"ypos"						"0"
		"wide"						"8000"
		"tall"						"8000"
		"autoResize"				"0"
		"pinCorner"					"0"
		"visible"					"1"
		"enabled"					"1"
		"tabPosition"				"0"
		"PaintBackgroundType"		"0"
	}
						
	"LblPlaying"
	{
		"ControlName"		"BaseModHybridButton" // not a button
		"fieldName"				"LblPlaying"
		"xpos"							"26"
		"ypos"							"45"
		"wide"							"400"
		"tall"								"50"
		"autoResize"				"0"
		"pinCorner"				"0"
		"visible"						"1"
		"enabled"					"0" // so it's disabled
		"labelText"				"THE STANLEY PARABLE"
		"style"							"MainMenuHeader2"
	}
	
	"LblGame"
	{
		"ControlName"		"BaseModHybridButton" // still not a button
		"fieldName"				"LblGame"
		"xpos"							"26"
		"ypos"							"65"
		"wide"							"400"
		"tall"								"50"
		"autoResize"				"0"
		"pinCorner"				"0"
		"visible"						"1"
		"enabled"					"0" // and guess what!!?!?!??
		"labelText"				"#TSP_Menu_Header_Demo"
		"style"							"MainMenuHeader1"
	}
	
	// Single player
	
	"BtnPlaySolo"
	{
		"ControlName"				"BaseModHybridButton"
		"fieldName"					"BtnPlaySolo"
		"xpos"						"26"
		"ypos"						"284"
		// this is moved down to 326 if there are no files to load.
		// if anyone was to go into the save menu with no files to load
		// it'd probably look fugly. so don't.
		"wide"						"220"
		"tall"						"800"
		"autoResize"				"0"
		"pinCorner"					"0"
		"visible"					"1"
		"enabled"					"1"
		"tabPosition"				"0"
		"navUp"						"BtnQuit"
		"navDown"					"BtnLoad"
		"labelText"					"#PORTAL2_MainMenu_Solo_Demo"
		"style"						"MainMenuButton"
		"command"					"SoloPlay"
		"ActivationType"			"1"
	}
	
	"BtnLoad"
	{
		"ControlName"				"BaseModHybridButton"
		"fieldName"					"BtnLoad"
		"xpos"						"26"
		// "ypos"						"284"
		"ypos"						"326"
		"wide"						"220"
		"tall"						"800"
		"autoResize"				"0"
		"pinCorner"					"0"
		"visible"					"1"
		"enabled"					"1"
		"tabPosition"				"0"
		"navUp"						"BtnPlaySolo"
		"navDown"					"BtnOptions"
		"labelText"					"#PORTAL2_MainMenu_Load"
		"style"						"MainMenuButton"
		"command"					"OpenLoadGameDialog"
		"ActivationType"			"1"
	}

	"BtnOptions"
	{
		"ControlName"				"BaseModHybridButton"
		"fieldName"					"BtnOptions"
		"xpos"						"26"
		"ypos"						"368"
		"wide"						"220"
		"tall"						"50"
		"autoResize"				"0"
		"pinCorner"					"0"
		"visible"					"1"
		"enabled"					"1"
		"tabPosition"				"0"
		"navUp"						"BtnLoad"
		"navDown"					"BtnQuit"
		"labelText"					"#PORTAL2_MainMenu_Options"
		"style"						"MainMenuButton"
		"command"					"Options"
		"ActivationType"			"1"
	}

	"BtnQuit" [!$GAMECONSOLE]
	{
		"ControlName"				"BaseModHybridButton"
		"fieldName"					"BtnQuit"
		"xpos"						"26"
		"ypos"						"410"
		"wide"						"220"
		"tall"						"50"
		"autoResize"				"0"
		"pinCorner"					"0"
		"visible"					"1"
		"enabled"					"1"
		"tabPosition"				"0"
		"navUp"						"BtnOptions"
		"navDown"					"BtnPlaySolo"
		"labelText"					"#PORTAL2_MainMenu_Quit"
		"style"						"MainMenuButton"
		"command"					"QuitGame_NoConfirm"
		"ActivationType"			"1"
	}
}
