---@type string, AtlasNamespace
local _, ns = ...

-- The versioned addon-to-addon contract. nil means the answer is not known yet: before the instance index and the
-- saved variables load there is no list to report, and a caller asks again after PLAYER_LOGIN rather than reading the
-- silence as "this player has no instances". Version 1 is the first contract.
---@class AtlasPublicAPI
---@field version number
---@field minor number
local API = { version = 1, minor = 1 }

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
	return ns.Model.Filter(ns.Instances, filter)
end

---@param mapID number?
---@return AtlasInstance?
function API.Instance(mapID)
	if not API.Ready() then
		return nil
	end
	return ns.Model.Find(ns.Instances, mapID)
end

-- Opening is the window's job. Until the window exists this answers false rather than pretending it opened.
---@param mapID number?
---@return boolean opened
function API.Open(mapID)
	if not API.Ready() or type(ns.OpenInstance) ~= "function" then
		return false
	end
	return ns.OpenInstance(mapID) == true
end

ns.API = API
AtlasForever = AtlasForever or {}
AtlasForever.API = API

return API
