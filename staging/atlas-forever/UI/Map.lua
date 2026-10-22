---@type string, AtlasNamespace
local _, ns = ...
local L = ns.L

local function label(parent, font, text, point, relative, relativePoint, x, y)
	local value = parent:CreateFontString(nil, "ARTWORK", font)
	value:SetPoint(point, relative, relativePoint, x, y)
	value:SetJustifyH("LEFT")
	value:SetText(text)
	return value
end

local QUESTIE_FIELDS = { "name", "minLevel", "maxLevel", "rank", "zoneID", "spawns" }
local QUESTIE_RANKS = {
	[0] = "Normal",
	[1] = "Elite",
	[2] = "Rare elite",
	[3] = "Boss",
	[4] = "Rare",
}

local function questieRows()
	local addon = QuestieDB
	local raw = type(addon) == "table" and addon.NpcDB
	local library = LibQuestieDB
	if
		type(library) == "table"
		and type(library.Npc) == "table"
		and type(library.Npc.GetAllIds) == "function"
		and type(library.Npc.GetAll) == "function"
	then
		local result = {}
		for _, id in ipairs(library.Npc.GetAllIds() or {}) do
			local values = library.Npc.GetAll(id, QUESTIE_FIELDS)
			if type(values) == "table" then
				local row = {}
				for index, key in ipairs(QUESTIE_FIELDS) do
					row[key] = values[index]
				end
				result[#result + 1] = row
			end
		end
		return result
	end
	local result = {}
	if type(raw) == "table" then
		for _, row in pairs(raw) do
			if type(row) == "table" then
				result[#result + 1] = row
			end
		end
	end
	return result
end

function ns.BuildMap(window)
	local panel = CreateFrame("Frame", nil, window)
	panel:SetPoint("TOPLEFT", window, "TOPLEFT", 410, -38)
	panel:SetPoint("BOTTOMRIGHT", window, "BOTTOMRIGHT", -16, 18)
	local title = label(panel, "GameFontNormalLarge", "", "TOPLEFT", panel, "TOPLEFT", 0, 0)
	local meta = label(panel, "GameFontHighlight", "", "TOPLEFT", title, "BOTTOMLEFT", 0, -8)
	local floorButtons = {}
	local mapMessage = label(
		panel,
		"GameFontHighlight",
		L["No floor map is available for this instance."],
		"TOPLEFT",
		meta,
		"BOTTOMLEFT",
		0,
		-24
	)
	mapMessage:SetWidth(300)
	mapMessage:SetWordWrap(true)
	local contentsTitle = label(panel, "GameFontNormal", L["Contents"], "TOPLEFT", panel, "TOPLEFT", 0, -110)
	local contentsScroll = CreateFrame("ScrollFrame", nil, panel, "UIPanelScrollFrameTemplate")
	contentsScroll:SetPoint("TOPLEFT", contentsTitle, "BOTTOMLEFT", 0, -8)
	contentsScroll:SetPoint("BOTTOMRIGHT", panel, "BOTTOMRIGHT", -20, 30)
	local contentsBody = CreateFrame("Frame", nil, contentsScroll)
	contentsScroll:SetScrollChild(contentsBody)
	local contents = contentsBody:CreateFontString(nil, "ARTWORK", "GameFontHighlightSmall")
	contents:SetPoint("TOPLEFT")
	contents:SetWidth(290)
	contents:SetWordWrap(true)
	contents:SetJustifyV("TOP")
	local footnote = label(panel, "GameFontDisableSmall", "", "BOTTOMLEFT", panel, "BOTTOMLEFT", 0, 26)
	local travel = CreateFrame("Button", nil, panel, "UIPanelButtonTemplate")
	travel:SetSize(150, 24)
	travel:SetPoint("BOTTOMLEFT", panel, "BOTTOMLEFT", 0, 0)
	travel:SetText(L["Travel to entrance"])
	local current
	local function render(entry, floorIndex)
		current = entry
		title:SetText(entry.name)
		meta:SetText((entry.mapType == "raid" and L["Raid"] or L["Dungeon"]) .. " · " .. tostring(entry.continent))
		for _, button in ipairs(floorButtons) do
			button:Hide()
		end
		if #entry.mapViews > 1 then
			mapMessage:Hide()
			for index, view in ipairs(entry.mapViews) do
				local selectedIndex = index
				local selectedEntry = entry
				local button = floorButtons[index]
				if not button then
					button = CreateFrame("Button", nil, panel, "UIPanelButtonTemplate")
					button:SetSize(94, 22)
					button:SetPoint("TOPLEFT", meta, "BOTTOMLEFT", (index - 1) * 98, -6)
					floorButtons[index] = button
				end
				local mapInfo = C_Map and C_Map.GetMapInfo and C_Map.GetMapInfo(view.uiMapID)
				button:SetText(mapInfo and mapInfo.name or (L["Floor"] .. " " .. index))
				button:SetEnabled(index ~= floorIndex)
				button:SetScript("OnClick", function()
					render(selectedEntry, selectedIndex)
				end)
				button:Show()
			end
			mapMessage:ClearAllPoints()
			mapMessage:SetPoint("TOPLEFT", floorButtons[#entry.mapViews], "BOTTOMLEFT", 0, -10)
			mapMessage:SetText(L["The client exposes floor names here, but no map image."])
			mapMessage:Show()
		else
			mapMessage:SetText(L["No floor map is available for this instance."])
			mapMessage:Show()
		end
		local names = {}
		if ns.db.settings.showContents then
			local areaIDs = {}
			for _, areaID in ipairs(entry.areaIDs or {}) do
				areaIDs[areaID] = true
			end
			for _, npc in ipairs(questieRows()) do
				if type(npc) == "table" and type(npc.name) == "string" then
					local present = areaIDs[tonumber(npc.zoneID)]
					if not present and type(npc.spawns) == "table" then
						for areaID in pairs(npc.spawns) do
							present = areaIDs[tonumber(areaID)]
							if present then
								break
							end
						end
					end
					if present then
						local minLevel, maxLevel = tonumber(npc.minLevel), tonumber(npc.maxLevel)
						local level = minLevel and maxLevel and (" " .. minLevel .. " - " .. maxLevel) or ""
						local rankValue = tonumber(npc.rank)
						local rank = rankValue and QUESTIE_RANKS[rankValue] and (" · " .. L[QUESTIE_RANKS[rankValue]])
							or rankValue and (" · rank " .. rankValue)
							or (type(npc.rank) == "string" and npc.rank ~= "" and (" · " .. npc.rank))
							or ""
						names[#names + 1] = npc.name .. level .. rank
					end
				end
			end
			table.sort(names)
		end
		contentsTitle:SetShown(ns.db.settings.showContents)
		contentsScroll:SetShown(ns.db.settings.showContents)
		if #names > 0 then
			contents:SetText(table.concat(names, "\n"))
			footnote:SetText(L["Creature positions are not available."])
		else
			contents:SetText(L["Install QuestieDB to see creature contents."])
			contentsTitle:SetShown(ns.db.settings.showContents)
			contentsScroll:SetShown(ns.db.settings.showContents)
			footnote:SetText("")
		end
		contentsBody:SetSize(290, math.max(contentsScroll:GetHeight(), contents:GetStringHeight() + 8))
		local entrance = entry.entrances and entry.entrances[1]
		travel:SetShown(ns.db.settings.travelButton and entrance ~= nil)
		travel:SetScript("OnClick", function()
			if current then
				ns.SafeCall("travel to entrance", ns.Navigate, current)
			end
		end)
	end
	function ns.ShowInstance(_, entry)
		render(entry, 1)
	end
end
