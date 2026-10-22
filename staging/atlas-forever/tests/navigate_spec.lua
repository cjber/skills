local here = debug.getinfo(1, "S").source:sub(2):match("^(.*)[/\\]") or "."
local Mock = dofile(here .. "/wow_mock.lua")
local harness = Mock.Harness({ files = { "Core/Navigate.lua" } })
local ns, env = harness.ns, harness.env
local entry = { name = "The Deadmines", entrances = { { mapID = 1436, x = 0.38, y = 0.77 } } }

local routed
env.ShortestPathForever =
	{ API = {
		version = 1,
		minor = 1,
		Navigate = function(...)
			routed = { ... }
			return true
		end,
	} }
assert(ns.Navigate(entry) == true, "Shortest Path accepts the entrance")
assert(
	routed[1] == "AtlasForever" and routed[2] == 1436 and routed[6] == "dungeon",
	"the route names its owner and stop kind"
)

env.ShortestPathForever.API.Navigate = function()
	return false
end
local point, waypoint, tracked
env.C_Map = {
	CanSetUserWaypointOnMap = function(mapID)
		assert(mapID == 1436)
		return true
	end,
	SetUserWaypoint = function(value)
		waypoint = value
	end,
}
env.UiMapPoint = {
	CreateFromCoordinates = function(mapID, x, y)
		point = { mapID, x, y }
		return point
	end,
}
env.C_SuperTrack = {
	SetSuperTrackedUserWaypoint = function(value)
		tracked = value
	end,
}
assert(ns.Navigate(entry) == true, "waypoint fallback succeeds after a route declines")
assert(waypoint == point and point[1] == 1436 and tracked == true, "the client waypoint is set and tracked")

env.InCombatLockdown = function()
	return true
end
assert(ns.Navigate(entry) == false, "travel declines in combat")
assert(select(2, ns.Navigate(entry)) == "combat", "combat decline is reported")

env.InCombatLockdown = function()
	return false
end
assert(ns.Navigate({ name = "Unknown", entrances = {} }) == false, "no position means no attempted travel")
assert(select(2, ns.Navigate({ name = "Unknown", entrances = {} })) == "no-entrance", "missing position is honest")
print("navigate: ok")
