# Environment Snapshots

本目录保存每次实验环境的机器可读快照，避免周报、实验记录与实际工具状态脱节。

- `toolchain_2026-07-15.json`：首份环境快照；Python 和 NetworkX 可用，Yosys、ABC、OpenSTA、Z3 未检出。
- `toolchain_2026-07-20.json`：安装 OpenSTA 后的环境快照；Python 3.11.9、Yosys 0.9、OpenSTA 3.1.0、NetworkX 3.4.2 可用，ABC 和 z3 仍未检出。OpenSTA 通过 `FAECO_OPENSTA="wsl.exe -d Ubuntu -- /usr/local/bin/sta"` 检测。

重新检测：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check_toolchain.ps1 `
  -OutputPath experiments/environment/toolchain_YYYY-MM-DD.json
```
