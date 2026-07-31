import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_toolchain.ps1"


def _run_toolchain_script(env=None):
    """运行 check_toolchain.ps1 并容忍 PowerShell 输出中的非 UTF-8 字节。

    Windows PowerShell 偶发输出 cp1251 / cp936 等非 UTF-8 字节（例如 stderr
    中的 WSL path translation warning 含 0xD1），用 ``text=True, encoding='utf-8'``
    会在解码阶段抛出 ``UnicodeDecodeError``，使 ``result.stdout`` 变 None。
    这里改用 bytes 模式读，再用 ``errors='replace'`` 容错解码，保证测试稳定。
    JSON 主体本身是 ASCII，decode 结果可被 ``json.loads`` 正常解析。
    """
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(SCRIPT),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        env=env,
    )
    stdout_text = (
        result.stdout.decode("utf-8", errors="replace") if result.stdout else ""
    )
    stderr_text = (
        result.stderr.decode("utf-8", errors="replace") if result.stderr else ""
    )
    return result.returncode, stdout_text, stderr_text


class ToolchainScriptTest(unittest.TestCase):
    def test_reports_a_machine_readable_snapshot_for_all_required_tools(self):
        returncode, stdout_text, stderr_text = _run_toolchain_script()
        self.assertEqual(returncode, 0, stderr_text)
        snapshot = json.loads(stdout_text)
        self.assertIn("checked_at_utc", snapshot)
        tools = {entry["id"]: entry for entry in snapshot["tools"]}
        self.assertEqual(
            set(tools),
            {"python", "yosys", "abc", "opensta", "z3", "networkx"},
        )
        self.assertTrue(tools["python"]["available"])
        self.assertIn("path", tools["python"])
        self.assertIn("version", tools["python"])
        self.assertIsInstance(tools["python"]["version"], str)
        self.assertGreater(len(tools["python"]["version"]), 0)
        self.assertTrue(all("version" in entry for entry in tools.values()))

    def test_uses_explicit_faeco_abc_path_when_provided(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fake_abc = Path(temp_dir) / "fake_abc.cmd"
            fake_abc.write_text("@echo ABC fake 1.0\r\n", encoding="utf-8")
            env = os.environ.copy()
            env["FAECO_ABC"] = str(fake_abc)

            returncode, stdout_text, stderr_text = _run_toolchain_script(env=env)
            self.assertEqual(returncode, 0, stderr_text)
            snapshot = json.loads(stdout_text)
            abc = {entry["id"]: entry for entry in snapshot["tools"]}["abc"]
            self.assertTrue(abc["available"])
            self.assertEqual(
                os.path.basename(abc["command"]),
                os.path.basename(str(fake_abc)),
                msg=(
                    "PowerShell ConvertTo-Json 在 Windows 用户名为非 ASCII "
                    "（如中文）时会 mojibake 父目录，仅比较 basename。"
                ),
            )
            self.assertEqual(
                os.path.basename(abc["path"]),
                os.path.basename(str(fake_abc)),
                msg=(
                    "PowerShell ConvertTo-Json 在 Windows 用户名为非 ASCII "
                    "（如中文）时会 mojibake 父目录，仅比较 basename。"
                ),
            )
            self.assertEqual(abc["version"], "ABC fake 1.0")

    def test_falls_back_to_yosys_abc_when_no_explicit_abc_path_is_provided(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            fake_yosys_abc = temp_path / "yosys-abc.cmd"
            fake_yosys_abc.write_text("@echo UC Berkeley, ABC fake yosys package\r\n", encoding="utf-8")
            env = os.environ.copy()
            env.pop("FAECO_ABC", None)
            env["PATH"] = f"{temp_path}{os.pathsep}{env.get('PATH', '')}"

            returncode, stdout_text, stderr_text = _run_toolchain_script(env=env)
            self.assertEqual(returncode, 0, stderr_text)
            snapshot = json.loads(stdout_text)
            abc = {entry["id"]: entry for entry in snapshot["tools"]}["abc"]
            self.assertTrue(abc["available"])
            self.assertEqual(abc["command"], "yosys-abc")
            self.assertEqual(
                os.path.basename(abc["path"]),
                os.path.basename(str(fake_yosys_abc)),
                msg=(
                    "PowerShell ConvertTo-Json 在 Windows 用户名为非 ASCII "
                    "（如中文）时会 mojibake 父目录，仅比较 basename。"
                ),
            )
            self.assertEqual(abc["version"], "UC Berkeley, ABC fake yosys package")

    def test_opensta_version_ignores_wsl_path_translation_warnings(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fake_sta = Path(temp_dir) / "fake_sta.cmd"
            fake_sta.write_text(
                "@echo wsl: Failed to translate 'E:\\APP\\cursor\\resources\\app\\bin' 1>&2\r\n"
                "@echo 3.1.0\r\n",
                encoding="utf-8",
            )
            env = os.environ.copy()
            env["FAECO_OPENSTA"] = str(fake_sta)

            returncode, stdout_text, stderr_text = _run_toolchain_script(env=env)
            self.assertEqual(returncode, 0, stderr_text)
            snapshot = json.loads(stdout_text)
            opensta = {entry["id"]: entry for entry in snapshot["tools"]}["opensta"]
            self.assertTrue(opensta["available"])
            self.assertEqual(opensta["version"], "3.1.0")

    def test_opensta_version_prefers_version_line_after_nonstandard_wsl_warning(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fake_sta = Path(temp_dir) / "fake_sta.cmd"
            fake_sta.write_text(
                "@echo wsl: corrupted path translation warning 1>&2\r\n"
                "@echo OpenSTA 3.1.0\r\n",
                encoding="utf-8",
            )
            env = os.environ.copy()
            env["FAECO_OPENSTA"] = str(fake_sta)

            returncode, stdout_text, stderr_text = _run_toolchain_script(env=env)
            self.assertEqual(returncode, 0, stderr_text)
            snapshot = json.loads(stdout_text)
            opensta = {entry["id"]: entry for entry in snapshot["tools"]}["opensta"]
            self.assertEqual(opensta["version"], "3.1.0")

    def test_explicit_opensta_command_preserves_wsl_distro_argument(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fake_wsl = Path(temp_dir) / "fake_wsl.cmd"
            fake_wsl.write_text(
                "@if \"%1\"==\"-d\" (\r\n"
                "  @echo wsl: Failed to translate 'E:\\APP\\cursor\\resources\\app\\bin' 1>&2\r\n"
                "  @echo 3.1.0\r\n"
                ") else (\r\n"
                "  @echo /bin/bash: line 1: %1: command not found\r\n"
                ")\r\n",
                encoding="utf-8",
            )
            env = os.environ.copy()
            env["FAECO_OPENSTA"] = f"{fake_wsl} -d Ubuntu -- /usr/local/bin/sta"

            returncode, stdout_text, stderr_text = _run_toolchain_script(env=env)
            self.assertEqual(returncode, 0, stderr_text)
            snapshot = json.loads(stdout_text)
            opensta = {entry["id"]: entry for entry in snapshot["tools"]}["opensta"]
            self.assertEqual(opensta["version"], "3.1.0")


if __name__ == "__main__":
    unittest.main()
