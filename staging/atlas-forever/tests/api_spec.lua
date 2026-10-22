local here = debug.getinfo(1, "S").source:sub(2):match("^(.*)[/\\]") or "."
local Mock = dofile(here .. "/wow_mock.lua")
local harness = Mock.Harness({
	files = {
		"Locales/enUS.lua",
		"Core/SafeCall.lua",
		"Data/Instances.lua",
		"Core/Model.lua",
		"Core/Core.lua",
		"Core/API.lua",
	},
})
local ns, env = harness.ns, harness.env
local API = env.AtlasForever.API

assert(API.version == 1 and API.minor == 1, "the public API version is declared")
assert(API.Ready() == false and API.Instances() == nil, "data remains unknown before saved variables load")
harness:Fire("ADDON_LOADED", "AtlasForever")
assert(API.Ready() == true, "saved variables plus bundled data make the API ready")
local instances = API.Instances()
assert(type(instances) == "table" and #instances > 0, "the API returns the complete index")
local entry = API.Instance(33)
assert(entry and entry.name == "Shadowfang Keep", "lookup uses the instance map ID")
assert(entry.areaIDs == nil and entry.wdtFileDataID == nil, "internal data is private")
entry.name = "changed"
assert(API.Instance(33).name == "Shadowfang Keep", "lookups return copies")
assert(#API.Instances({ mapType = "raid" }) > 0, "the public filter works")
assert(#API.Instances({ mapType = "invalid" }) == 0, "unsupported filters match no entries")
local opened
ns.OpenInstance = function(mapID)
	opened = mapID
	return true
end
assert(API.Open(999999) == false and opened == nil, "opening an unknown instance does not open a different one")
assert(API.Open(33) and opened == 33, "Open delegates to the window")
print("api: ok")
