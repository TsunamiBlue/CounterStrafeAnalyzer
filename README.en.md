# CounterStrafeAnalyzer

[![Build Release](https://github.com/TsunamiBlue/CounterStrafeAnalyzer/actions/workflows/release.yml/badge.svg)](https://github.com/TsunamiBlue/CounterStrafeAnalyzer/actions/workflows/release.yml)
[![Latest Release](https://img.shields.io/github/v/release/TsunamiBlue/CounterStrafeAnalyzer?display_name=tag&sort=semver)](https://github.com/TsunamiBlue/CounterStrafeAnalyzer/releases)
[![Platform](https://img.shields.io/badge/platform-Windows-0078d4)](#requirements)
[![Python](https://img.shields.io/badge/python-3.8%2B-3776ab)](#requirements)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/license-CC%20BY--NC%204.0-lightgrey)](LICENSE)
[![Commercial Use](https://img.shields.io/badge/commercial%20use-not%20allowed-red)](LICENSE)

A local CS2 counter-strafing and shooting-input analysis tool.

> This project is based on the original Gitee repository [DDAsashio/CS2StopReflex](https://gitee.com/DDAsashio/CS2StopReflex), with further cleanup and feature extensions.

CS2 Counter-Strafing Evaluation Tool is a local input analysis tool built with Python 3 and PyQt5. It measures Counter-Strike 2 counter-strafing timing, directional consistency, and the relationship between movement correction and left-mouse shooting input.

The tool only analyzes local keyboard and mouse input events. It does not read game memory, read game state, or modify game files.

## Quick Links

- [Features](#features)
- [Counter-Strafe Logic](#counter-strafe-logic)
- [Shooting Groups](#shooting-groups)
- [Installation](#installation)
- [License](#license)
- [Disclaimer](#disclaimer)

## Features

- Counter-strafe timing analysis between movement-key release and opposite-key press.
- AD / WS trend charts with scatter plots, average lines, and boxplots.
- Directional analysis for AD, DA, WS, and SW transitions.
- Shot / Spray / No shot grouping based on local left-mouse input.
- Left-click timing analysis, with `40-90ms` treated as the preferred shooting timing range.
- Gray display for No shot entries.
- Optional same-direction detection for A->A, D->D, W->W, and S->S.
- Background recording mode with post-session report.
- Configurable display count, filter threshold, shot window, key mappings, and reaction baseline.
- GitHub Actions workflow for automatic Windows `.exe` release builds.

## Counter-Strafe Logic

A standard counter-strafe is usually represented as:

```text
release current movement key -> press opposite movement key
```

Examples:

```text
A -> D
D -> A
W -> S
S -> W
```

The measured delta is:

```text
Delta T = opposite_press_time - release_time
```

A value closer to 0ms indicates more synchronized counter-strafing input. Negative values usually mean the opposite key was triggered earlier; positive values usually mean it was triggered later.

## Shooting Groups

Records are classified by local left-mouse input:

- `Shot`: left mouse button was pressed within the shot window after the counter-strafe event.
- `Spray`: left mouse button was already held when the counter-strafe event happened.
- `No shot`: no left mouse input was detected within the shot window.

The default shot window is `250ms`. This is used only for intent classification and can be changed in the UI.

Left-click timing quality is displayed separately:

- `40-90ms`: preferred shooting timing.
- `<40ms`: early.
- `>90ms`: late.

## Color Rules

Timing colors encode both direction and severity:

- Near 0ms: green.
- Larger negative values: blue to purple.
- Larger positive values: yellow to red.
- `No shot`: gray.

Shot history rows also use an additional background highlight for left-click timing quality.

## Requirements

- Python 3.8+
- Windows 10/11 recommended

The target platform is Windows because the tool relies on low-level keyboard and mouse hooks and is designed around CS2 gameplay.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## License

This project is licensed under [Creative Commons Attribution-NonCommercial 4.0 International](LICENSE).

You may copy, share, and adapt this work for non-commercial purposes. Commercial use is not permitted without prior written permission.

## Disclaimer

This tool is for local input analysis and training feedback only. It does not read game state, read game memory, or modify game files. If you use any third-party input listener while playing on strict anti-cheat platforms such as Faceit or 5E, evaluate the risk yourself.
