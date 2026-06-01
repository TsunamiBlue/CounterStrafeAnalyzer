# CS2 Counter-Strafing Evaluation Tool

## Overview

This is a high-precision Counter-Strike 2 counter-strafing evaluation tool built with Python 3 and PyQt5. It captures raw keyboard input events, calculates the time delta between releasing one movement key and pressing the opposite key, and visualizes the player's consistency.

The tool is designed for advanced players who want to quantify counter-strafing timing and improve movement muscle memory.

## Features

- Keyboard hook based input capture
- AD and WS axis timing analysis
- Real-time feedback and history display
- Background recording mode with post-session analysis
- Matplotlib charts for trend and distribution visualization
- Configurable reaction baseline, filter threshold, and key mappings

## Requirements

- Python 3.8+
- Windows 10/11 recommended

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the application:

```bash
python main.py
```

## Notes

This tool only analyzes local keyboard input. It does not modify game files or read game memory. When using it with strict anti-cheat platforms, evaluate the risk of running any third-party input listener in the background.
