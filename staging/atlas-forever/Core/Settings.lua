---@type string, AtlasNamespace
local _, ns = ...
local L = ns.L

local function changed(setting)
	setting:SetValueChangedCallback(function()
		if ns.ApplySettings then
			ns.ApplySettings()
		end
	end)
end

local function register()
	if type(Settings) ~= "table" or type(Settings.RegisterVerticalLayoutCategory) ~= "function" then
		return
	end
	local category = Settings.RegisterVerticalLayoutCategory(L["Atlas Forever"])
	local function checkbox(key, label)
		local setting = Settings.RegisterAddOnSetting(
			category,
			"AtlasForever_" .. key,
			key,
			ns.db.settings,
			Settings.VarType.Boolean,
			L[label],
			ns.db.settings[key]
		)
		changed(setting)
		Settings.RegisterInitializer(category, Settings.CreateCheckboxInitializer(setting))
	end
	checkbox("rememberLast", "Remember last instance")
	checkbox("showContents", "Show contents")
	checkbox("travelButton", "Show travel button")
	local scale = Settings.RegisterAddOnSetting(
		category,
		"AtlasForever_windowScale",
		"windowScale",
		ns.db.settings,
		Settings.VarType.Number,
		L["Window scale"],
		ns.db.settings.windowScale
	)
	local options = Settings.CreateSliderOptions(0.8, 1.2, 0.05)
	changed(scale)
	Settings.RegisterInitializer(category, Settings.CreateSliderInitializer(scale, options))
	Settings.RegisterAddOnCategory(category)
end

ns.OnReady(register)
