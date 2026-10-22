---@type string, AtlasNamespace
local _, ns = ...

-- The versioned addon-to-addon contract. nil means the answer is not known yet: before the instance index and the
-- saved variables load there is no list to report, and a caller asks again after PLAYER_LOGIN rather than reading the
-- silence as "this player has no instances". Version 1 is the first contract.
---@class AtlasPublicAPI
---@field version number
---@field minor number
local API = { version = 1, minor = 1 }

local function public(entry)
	if type(entry) ~= "table" then
		return nil
	end
	local result = {
		id = entry.id,
		name = entry.name,
		mapID = entry.mapID,
		mapType = entry.mapType,
		continent = entry.continent,
		minLevel = entry.minLevel,
		maxLevel = entry.maxLevel,
	}
	if type(entry.entrances) == "table" then
		result.entrances = {}
		for index, entrance in ipairs(entry.entrances) do
			result.entrances[index] = { mapID = entrance.mapID, x = entrance.x, y = entrance.y }
		end
	end
	return result
end

---@return boolean
function API.Ready()
	return ns.ready == true and ns.Instances ~= nil
end

---@param filter AtlasFilter?
---@return AtlasInstance[]?
function API.Instances(filter)
	if not API.Ready() then
		return nil
	end
	local entries, result = ns.Model.Filter(ns.Instances, filter), {}
	for index, entry in ipairs(entries) do
		result[index] = public(entry)
	end
	return result
end

---@param mapID number?
---@return AtlasInstance?
function API.Instance(mapID)
	if not API.Ready() then
		return nil
	end
	return public(ns.Model.Find(ns.Instances, mapID))
end

-- Opening is the window's job. Until the window exists this answers false rather than pretending it opened.
---@param mapID number?
---@return boolean opened
function API.Open(mapID)
	if not API.Ready() or type(ns.OpenInstance) ~= "function" then
		return false
	end
	if mapID ~= nil and not ns.Model.Find(ns.Instances, mapID) then
		return false
	end
	return ns.OpenInstance(mapID) == true
end

ns.API = API
AtlasForever = AtlasForever or {}
AtlasForever.API = API

return API
