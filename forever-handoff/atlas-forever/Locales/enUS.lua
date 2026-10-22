---@type string, AtlasNamespace
local _, ns = ...

-- English phrases are the keys. A translation lists the same keys with its own text, and the fallback keeps an
-- untranslated phrase readable instead of blank.
---@type table<string, string>
local L = {
	["Atlas Forever"] = "Atlas Forever",
	["%s: %d bookmarks"] = "%s: %d bookmarks",
	["%s: bookmarks are not loaded yet"] = "%s: bookmarks are not loaded yet",
}

setmetatable(L, {
	__index = function(_, key)
		return key
	end,
})

ns.L = L
