<h1 align="center">CounterStrafeAnalyzer</h1>

<p align="center">
  <a href="https://github.com/TsunamiBlue/CounterStrafeAnalyzer/actions/workflows/release.yml"><img alt="Build Release" src="https://github.com/TsunamiBlue/CounterStrafeAnalyzer/actions/workflows/release.yml/badge.svg"></a>
  <a href="https://github.com/TsunamiBlue/CounterStrafeAnalyzer/releases"><img alt="Latest Release" src="https://img.shields.io/github/v/release/TsunamiBlue/CounterStrafeAnalyzer?display_name=tag&sort=semver"></a>
  <a href="#环境要求"><img alt="Platform" src="https://img.shields.io/badge/platform-Windows-0078d4"></a>
  <a href="#环境要求"><img alt="Python" src="https://img.shields.io/badge/python-3.8%2B-3776ab"></a>
  <a href="LICENSE"><img alt="License: CC BY-NC 4.0" src="https://img.shields.io/badge/license-CC%20BY--NC%204.0-lightgrey"></a>
  <a href="LICENSE"><img alt="Commercial Use" src="https://img.shields.io/badge/commercial%20use-not%20allowed-red"></a>
  <a href="README.md"><img alt="中文" src="https://img.shields.io/badge/lang-中文-blue"></a>
  <a href="README.en.md"><img alt="English" src="https://img.shields.io/badge/lang-English-blue"></a>
</p>

<p align="center">面向 CS2 的本地急停与射击输入分析工具。</p>

CS2 Counter-Strafing Evaluation Tool 是一个基于 Python 3 和 PyQt5 的本地急停分析工具，用于量化 Counter-Strike 2 中的反向急停时机、方向稳定性，以及急停与鼠标左键射击输入之间的关系。

本工具只分析本机键盘和鼠标输入事件，不读取游戏内存、不读取游戏状态、不修改任何游戏文件。

## 快速入口

- [核心功能](#核心功能)
- [急停判定逻辑](#急停判定逻辑)
- [射击分组](#射击分组)
- [安装与运行](#安装与运行)
- [许可证](#许可证)
- [致谢](#致谢)
- [免责声明](#免责声明)

## 核心功能

- 急停时间差分析：记录松开移动键到按下相反方向键之间的时间差。
- AD / WS 趋势图：使用 Matplotlib 显示急停散点、平均线和箱线图。
- 方向分析视图：分别统计 AD、DA、WS、SW 四种反向急停的样本数、平均误差、平均偏向、稳定性、评级和最佳/最差表现。
- Shot / Spray / No shot 分组：通过本地鼠标左键输入判断急停是否关联射击。
- 左键时机分析：显示左键相对急停事件的延迟，`40-90ms` 视为合理射击时机。
- No shot 灰色标记：未在识别窗口内检测到左键输入的急停记录会显示为灰色。
- 同向检测开关：默认只检测反向急停，也可打开 A->A、D->D、W->W、S->S 这类同向重按检测。
- 后台记录模式：减少实时渲染开销，结束后生成统计报告。
- 可配置参数：显示点数、过滤阈值、射击窗口、按键映射、生理反应基准。
- GitHub Actions 自动构建：推送 `v*` 标签时自动构建 Windows `.exe` 并发布 Release。

## 急停判定逻辑

一次标准急停通常由以下事件组成：

```text
松开当前方向键 -> 按下相反方向键
```

例如：

```text
A -> D
D -> A
W -> S
S -> W
```

工具计算两次输入事件之间的时间差：

```text
Delta T = opposite_press_time - release_time
```

`Delta T` 越接近 0，说明反向急停输入越同步。负值通常代表反向键更早触发，正值通常代表反向键更晚触发。

## 射击分组

工具通过本地鼠标左键事件为急停记录打标签：

- `Shot`：急停后在射击窗口内检测到左键按下。
- `Spray`：急停发生时左键已经处于按住状态。
- `No shot`：射击窗口内没有检测到左键按下。

默认射击窗口为 `250ms`，用于判断是否存在射击意图。该窗口可以在界面中调整。

左键时机质量单独显示：

- `40-90ms`：合理射击时机。
- `<40ms`：偏早。
- `>90ms`：偏晚。

## 颜色规则

急停误差颜色同时考虑正负方向和严重程度：

- 接近 0ms：绿色。
- 负值偏大：蓝色到紫色。
- 正值偏大：黄色到红色。
- `No shot`：灰色。

历史记录中的 Shot 条目会额外用背景色标记左键时机是否处于 `40-90ms` 合理范围。

## 环境要求

- Python 3.8+
- Windows 10/11 推荐

由于底层键鼠钩子和 CS2 使用场景限制，主要目标平台是 Windows。

## 安装与运行

你可以直接从 [GitHub Releases](https://github.com/TsunamiBlue/CounterStrafeAnalyzer/releases) 下载 Windows `.exe` 版本运行，无需安装 Python 环境。

如果需要从源码运行，请先安装依赖：

```bash
pip install -r requirements.txt
```

运行程序：

```bash
python main.py
```

## 许可证

本项目采用 [Creative Commons Attribution-NonCommercial 4.0 International](LICENSE) 许可。

允许非商业用途下的复制、分享和改编，但不允许未经授权的商业使用。

## 致谢

本项目基于原始 Gitee 项目 [DDAsashio/CS2StopReflex](https://gitee.com/DDAsashio/CS2StopReflex) 继续整理和扩展。

## 免责声明

本工具仅用于本地输入分析和训练反馈，不读取游戏状态、不读取游戏内存、不修改游戏文件。若在 Faceit、5E 等反作弊严格的平台后台运行任何第三方输入监听工具，请自行评估风险。
