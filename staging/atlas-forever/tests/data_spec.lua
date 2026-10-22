local here = debug.getinfo(1, "S").source:sub(2):match("^(.*)[/\\]") or "."
local Mock = dofile(here .. "/wow_mock.lua")
local harness = Mock.Harness({ files = { "Data/Instances.lua" } })
local entries = harness.ns.Instances
assert(type(entries) == "table" and #entries > 0, "generated rows load")
local seen, previous = {}, 0
for _, entry in ipairs(entries) do
	assert(type(entry.id) == "number" and entry.id % 1 == 0, "instance id is an integer")
	assert(type(entry.mapID) == "number" and entry.mapID % 1 == 0, "mapID is an integer")
	assert(type(entry.name) == "string" and entry.name ~= "", "instance has a name")
	assert(entry.id > previous, "rows are deterministically sorted by ID")
	previous = entry.id
	assert(not seen[entry.mapID], "mapIDs are unique")
	seen[entry.mapID] = true
	assert(
		type(entry.wdtFileDataID) == "number" and entry.wdtFileDataID > 0,
		"the client exposes the map's WDT file ID"
	)
	for _, view in ipairs(entry.mapViews) do
		assert(type(view.uiMapID) == "number", "a floor view has a UI map ID")
		assert(type(view.mapArtIDs) == "table" and #view.mapArtIDs > 0, "a client-exposed floor has map art")
	end
	for _, entrance in ipairs(entry.entrances or {}) do
		assert(type(entrance.mapID) == "number", "entrance map is an integer")
		assert(entrance.x >= 0 and entrance.x <= 1 and entrance.y >= 0 and entrance.y <= 1, "entrance is on its map")
	end
end
print("data: ok (" .. #entries .. " rows)")
