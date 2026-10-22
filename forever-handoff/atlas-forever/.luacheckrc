std = "lua51"
max_line_length = 120
exclude_files = {
	"tools/.cache/**",
	".release/**",
	".types/**",
	"types/**",
	".claude/**",
	"reference/**",
}
ignore = { "212/_.*" } -- unused arguments prefixed with _
globals = {
	"AtlasForever",
	"AtlasForeverDB",
	"SLASH_ATLASFOREVER1",
	"SLASH_ATLASFOREVER2",
	"SlashCmdList",
}
read_globals = {
	"C_Map",
	"C_Timer",
	"CreateColor",
	"CreateFrame",
	"GameFontHighlight",
	"GameFontHighlightSmall",
	"GameFontNormal",
	"GameFontNormalLarge",
	"GameFontNormalSmall",
	"GameTooltip",
	"GetLocale",
	"GetRealZoneText",
	"GetTime",
	"GetZoneText",
	"geterrorhandler",
	"InterfaceOptions_AddCategory",
	"InCombatLockdown",
	"Settings",
	"UIParent",
	"UISpecialFrames",
	"UnitPosition",
	"time",
}

-- A translation's lines are as long as its phrases.
files["Locales/*.lua"] = { max_line_length = false }
