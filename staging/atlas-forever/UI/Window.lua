---@type string, AtlasNamespace
local _, ns = ...

local window
local shownMapID

function ns.OpenInstance(mapID)
	if not ns.ready then
		return false
	end
	if not window then
		window = CreateFrame("Frame", "AtlasForeverWindow", UIParent, "UIPanelDialogTemplate")
		window:SetSize(760, 470)
		window:SetPoint("CENTER")
		window:SetMovable(true)
		window:EnableMouse(true)
		window:RegisterForDrag("LeftButton")
		window:SetScript("OnDragStart", window.StartMoving)
		window:SetScript("OnDragStop", window.StopMovingOrSizing)
		window:SetScale(ns.db.settings.windowScale or 1)
		table.insert(UISpecialFrames, "AtlasForeverWindow")
		ns.BuildList(window, function(entry)
			shownMapID = entry.mapID
			ns.ShowInstance(window, entry)
			if ns.db.settings.rememberLast then
				ns.db.lastInstance = entry.mapID
			end
		end)
		ns.BuildMap(window)
	end
	window:Show()
	local entry = ns.Model.Find(ns.Instances, mapID or (ns.db.settings.rememberLast and ns.db.lastInstance))
	entry = entry or ns.Instances[1]
	if entry then
		shownMapID = entry.mapID
		ns.ShowInstance(window, entry)
	end
	return true
end

function ns.Open()
	return ns.OpenInstance()
end

function ns.ApplySettings()
	if not window or not ns.db then
		return
	end
	window:SetScale(ns.db.settings.windowScale or 1)
	local entry = ns.Model.Find(ns.Instances, shownMapID)
	if entry then
		ns.ShowInstance(window, entry)
	end
end
