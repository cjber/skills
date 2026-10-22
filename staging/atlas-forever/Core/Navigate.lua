---@type string, AtlasNamespace
local _, ns = ...

---@param entry AtlasInstance?
---@return boolean
---@return string?
function ns.Navigate(entry)
	local entrance = type(entry) == "table" and type(entry.entrances) == "table" and entry.entrances[1]
	if
		type(entrance) ~= "table"
		or type(entrance.mapID) ~= "number"
		or type(entrance.x) ~= "number"
		or type(entrance.y) ~= "number"
	then
		return false, "no-entrance"
	end
	if type(InCombatLockdown) == "function" and InCombatLockdown() then
		return false, "combat"
	end
	local addon = ShortestPathForever
	local api = type(addon) == "table" and addon.API
	if
		type(api) == "table"
		and api.version == 1
		and type(api.minor) == "number"
		and api.minor >= 1
		and type(api.Navigate) == "function"
	then
		local ok, result =
			pcall(api.Navigate, "AtlasForever", entrance.mapID, entrance.x, entrance.y, entry.name, "dungeon")
		if ok and result == true then
			return true
		end
	end
	if
		type(C_Map) == "table"
		and type(C_Map.CanSetUserWaypointOnMap) == "function"
		and type(C_Map.SetUserWaypoint) == "function"
		and type(C_SuperTrack) == "table"
		and type(C_SuperTrack.SetSuperTrackedUserWaypoint) == "function"
		and type(UiMapPoint) == "table"
		and type(UiMapPoint.CreateFromCoordinates) == "function"
		and C_Map.CanSetUserWaypointOnMap(entrance.mapID)
	then
		C_Map.SetUserWaypoint(UiMapPoint.CreateFromCoordinates(entrance.mapID, entrance.x, entrance.y))
		C_SuperTrack.SetSuperTrackedUserWaypoint(true)
		return true
	end
	return false, "unavailable"
end
