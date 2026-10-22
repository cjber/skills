---@type string, AtlasNamespace
local addonName, ns = ...

local L = ns.L

ns.ready = false
ns.SCHEMA = 1

---@return AtlasSavedVariables
local function defaults()
	return {
		schema = ns.SCHEMA,
		lastInstance = 0,
		settings = {
			windowScale = 1,
			rememberLast = true,
			showContents = true,
			travelButton = true,
		},
	}
end

-- The saved state is one flat table per account. Frames, functions and userdata never go in it.
local function load()
	AtlasForeverDB = AtlasForeverDB or {}
	local db = AtlasForeverDB
	local missing = defaults()
	if type(db.schema) ~= "number" then
		db.schema = ns.SCHEMA
	end
	if type(db.lastInstance) ~= "number" then
		db.lastInstance = missing.lastInstance
	end
	if type(db.settings) ~= "table" then
		db.settings = missing.settings
	end
	for key, value in pairs(missing.settings) do
		if db.settings[key] == nil then
			db.settings[key] = value
		end
	end
	if type(db.settings.windowScale) ~= "number" then
		db.settings.windowScale = missing.settings.windowScale
	end
	db.settings.windowScale = math.max(0.8, math.min(1.2, db.settings.windowScale))
	for _, key in ipairs({ "rememberLast", "showContents", "travelButton" }) do
		if type(db.settings[key]) ~= "boolean" then
			db.settings[key] = missing.settings[key]
		end
	end
	ns.db = db
	ns.ready = true
end

---@type fun()[]
local readyCallbacks = {}

-- Anything that needs saved state asks here rather than testing ns.ready at load time, so a file loaded before the
-- saved variables still runs exactly once.
---@param callback fun()
function ns.OnReady(callback)
	if type(callback) ~= "function" then
		return
	end
	if ns.ready then
		callback()
		return
	end
	readyCallbacks[#readyCallbacks + 1] = callback
end

local function announce()
	for _, callback in ipairs(readyCallbacks) do
		ns.SafeCall("ready callback", callback)
	end
	readyCallbacks = {}
end

local function status()
	if not ns.ready then
		print(string.format(L["%s: instance index is not ready yet"], L["Atlas Forever"]))
		return
	end
	if ns.Open then
		ns.Open()
	else
		print(string.format(L["%s: %d instances"], L["Atlas Forever"], #ns.Instances))
	end
end

SLASH_ATLASFOREVER1 = "/atlas"
SLASH_ATLASFOREVER2 = "/atlasforever"
SlashCmdList["ATLASFOREVER"] = function(message)
	ns.SafeCall("slash command", status, message)
end

function AtlasForever_OnAddonCompartmentClick()
	if ns.Open then
		ns.Open()
	end
end

local events = CreateFrame("Frame")
events:RegisterEvent("ADDON_LOADED")
events:RegisterEvent("PLAYER_LOGIN")
events:SetScript("OnEvent", function(_, event, arg1)
	if event == "ADDON_LOADED" and arg1 == addonName then
		ns.SafeCall("load", load)
	elseif event == "PLAYER_LOGIN" then
		ns.SafeCall("ready", announce)
	end
end)
