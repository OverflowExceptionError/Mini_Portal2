"Resource/UI/tspvideo.res"
{
	"Video"
	{
		"ControlName"		"Frame"
		"fieldName"			"Video"
		"xpos"				"0"
		"ypos"				"0"
		"wide"				"800"
		"tall"				"600"
		"autoResize"		"0"
		"visible"			"1"
		"enabled"			"1"
		"tabPosition"		"0"
		"dialogstyle"		"1"
	}

	"DrpAspectRatio"
	{
		"ControlName"		"BaseModHybridButton"
		"fieldName"			"DrpAspectRatio"
		"xpos"				"26"
		"ypos"				"86"
		"wide"				"450"
		"tall"				"20"
		"visible"			"1"
		"enabled"			"1"
		"tabPosition"		"0"
		"navUp"				"BtnOK"
		"navDown"			"DrpResolution"
		"labelText"			"#GameUI_AspectRatio"
		"style"				"DialogListButton"
		"list"
		{
			"#GameUI_AspectNormal"		"#GameUI_AspectNormal"
			"#GameUI_AspectWide16x9"	"#GameUI_AspectWide16x9"
			"#GameUI_AspectWide16x10"	"#GameUI_AspectWide16x10"
		}
	}
	
	"DrpResolution"
	{
		"ControlName"		"BaseModHybridButton"
		"fieldName"			"DrpResolution"
		"xpos"				"26"
		"ypos"				"128"
		"wide"				"450"
		"tall"				"20"
		"visible"			"1"
		"enabled"			"1"
		"tabPosition"		"0"
		"navUp"				"DrpAspectRatio"
		"navDown"			"DrpDisplayMode"
		"labelText"			"#GameUI_Resolution"
		"style"				"DialogListButton"
		"list"
		{
			"_res0"		"_res0"
			"_res1"		"_res1"
			"_res2"		"_res2"
			"_res3"		"_res3"
			"_res4"		"_res4"
			"_res5"		"_res5"
			"_res6"		"_res6"
			"_res7"		"_res7"
			"_res8"		"_res8"
			"_res9"		"_res9"
			"_res:"		"_res:"
			"_res;"		"_res;"
			"_res<"		"_res<"
			"_res="		"_res="
			"_res>"		"_res>"
			"_res?"		"_res?"
			"_res@"		"_res@"
			"_resA"		"_resA"
			"_resB"		"_resB"	
			"_resC"		"_resC"
			"_resD"		"_resD"
			"_resE"		"_resE"
			"_resF"		"_resF"
			"_resG"		"_resG"
			"_resH"		"_resH"
			"_resI"		"_resI"
			"_resJ"		"_resJ"
			"_resK"		"_resK"
			"_resL"		"_resL"
			"_resM"		"_resM"
			"_resN"		"_resN"
			"_resO"		"_resO"
			"_resP"		"_resP"
			"_resQ"		"_resQ"
			"_resR"		"_resR"
			"_resS"		"_resS"
			"_resT"		"_resT"
			"_resU"		"_resU"
			"_resV"		"_resV"
			"_resW"		"_resW"
			"_resX"		"_resX"
			"_resY"		"_resY"
			"_resZ"		"_resZ" 
		}
	}
	
	"DrpDisplayMode"
	{
		"ControlName"		"BaseModHybridButton"
		"fieldName"			"DrpDisplayMode"
		"xpos"				"26"
		"ypos"				"170"
		"wide"				"450"
		"tall"				"20"
		"visible"			"1"
		"enabled"			"1"
		"tabPosition"		"0"
		"navUp"				"DrpResolution"
		"navDown"			"DrpPowerSavingsMode"
		"labelText"			"#GameUI_DisplayMode"
		"style"				"DialogListButton"
		"list"
		{
			"#GameUI_Fullscreen"						"#GameUI_Fullscreen"
			"#GameUI_Windowed"							"#GameUI_Windowed"
			"#L4D360UI_VideoOptions_Windowed_NoBorder"	"#L4D360UI_VideoOptions_Windowed_NoBorder"	[!$OSX]
		}
	}
	
	"DrpPowerSavingsMode"
	{
		"ControlName"		"BaseModHybridButton"
		"fieldName"			"DrpPowerSavingsMode"
		"xpos"				"26"
		"ypos"				"212"
		"wide"				"450"
		"tall"				"20"
		"visible"			"1"
		"enabled"			"1"
		"tabPosition"		"0"
		"navUp"				"DrpDisplayMode"
		"navDown"			"DrpOverlayPosition"
		"labelText"			"#GameUI_PowerSavingsMode"
		"style"				"DialogListButton"
		"tooltiptext"		"#PORTAL2_VideoOptions_PowerSavings_Info"
		"list"
		{
			"#L4D360UI_Disabled"			"PowerSavingsDisabled"
			"#L4D360UI_Enabled"				"PowerSavingsEnabled"
		}
	}

	"DrpOverlayPosition"
	{
		"ControlName"		"BaseModHybridButton"
		"fieldName"			"DrpOverlayPosition"
		"xpos"				"26"
		"ypos"				"254"
		"wide"				"450"
		"tall"				"20"
		"visible"			"1"
		"enabled"			"1"
		"tabPosition"		"0"
		"navUp"				"DrpPowerSavingsMode"
		"navDown"			"DrpFOV"
		"labelText"			"#GameUI_OverlayPosition"
		"style"				"DialogListButton"
		"list"
		{
			"#TSPUI_TL"			"TopLeft"
			"#TSPUI_TR"			"TopRight"
			"#TSPUI_BL"			"BotLeft"
			"#TSPUI_BR"			"BotRight"
		}
	}

	"DrpFOV"
	{
		"ControlName"		"SliderControl"
		"fieldName"			"DrpFOV"
		"xpos"				"26"
		"ypos"				"308"
		"wide"				"450"
		"tall"				"20"
		"visible"			"1"
		"enabled"			"1"
		"tabPosition"		"0"
		"minValue"			"90.0"
		"maxValue"			"130.0"
		"stepSize"			"5"
		"navUp"				"DrpOverlayPosition"
		"navDown"			"BtnAdvanced"
		"conCommand"		"cl_fov"
		"style"				"DialogListButton"

		"BtnDropButton"
		{
			"ControlName"			"BaseModHybridButton"
			"fieldName"				"BtnDropButton"
			"xpos"					"0"
			"ypos"					"0"
			"zpos"					"0"
			"wide"					"450"
			"tall"					"0"
			"autoResize"			"1"
			"pinCorner"				"0"
			"visible"				"1"
			"enabled"				"1"
			"tabPosition"			"0"
			"labelText"				"#Valve_Hud_CamFOV"
			"style"					"LeftDialogButton"
			"command"				""
			"ActivationType"		"1"
			"usablePlayerIndex"		"nobody"
		}
	}

	"BtnAdvanced"
	{
		"ControlName"			"BaseModHybridButton"
		"fieldName"				"BtnAdvanced"
		"xpos"					"26"
		"ypos"				"336"
		"wide"					"200"
		"tall"					"20"
		"visible"				"1"
		"enabled"				"1"
		"tabPosition"			"0"
		"navUp"					"DrpOverlayPosition"
		"navDown"				"BtnOK"
		"labelText"				"#PORTAL2_AdvancedVideoConf"
		"style"					"MainMenuButton"
		"command"				"ShowAdvanced"
	}
	
	"BtnOK"
	{
		"ControlName"				"BaseModHybridButton"
		"fieldName"					"BtnOK"
		"xpos"						"26"
		"ypos"				"382"
		"wide"						"200"
		"tall"						"20"
		"autoResize"				"0"
		"navRight"					"BtnBack"
		"navLeft"					"BtnDefaults"
		"navUp"						"BtnAdvanced"
		"navDown"					"DrpAspectRatio"
		"visible"					"1"
		"enabled"					"1"
		"tabPosition"				"0"
		"labelText"					"#L4D360UI_OK"
		"style"						"MainMenuButtonSmall"
		"command"					"OK"
		"ActivationType"			"1"
	}
	
	"BtnBack"
	{
		"ControlName"				"BaseModHybridButton"
		"fieldName"					"BtnBack"
		"xpos"						"26"
		"ypos"				"382"
		"wide"						"200"
		"tall"						"20"
		"autoResize"				"0"
		"visible"					"1"
		"enabled"					"1"
		"tabPosition"				"0"
		"navRight"					"BtnDefaults"
		"navLeft"					"BtnOK"
		"navUp"						"BtnAdvanced"
		"navDown"					"DrpAspectRatio"
		"labelText"					"#L4D360UI_Back"
		"style"						"MainMenuButtonSmall"
		"command"					"Back"
		"ActivationType"			"1"
	}

	"BtnDefaults"
	{
		"ControlName"				"BaseModHybridButton"
		"fieldName"					"BtnDefaults"
		"xpos"						"26"
		"ypos"				"382"
		"wide"						"200"
		"tall"						"20"
		"navRight"					"BtnOK"
		"navLeft"					"BtnBack"
		"navUp"						"BtnAdvanced"
		"navDown"					"DrpAspectRatio"
		"autoResize"				"0"
		"visible"					"1"
		"enabled"					"1"
		"tabPosition"				"0"
		"labelText"					"#L4D360UI_Controller_Default"
		"style"						"MainMenuButtonSmall"
		"command"					"Defaults"
		"ActivationType"			"1"
	}
}