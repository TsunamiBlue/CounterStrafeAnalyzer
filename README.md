CS2 Counter-Strafing Evaluation Tool (Pro Tech Edition)

1. 项目简介

这是一个基于 Python 3 和 PyQt5 开发的高精度 CS2（Counter-Strike 2）急停操作评估工具。本工具通过底层键盘钩子（Keyboard Hooks）捕获原始输入信号，计算急停操作中的时间差（$\Delta T$），并提供多维度的可视化分析报告。

本工具专为职业选手及高阶玩家设计，旨在量化急停肌肉记忆，辅助提升射击精准度。

2. 核心功能

高精度信号采集：利用 pynput 库和 time.perf_counter() 实现纳秒级系统时间戳打标，确保存储的事件序列具备极高的置信度。

Tech UI 视觉风格：采用深色科技感界面，支持高性能实时渲染与背景网格绘制。

双模式运行：

实时渲染模式：实时显示当前按键状态、趋势图表及反应占比。

后台记录模式：降低 CPU/GPU 占用，在不影响游戏帧率的前提下在后台静默收集急停数据，并在结束后生成深度分析报告。

可视化分析：集成 Matplotlib 绘制 AD/WS 轴向的散点分布图与箱线图（Boxplot），直观展现操作的稳定性与一致性。

动态参数配置：支持生理反应基准设置、过滤阈值调整及自定义按键映射（支持非 WASD 布局）。

3. 技术原理：误差抵消逻辑

本工具的准确性建立在 Delta Time ($\Delta T$) 差分逻辑 之上。

假设系统存在固有的输入延迟 $L_{sys}$（包括 USB 回报率延迟、OS 调度延迟）：

信号 A（松开 A 键）：软件接收时刻 $T_{A} = T_{A\_phys} + L_{sys}$

信号 D（按下 D 键）：软件接收时刻 $T_{D} = T_{D\_phys} + L_{sys}$

计算误差：


$$\Delta T = T_{D} - T_{A} = (T_{D\_phys} + L_{sys}) - (T_{A\_phys} + L_{sys}) = T_{D\_phys} - T_{A\_phys}$$

结论：只要系统延迟在短时间内保持稳定，其常数项会在减法运算中被相互抵消。因此，本工具测得的数值反映的是玩家物理动作的真实偏差。

4. 安装与运行

4.1 环境要求

Python 3.8+

Windows 10/11 (由于底层钩子限制，暂不支持 macOS/Linux)

4.2 安装依赖

pip install PyQt5 pynput matplotlib


4.3 运行程序

python main.py


5. 编译与部署

代码已针对 Nuitka 和 PyInstaller 进行了资源路径兼容性优化（resource_path 函数）。

使用 Nuitka 编译（推荐，性能更高）：

nuitka --standalone --show-progress --show-memory --plugin-enable=qt-plugins --windows-disable-console --include-data-files=background.png=background.png main.py


6. 操作指南

生理反应基准：设置您的平均反应时间（默认 150ms），用于计算急停误差对射击窗口的影响占比。

后台记录：在进入正式比赛前点击“后台记录”，程序将停止所有 GUI 渲染，最大限度释放资源。比赛结束后点击“停止并分析”查看综合评级。

按键映射：如果您使用 ESDF 或其他自定义布局，请通过“按键映射”功能进行适配。

7. 免责声明

本工具仅作为本地输入信号分析使用，不修改任何游戏文件，不读取游戏内存，不属于作弊软件。但在参与官方反作弊严苛的赛事（如 Faceit/5E 等）时，请自行评估后台运行第三方输入监听工具的风险。

Senior Engineer's Note:

采集精度受限于 Windows 的系统滴答定时器精度（通常为 1ms 或 15.6ms）。本工具已尝试通过 perf_counter 提升精度，但在极高性能要求下，建议配合 1000Hz+ 回报率的键盘使用。