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
	"AtlasForever_OnAddonCompartmentClick",
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
	"GameFontDisableSmall",
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
	"ShortestPathForever",
	"QuestieDB",
	"LibQuestieDB",
	"C_SuperTrack",
	"UiMapPoint",
	"UIParent",
	"UISpecialFrames",
	"UnitPosition",
	"time",
}

-- A translation's lines are as long as its phrases.
files["Locales/*.lua"] = { max_line_length = false }
files["Data/*.lua"] = { max_line_length = false }
