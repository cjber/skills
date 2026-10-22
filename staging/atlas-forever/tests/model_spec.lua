local here = debug.getinfo(1, "S").source:sub(2):match("^(.*)[/\\]") or "."
local Mock = dofile(here .. "/wow_mock.lua")
local harness = Mock.Harness({ files = { "Locales/enUS.lua", "Core/SafeCall.lua", "Core/Model.lua" } })
local Model = harness.ns.Model

assert(Model, "the model loads on its own, without a client")

local ragefire = {
	id = 1,
	name = "Ragefire Chasm",
	mapID = 389,
	mapType = "party",
	continent = "Kalimdor",
	minLevel = 13,
	maxLevel = 18,
}
local deadmines = {
	id = 2,
	name = "The Deadmines",
	mapID = 291,
	mapType = "party",
	continent = "Eastern Kingdoms",
	minLevel = 17,
	maxLevel = 26,
}
local molten = {
	id = 3,
	name = "Molten Core",
	mapID = 232,
	mapType = "raid",
	continent = "Eastern Kingdoms",
	minLevel = 60,
	maxLevel = 60,
}
local unknown = { id = 4, name = "Unnamed Vault", mapID = 999, mapType = "party", continent = "Kalimdor" }
local all = { molten, deadmines, ragefire, unknown }

assert(Model.LevelRange(ragefire) == "13 - 18", "a range reads low to high")
assert(Model.LevelRange(molten) == "60", "a single level is not a range")
assert(Model.LevelRange({ minLevel = 40 }) == "40+", "one known end is shown honestly")
assert(Model.LevelRange({ maxLevel = 20 }) == "up to 20", "a known ceiling is shown honestly")
assert(Model.LevelRange(unknown) == nil, "an unknown range is absent, never invented")
assert(Model.LevelRange(nil) == nil, "no entry has no range")

assert(Model.Matches(ragefire, {}), "an empty filter matches everything")
assert(Model.Matches(ragefire, nil), "no filter matches everything")
assert(Model.Matches(ragefire, { query = "rage" }), "search matches inside a name")
assert(Model.Matches(ragefire, { query = "  RAGE  " }), "search trims and ignores case")
assert(not Model.Matches(ragefire, { query = "deadmines" }), "search rejects a name it does not hold")
assert(Model.Matches(ragefire, { continent = "Kalimdor" }), "the continent filter matches the entry's continent")
assert(
	not Model.Matches(ragefire, { continent = "Eastern Kingdoms" }),
	"the continent filter rejects another continent"
)
assert(Model.Matches(molten, { mapType = "raid" }), "the type filter matches a raid")
assert(not Model.Matches(molten, { mapType = "party" }), "the type filter rejects a dungeon")
assert(Model.Matches(ragefire, { minLevel = 15, maxLevel = 20 }), "overlapping levels are in range")
assert(not Model.Matches(ragefire, { minLevel = 40 }), "a filter above the range rejects it")
assert(not Model.Matches(ragefire, { maxLevel = 12 }), "a filter below the range rejects it")
assert(not Model.Matches(unknown, { minLevel = 1 }), "an entry with no levels is never claimed to be in range")
assert(Model.Matches(unknown, { query = "vault" }), "an entry with no levels still matches a name search")

local party = Model.Filter(all, { mapType = "party" })
assert(#party == 3, "the type filter keeps three dungeons")
assert(party[1].name == "Ragefire Chasm" and party[2].name == "The Deadmines", "results are ordered by name")
assert(party[3].name == "Unnamed Vault", "ordering is stable and complete")

local ties = Model.Filter({ { id = 9, name = "Same", mapID = 2 }, { id = 7, name = "same", mapID = 1 } }, {})
assert(ties[1].id == 7, "a name tie is broken by id, so two runs never disagree")
assert(#Model.Filter(nil, {}) == 0, "a missing index filters as empty")

assert(Model.Find(all, 389).name == ragefire.name, "an instance is found by its map")
assert(Model.Find(all, 389) ~= ragefire, "find returns a copy for callers")
assert(Model.Find(all, 1) == nil, "the id is not the map: only mapID resolves")
assert(Model.Find(all, nil) == nil, "no map finds nothing")
assert(Model.Find(nil, 389) == nil, "a missing index finds nothing")

assert(Model.Remember(nil, 389, 3)[1] == 389, "a new visit starts the list")
local recent = Model.Remember({ 291, 389, 232 }, 389, 3)
assert(recent[1] == 389 and #recent == 3 and recent[3] == 232, "a revisit moves to the front without duplicating")
local capped = Model.Remember({ 1, 2, 3, 4 }, 5, 3)
assert(#capped == 3 and capped[1] == 5, "the list is capped at the limit")
assert(#Model.Remember({ 1, 2 }, nil) == 0, "no visit changes nothing")

print("model: ok")
