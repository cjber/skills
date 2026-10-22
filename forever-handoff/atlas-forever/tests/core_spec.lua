local here = debug.getinfo(1, "S").source:sub(2):match("^(.*)[/\\]") or "."
local Mock = dofile(here .. "/wow_mock.lua")
local harness = Mock.Harness()
local ns = harness.ns

assert(not ns.ready, "nothing is ready before the saved variables load")
assert(harness.env.SlashCmdList["ATLASFOREVER"] ~= nil, "the slash command is registered at load")

local API = harness.env.AtlasForever and harness.env.AtlasForever.API
assert(API, "the public API is installed")
assert(API.version == 1 and API.minor == 1, "the contract is versioned")
assert(API.Ready() == false, "not ready before the saved variables load")
assert(API.Instances() == nil, "an unknown index is nil, not an empty list")
assert(API.Instance(389) == nil, "an unknown instance is nil")
assert(API.Open(389) == false, "nothing opens before the window exists")

harness:Fire("ADDON_LOADED", "AtlasForever")
assert(ns.ready, "the addon's own ADDON_LOADED loads the saved variables")
assert(type(harness.env.AtlasForeverDB) == "table", "the saved variables exist after loading")
assert(type(ns.db.settings) == "table", "settings start as a table")
assert(ns.db.settings.travelButton == true, "the travel button is on by default")
assert(ns.db.settings.showContents == true, "contents are shown by default")
assert(ns.db.settings.rememberLast == true, "the last instance is remembered by default")
assert(API.Ready() == false, "saved state alone is not enough: the index must be loaded too")

-- The index arrives from generated data, not from the client at runtime.
ns.Instances = {
	{
		id = 1,
		name = "Ragefire Chasm",
		mapID = 389,
		mapType = "party",
		continent = "Kalimdor",
		minLevel = 13,
		maxLevel = 18,
	},
	{ id = 2, name = "The Deadmines", mapID = 291, mapType = "party", continent = "Eastern Kingdoms" },
}
assert(API.Ready() == true, "ready once saved state and the index are both loaded")
assert(#API.Instances() == 2, "the whole index is listed with no filter")
assert(#API.Instances({ continent = "Kalimdor" }) == 1, "the API filters like the window does")
assert(API.Instance(291).name == "The Deadmines", "an instance is read by its map")

local opened = nil
ns.OpenInstance = function(mapID)
	opened = mapID
	return true
end
assert(API.Open(291) == true and opened == 291, "opening goes through the window once it exists")
ns.OpenInstance = nil

local ran = 0
ns.OnReady(function()
	ran = ran + 1
end)
assert(ran == 1, "a callback asked for after loading runs at once")
harness:Fire("PLAYER_LOGIN")
harness:Fire("PLAYER_LOGIN")
assert(ran == 1, "a ready callback never runs a second time")

for key, value in pairs(ns.db) do
	assert(
		type(value) ~= "function" and type(value) ~= "userdata",
		"nothing unsaveable is stored under " .. tostring(key)
	)
end

print("core: ok")
