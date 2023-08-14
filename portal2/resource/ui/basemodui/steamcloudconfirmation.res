"Resource/UI/SteamCloudConfirmation.res"
{
	"SteamCloudConfirmation"
	{
		"ControlName"		"Frame"
		"fieldName"		"SteamCloudConfirmation"
		"xpos"			"c-200"
		"ypos"			"c-75"
		"wide"			"400"
		"tall"                  "150"
		"autoResize"		"0"
		"pinCorner"		"0"
		"visible"		"1"
		"enabled"		"1"
		"tabPosition"		"0"
	}

	"ImgCloudImage"
	{
		"ControlName"			"ImagePanel"
		"fieldName"			"ImgCloudImage"
		"xpos"				"0"
		"ypos"				"0"
		"zpos"				"0"
		"wide"				"400"
		"tall"				"86"
		"scaleImage"			"1"
		"pinCorner"			"0"
		"visible"			"1"
		"enabled"			"1"
		"tabPosition"			"0"
		"image"				"resource/cloud_bg_image"
		"scaleImage"			"1"
	}

	"ImgLevelBack"
	{
		"ControlName"			"Panel"
		"fieldName"			"ImgLevelBack"
		"xpos"				"0"
		"ypos"				"61"
		"zpos"				"1"
		"wide"				"400"
		"tall"				"90"
		"autoResize"			"0"
		"pinCorner"			"0"
		"visible"			"1"
		"enabled"			"1"
		"tabPosition"			"0"
		"bgcolor_override"		"44 44 44 255"
		"PaintBackgroundType"	"2" 
	}

	"LblCloudTitle"
	{
		"ControlName"		"Label"
		"fieldName"		"LblCloudTitle"
		"xpos"			"0"
		"ypos"			"6"
		"zpos"			"2"
		"wide"			"400"
		"tall"			"18"
		"autoResize"		"0"
		"pinCorner"		"0"
		"visible"		"1"
		"enabled"		"1"
		"tabPosition"		"0"
		"labelText"		"#L4D360UI_Cloud_WelcomeTitle"
		"textAlignment"		"center"
		"font"			"FrameTitle"
	}

	"LblCloudDescription"
	{
		"ControlName"		"Label"
		"fieldName"		"LblCloudDescription"
		"xpos"			"10"
		"ypos"			"27"
		"zpos"			"2"
		"wide"			"380"
		"tall"			"30"
		"autoResize"		"0"
		"pinCorner"		"0"
		"visible"		"1"
		"enabled"		"1"
		"tabPosition"		"0"
		"labelText"		"#L4D360UI_Cloud_Subtitle"
		"textAlignment"		"west"
		"wrap"                  "1"
	}

	"CheckButtonCloud"
	{
		"ControlName"		"CvarToggleCheckButton_GameUI"
		"fieldName"		"CheckButtonCloud"
		"xpos"			"6"
		"ypos"			"65"
		"zpos"			"2"
		"wide"			"14"
		"tall"			"14"
		"autoResize"		"0"
		"pinCorner"		"0"
		"visible"		"1"
		"enabled"		"1"
		"tabPosition"		"2"
		"textAlignment"		"west"
		"dulltext"		"0"
		"brighttext"		"0"
		"wrap"			"0"
		"Default"		"0"
	}

	"LblKeepInSyncTip"
	{
		"ControlName"		"Label"
		"fieldName"		"LblKeepInSyncTip"
		"xpos"			"25"
		"ypos"			"65"
		"zpos"			"2"
		"wide"			"375"
		"tall"			"14"
		"autoResize"		"0"
		"pinCorner"		"0"
		"visible"		"1"
		"enabled"		"1"
		"tabPosition"		"0"
		"labelText"		"#L4D360UI_Cloud_KeepInSync_Tip"
		"textAlignment"		"west"
		"font"			"DefaultBold"
	}

	"LblFeaturesinclude"
	{
		"ControlName"		"Label"
		"fieldName"		"LblFeaturesinclude"
		"xpos"			"25"
		"ypos"			"80"
		"zpos"			"2"
		"wide"			"375"
		"tall"			"14"
		"autoResize"		"0"
		"pinCorner"		"0"
		"visible"		"1"
		"enabled"		"1"
		"tabPosition"		"0"
		"labelText"		"#L4D360UI_Cloud_FeatureInclude"
		"textAlignment"		"west"
		"wrap"                  "1"
		"font"			"Default"
	}

	"LblFeaturesInput"
	{
		"ControlName"		"Label"
		"fieldName"		"LblFeaturesInput"
		"xpos"			"25"
		"ypos"			"95"
		"zpos"			"2"
		"wide"			"375"
		"tall"			"15"
		"autoResize"		"0"
		"pinCorner"		"0"
		"visible"		"1"
		"enabled"		"1"
		"tabPosition"		"0"
		"labelText"		"#L4D360UI_Cloud_FeaturesInput"
		"textAlignment"		"west"
		"wrap"                  "1"
		"font"			"Default"
	}

	"LblFeaturesMultiplayer"
	{
		"ControlName"		"Label"
		"fieldName"		"LblCloudTitle"
		"xpos"			"25"
		"ypos"			"110"
		"zpos"			"2"
		"wide"			"375"
		"tall"			"15"
		"autoResize"		"0"
		"pinCorner"		"0"
		"visible"		"1"
		"enabled"		"1"
		"tabPosition"		"0"
		"labelText"		"#L4D360UI_Cloud_FeaturesMultiplayer"
		"textAlignment"		"west"
		"wrap"                  "1"
		"font"			"Default"
	}

	"LblOptionsAccess"
	{
		"ControlName"		"Label"
		"fieldName"		"LblOptionsAccess"
		"xpos"			"25"
		"ypos"			"130"
		"zpos"			"2"
		"wide"			"355"
		"tall"			"15"
		"autoResize"		"0"
		"pinCorner"		"0"
		"visible"		"0"
		"enabled"		"1"
		"tabPosition"		"0"
		"labelText"		"#L4D360UI_Cloud_Options_access"
		"textAlignment"		"west"
		"wrap"                  "1"
		"font"			"DefaultVerySmall"
	}

	"BtnOK"
	{
		"ControlName"			"Button"
		"fieldName"			"BtnOK"
		"xpos"				"320"
		"ypos"				"127"
		"zpos"				"2"
		"wide"				"60"
		"tall"				"20"
		"autoResize"			"0"
		"pinCorner"			"0"
		"visible"			"1"
		"enabled"			"1"
		"tabPosition"			"0"
		"AllCaps"			"1"
		"labelText"			"#GameUI_OK"
		"font"				"Default"
		"textAlignment"			"center"
		"command"			"OK"
	}

}