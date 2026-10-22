---@type string, AtlasNamespace
local _, ns = ...

-- English phrases are the keys. A translation lists the same keys with its own text, and the fallback keeps an
-- untranslated phrase readable instead of blank.
---@type table<string, string>
local L = {
	["Atlas Forever"] = "Atlas Forever",
	["%s: %d instances"] = "%s: %d instances",
	["%s: instance index is not ready yet"] = "%s: instance index is not ready yet",
	["All continents"] = "All continents",
	["Continents"] = "Continents",
	["Instances"] = "Instances",
	["Type"] = "Type",
	["All types"] = "All types",
	["Dungeons"] = "Dungeons",
	["Raids"] = "Raids",
	["Dungeon"] = "Dungeon",
	["Raid"] = "Raid",
	["Floor"] = "Floor",
	["Contents"] = "Contents",
	["No floor map is available for this instance."] = "The client does not expose an interior map for this instance.",
	["The client exposes floor names here, but no map image."] = "The client exposes floor names here, but no map image.",
	["Creature positions are not available."] = "Creature positions are not available.",
	["Creature contents are not available from the installed client data."] = "Creature contents are not available from the installed client data.",
	["Install QuestieDB to see creature contents."] = "Install QuestieDB to see creature contents.",
	["Normal"] = "Normal",
	["Elite"] = "Elite",
	["Rare elite"] = "Rare elite",
	["Boss"] = "Boss",
	["Rare"] = "Rare",
	["Travel to entrance"] = "Travel to entrance",
	["Remember last instance"] = "Remember last instance",
	["Show contents"] = "Show contents",
	["Show travel button"] = "Show travel button",
	["Window scale"] = "Window scale",
}

setmetatable(L, {
	__index = function(_, key)
		return key
	end,
})

ns.L = L
