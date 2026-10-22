---@type string, AtlasNamespace
local _, ns = ...
local L = ns.L

function ns.BuildList(window, onSelect)
	local filter = { continent = nil }
	local continents = {}
	for _, entry in ipairs(ns.Instances) do
		continents[entry.continent] = true
	end
	local continentNames = { L["All continents"] }
	for name in pairs(continents) do
		continentNames[#continentNames + 1] = name
	end
	table.sort(continentNames, function(a, b)
		if a == L["All continents"] then
			return true
		end
		if b == L["All continents"] then
			return false
		end
		return a < b
	end)
	local side = CreateFrame("Frame", nil, window)
	side:SetPoint("TOPLEFT", 16, -38)
	side:SetSize(170, 410)
	local sideTitle = side:CreateFontString(nil, "ARTWORK", "GameFontNormal")
	sideTitle:SetPoint("TOPLEFT")
	sideTitle:SetText(L["Continents"])
	local list = CreateFrame("Frame", nil, window)
	list:SetPoint("TOPLEFT", side, "TOPRIGHT", 8, 0)
	list:SetSize(210, 410)
	local listTitle = list:CreateFontString(nil, "ARTWORK", "GameFontNormal")
	listTitle:SetPoint("TOPLEFT")
	listTitle:SetText(L["Instances"])
	local scroll = CreateFrame("ScrollFrame", nil, list, "UIPanelScrollFrameTemplate")
	scroll:SetPoint("TOPLEFT", 0, -24)
	scroll:SetPoint("BOTTOMRIGHT")
	local content = CreateFrame("Frame", nil, scroll)
	content:SetSize(188, 386)
	scroll:SetScrollChild(content)
	local continentButtons, rows = {}, {}
	local function DrawRows()
		for _, row in ipairs(rows) do
			row:Hide()
		end
		local visible = ns.Model.Filter(ns.Instances, filter)
		for rowIndex, entry in ipairs(visible) do
			local selectedEntry = entry
			local row = rows[rowIndex]
			if not row then
				row = CreateFrame("Button", nil, content, "UIPanelButtonTemplate")
				row:SetSize(180, 28)
				row:SetPoint("TOPLEFT", 0, -(rowIndex - 1) * 32)
				row.nameText = row:CreateFontString(nil, "ARTWORK", "GameFontHighlightSmall")
				row.nameText:SetPoint("LEFT", row, "LEFT", 8, 0)
				row.nameText:SetPoint("RIGHT", row, "RIGHT", -54, 0)
				row.nameText:SetJustifyH("LEFT")
				row.nameText:SetJustifyV("MIDDLE")
				row.nameText:SetWordWrap(true)
				row.metaText = row:CreateFontString(nil, "ARTWORK", "GameFontDisableSmall")
				row.metaText:SetPoint("RIGHT", row, "RIGHT", -7, 0)
				row.metaText:SetWidth(43)
				row.metaText:SetJustifyH("RIGHT")
				row.metaText:SetJustifyV("MIDDLE")
				rows[rowIndex] = row
			end
			local level = ns.Model.LevelRange(selectedEntry)
			local typeName = selectedEntry.mapType == "raid" and L["Raid"] or L["Dungeon"]
			row:SetText("")
			row.nameText:SetText(selectedEntry.name)
			row.metaText:SetText(typeName .. (level and ("\n" .. level) or ""))
			row:SetScript("OnClick", function()
				onSelect(selectedEntry)
			end)
			row:SetScript("OnEnter", function(self)
				GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
				GameTooltip:AddLine(selectedEntry.name)
				GameTooltip:AddLine(typeName, 1, 1, 1)
				if level then
					GameTooltip:AddLine(level, 0.8, 0.8, 0.8)
				end
				GameTooltip:Show()
			end)
			row:SetScript("OnLeave", function()
				GameTooltip:Hide()
			end)
			row:Show()
		end
		content:SetHeight(math.max(386, #visible * 32))
	end
	local function DrawContinents()
		for index, name in ipairs(continentNames) do
			local selectedContinent = name
			local button = continentButtons[index]
			if not button then
				button = CreateFrame("Button", nil, side, "UIPanelButtonTemplate")
				button:SetSize(160, 24)
				button:SetPoint("TOPLEFT", 0, -24 - (index - 1) * 28)
				continentButtons[index] = button
			end
			button:SetText(name)
			button:SetScript("OnClick", function()
				filter.continent = selectedContinent == L["All continents"] and nil or selectedContinent
				DrawRows()
			end)
		end
	end
	local typeTitle = side:CreateFontString(nil, "ARTWORK", "GameFontNormal")
	typeTitle:SetPoint("TOPLEFT", 0, -24 - #continentNames * 28 - 10)
	typeTitle:SetText(L["Type"])
	local typeOptions = {
		{ label = L["All types"], value = nil },
		{ label = L["Dungeons"], value = "party" },
		{ label = L["Raids"], value = "raid" },
	}
	for index, option in ipairs(typeOptions) do
		local selectedType = option.value
		local button = CreateFrame("Button", nil, side, "UIPanelButtonTemplate")
		button:SetSize(160, 24)
		button:SetPoint("TOPLEFT", 0, -34 - #continentNames * 28 - (index - 1) * 28)
		button:SetText(option.label)
		button:SetScript("OnClick", function()
			filter.mapType = selectedType
			DrawRows()
		end)
	end
	DrawContinents()
	continentButtons[1]:Click()
end
