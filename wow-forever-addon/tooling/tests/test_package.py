import shutil
import tempfile
import unittest
from pathlib import Path

from forever_tools import package

POLICY = package.Policy(addons=("Addon", "Lib"))


class PackageTest(unittest.TestCase):
    def make(self, files):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        for name, text in files.items():
            (root / name).parent.mkdir(parents=True, exist_ok=True)
            (root / name).write_text(text)
        return root

    def good(self):
        return {
            "Addon/Addon.toc": (
                "## Title: A\n## IconTexture: Interface\\AddOns\\Addon\\media\\Icon\nCore.lua\nUI\\ui.xml\n"
            ),
            "Addon/Core.lua": (
                'local DOT = "Interface\\\\AddOns\\\\Addon\\\\media\\\\Dot"\n'
                'local other = "Interface\\\\AddOns\\\\X\\\\y"\n'
            ),
            "Addon/UI/ui.xml": (
                '<Ui><Script file="ui.lua"/><Texture file="Interface\\AddOns\\Addon\\media\\Shade"/></Ui>'
            ),
            "Addon/UI/ui.lua": "",
            "Addon/media/Icon.tga": "",
            "Addon/media/dot.tga": "",
            "Addon/media/Shade.blp": "",
            "Addon/LICENSE": "MIT",
            "Lib/Lib.toc": "## IconTexture: Interface\\AddOns\\Addon\\media\\Icon\nLib.lua\n",
            "Lib/Lib.lua": "",
        }

    def test_a_complete_package_passes(self):
        self.assertEqual(package.check(self.make(self.good()), POLICY), [])

    def test_each_problem_is_reported_once(self):
        files = self.good()
        del files["Addon/UI/ui.lua"], files["Addon/media/Shade.blp"], files["Addon/LICENSE"], files["Lib/Lib.toc"]
        files["Addon/tests/x_spec.lua"] = ""
        files["Addon/tools/gen.py"] = ""
        problems = package.check(self.make(files), POLICY)
        self.assertEqual(len(problems), 6, problems)
        joined = "\n".join(problems)
        for expected in (
            "Addon/UI/ui.lua: missing (loaded by Addon/UI/ui.xml)",
            "Addon/UI/ui.xml: names Interface\\AddOns\\Addon\\media\\Shade",
            "Addon/tests: shipped",
            "Addon/tools: shipped",
            "Addon/LICENSE: missing",
            "Lib/Lib.toc: missing",
        ):
            self.assertIn(expected, joined)

    def test_a_missing_addon_folder_and_a_lua_path_are_named(self):
        files = self.good()
        del files["Addon/media/dot.tga"]
        root = self.make({k: v for k, v in files.items() if not k.startswith("Lib/")})
        problems = package.check(root, POLICY)
        self.assertEqual(len(problems), 2, problems)
        self.assertIn("Addon/Core.lua:1: names Interface\\AddOns\\Addon\\media\\Dot", problems[0] + problems[1])
        self.assertIn("Lib: not in", problems[0] + problems[1])

    def test_the_client_rules_for_case_prefixes_absolute_includes_and_flavours(self):
        files = self.good()
        files["Addon/Addon.toc"] = files["Addon/Addon.toc"].replace("Core.lua", "core.lua")
        files["Addon/Core.lua"] += 'local P = "Interface\\\\AddOns\\\\Addon\\\\media\\\\class_" .. class\n'
        files["Addon/UI/ui.xml"] = '<Ui><Script file="Interface\\AddOns\\Addon\\UI\\ui.lua"/></Ui>'
        files["Addon/Addon_Vanilla.toc"] = "Gone.lua\n"
        files["Addon/Tests/x.lua"] = ""
        problems = package.check(self.make(files), POLICY)
        self.assertEqual(len(problems), 2, problems)
        self.assertIn("Addon/Tests: shipped", problems[0])
        self.assertIn("Addon/Gone.lua: missing (loaded by Addon/Addon_Vanilla.toc)", problems[1])

    def test_missing_support_is_a_problem_not_a_crash(self):
        root = self.make({})
        release = self.make({"Addon/Addon.toc": ""})
        policy = package.Policy(addons=("Addon",), specs=("tests/a_spec.lua",))
        self.assertIn("tests: not in the checkout", package.run_specs(root, release, policy)[0])

    @unittest.skipUnless(shutil.which("luajit"), "needs luajit")
    def test_specs_run_on_the_package_with_the_support_laid_over(self):
        root = self.make({"tests/a_spec.lua": 'assert(loadfile("Core.lua"))()\n', "Core.lua": ""})
        release = self.make({"Addon/Core.lua": "", "Addon/Addon.toc": "Core.lua\n"})
        policy = package.Policy(addons=("Addon",), specs=("tests/a_spec.lua",))
        self.assertEqual(package.run_specs(root, release, policy), [])
        (release / "Addon/Core.lua").unlink()
        problems = package.run_specs(root, release, policy)
        self.assertEqual(len(problems), 1)
        self.assertIn("fails on the packaged files", problems[0])

    def test_shipped_support_is_refused(self):
        root = self.make({"tests/a_spec.lua": ""})
        release = self.make({"Addon/tests/a_spec.lua": ""})
        policy = package.Policy(addons=("Addon",), specs=("tests/a_spec.lua",))
        self.assertIn("shipped in the package", package.run_specs(root, release, policy)[0])


if __name__ == "__main__":
    unittest.main()
