---@type string, AtlasNamespace
local _, ns = ...

-- Instance index arithmetic with no WoW API and no frames: the window draws whatever these return, and the specs
-- exercise them without a client.
---@class AtlasInstance
---@field id number
---@field name string
---@field mapID number
---@field mapType string -- the client's map type: "party", "raid", "scenario", "micro" and so on
---@field continent string
---@field minLevel number?
---@field maxLevel number?
---@field entrances table?

---@class AtlasFilter
---@field continent string?
---@field mapType string?
---@field query string?
---@field minLevel number?
---@field maxLevel number?

---@class AtlasModel
local Model = {}

ns.Model = Model

---@param value string?
---@return string
local function trim(value)
	if type(value) ~= "string" then
		return ""
	end
	return (value:gsub("^%s*(.-)%s*$", "%1"))
end

-- A level range is shown only when the client reports it. One end alone is still honest: "38+" or "up to 45".
---@param entry AtlasInstance?
---@return string?
function Model.LevelRange(entry)
	if type(entry) ~= "table" then
		return nil
	end
	local low, high = entry.minLevel, entry.maxLevel
	if type(low) == "number" and type(high) == "number" then
		if low == high then
			return tostring(low)
		end
		return string.format("%d - %d", low, high)
	elseif type(low) == "number" then
		return string.format("%d+", low)
	elseif type(high) == "number" then
		return string.format("up to %d", high)
	end
	return nil
end

-- An entry with no level range is never claimed to be in range: it fails a level filter rather than passing it.
---@param entry AtlasInstance
---@param filter AtlasFilter?
---@return boolean
function Model.Matches(entry, filter)
	if type(entry) ~= "table" then
		return false
	end
	filter = filter or {}
	local query = trim(filter.query):lower()
	if query ~= "" and not tostring(entry.name or ""):lower():find(query, 1, true) then
		return false
	end
	if filter.continent and filter.continent ~= "" and entry.continent ~= filter.continent then
		return false
	end
	if filter.mapType and filter.mapType ~= "" and entry.mapType ~= filter.mapType then
		return false
	end
	local wantsLevel = type(filter.minLevel) == "number" or type(filter.maxLevel) == "number"
	if wantsLevel then
		local low = type(entry.minLevel) == "number" and entry.minLevel
			or type(entry.maxLevel) == "number" and entry.maxLevel
		local high = type(entry.maxLevel) == "number" and entry.maxLevel or low
		if type(low) ~= "number" then
			return false
		end
		local floor = type(filter.minLevel) == "number" and filter.minLevel or 0
		local ceiling = type(filter.maxLevel) == "number" and filter.maxLevel or 999
		if high < floor or low > ceiling then
			return false
		end
	end
	return true
end

-- Deterministic: by name, then by id, so two runs never order a tie differently.
---@param entries AtlasInstance[]?
---@param filter AtlasFilter?
---@return AtlasInstance[] matched
function Model.Filter(entries, filter)
	local matched = {}
	for _, entry in ipairs(entries or {}) do
		if Model.Matches(entry, filter) then
			matched[#matched + 1] = entry
		end
	end
	table.sort(matched, function(left, right)
		local a, b = tostring(left.name or ""):lower(), tostring(right.name or ""):lower()
		if a == b then
			return (left.id or 0) < (right.id or 0)
		end
		return a < b
	end)
	return matched
end

---@param entries AtlasInstance[]?
---@param mapID number?
---@return AtlasInstance?
function Model.Find(entries, mapID)
	if type(mapID) ~= "number" then
		return nil
	end
	for _, entry in ipairs(entries or {}) do
		if entry.mapID == mapID then
			return entry
		end
	end
	return nil
end

-- Recently opened instances, most recent first, each map once, capped so the saved table cannot grow without end.
---@param recent number[]?
---@param mapID number?
---@param limit number?
---@return number[] recent
function Model.Remember(recent, mapID, limit)
	local updated = {}
	if type(mapID) ~= "number" then
		return updated
	end
	local cap = type(limit) == "number" and limit or 10
	updated[1] = mapID
	for _, existing in ipairs(recent or {}) do
		if existing ~= mapID and #updated < cap then
			updated[#updated + 1] = existing
		end
	end
	return updated
end

return Model
