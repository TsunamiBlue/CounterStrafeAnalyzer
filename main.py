# -*- coding: utf-8 -*-
#
# CounterStrafeAnalyzer
# Local CS2 counter-strafing and shooting-input analysis tool.
#

import sys
import os
import time
from collections import deque
import statistics
import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget,
    QHBoxLayout, QListWidget, QMessageBox, QListWidgetItem, QPushButton,
    QGridLayout, QDialog,
    QRadioButton, QButtonGroup, QLineEdit, QFormLayout, QTextBrowser,
    QTabWidget, QFrame, QDoubleSpinBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, pyqtSlot
from PyQt5.QtGui import QFont, QColor, QBrush, QPixmap, QPainter
from pynput import keyboard, mouse

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import rcParams

# --- Global Settings ---
# Support Chinese characters in matplotlib
rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial']
rcParams['axes.unicode_minus'] = False
rcParams['savefig.facecolor'] = 'none'

# --- Theme System ---

# Dark theme color map — high contrast for dark backgrounds
_DARK = {
    'BG':              "#0a0a0a",
    'PANEL':           "#141414",
    'PANEL_LIGHT':     "#1e1e1e",
    'ACCENT':          "#00f3ff",
    'TEXT_MAIN':       "#f0f0f0",
    'TEXT_SUB':        "#999999",
    'KEY_OFF':         "#1f1f1f",
    'KEY_ON':          "#00f3ff",
    'BORDER':          "#333333",
    'DANGER':          "#ff5252",
    'WARNING':         "#ffea00",
    'SUCCESS':         "#00ff88",
    'NO_SHOT':         "#666666",
    'LIST_BG':         "#000000",
    'INPUT_BG':        "#0f0f0f",
    'BTN_HOVER_BG':    "#2a2a2a",
    'BTN_PRESS_BG':    "rgba(0, 243, 255, 0.1)",
    'SCROLL_HANDLE':   "#333333",
    'SCROLL_HANDLE_HV':"#555555",
    'ACCENT_RGBA':     "rgba(0, 243, 255, 0.15)",
}

# Light theme color map — high contrast for light backgrounds
_LIGHT = {
    'BG':              "#f0f0f0",
    'PANEL':           "#ffffff",
    'PANEL_LIGHT':     "#e8e8e8",
    'ACCENT':          "#0055aa",
    'TEXT_MAIN':       "#0a0a0a",
    'TEXT_SUB':        "#555555",
    'KEY_OFF':         "#d0d0d0",
    'KEY_ON':          "#0055aa",
    'BORDER':          "#bbbbbb",
    'DANGER':          "#b71c1c",
    'WARNING':         "#e65100",
    'SUCCESS':         "#008a00",
    'NO_SHOT':         "#888888",
    'LIST_BG':         "#ffffff",
    'INPUT_BG':        "#ffffff",
    'BTN_HOVER_BG':    "#d0d0d0",
    'BTN_PRESS_BG':    "rgba(0, 85, 170, 0.1)",
    'SCROLL_HANDLE':   "#cccccc",
    'SCROLL_HANDLE_HV':"#aaaaaa",
    'ACCENT_RGBA':     "rgba(0, 85, 170, 0.12)",
}

# Module-level color globals — initialized to dark theme
COLOR_BG = COLOR_PANEL = COLOR_PANEL_LIGHT = COLOR_ACCENT = ""
COLOR_TEXT_MAIN = COLOR_TEXT_SUB = COLOR_KEY_OFF = COLOR_KEY_ON = ""
COLOR_BORDER = COLOR_DANGER = COLOR_WARNING = COLOR_SUCCESS = COLOR_NO_SHOT = ""

def _build_stylesheet(c):
    """Build a Qt stylesheet string from a theme color dictionary `c`."""
    return f"""
    QMainWindow {{
        background-color: {c['BG']};
    }}
    QWidget {{
        color: {c['TEXT_MAIN']};
        font-family: "Microsoft YaHei UI", sans-serif;
    }}
    QGroupBox {{
        border: none;
        background-color: {c['PANEL']};
        border-radius: 8px;
        padding-top: 15px;
        margin-top: 0px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 5px 0px 0px 5px;
        left: 10px;
        color: {c['TEXT_SUB']};
        font-size: 11px;
        font-weight: bold;
    }}
    QListWidget {{
        background-color: {c['LIST_BG']};
        border: 1px solid {c['BORDER']};
        border-radius: 4px;
        outline: none;
        font-family: "Consolas", monospace;
    }}
    QListWidget::item:selected {{
        background-color: {c['ACCENT_RGBA']};
        color: {c['ACCENT']};
        border-left: 2px solid {c['ACCENT']};
    }}
    QTabWidget::pane {{
        border: none;
        background: {c['PANEL']};
    }}
    QTabBar::tab {{
        background: {c['BG']};
        color: {c['TEXT_SUB']};
        padding: 8px 16px;
        border: none;
        border-bottom: 2px solid {c['BORDER']};
        font-weight: bold;
    }}
    QTabBar::tab:selected {{
        color: {c['ACCENT']};
        border-bottom: 2px solid {c['ACCENT']};
    }}
    QPushButton {{
        background-color: {c['PANEL_LIGHT']};
        border: 1px solid {c['BORDER']};
        border-radius: 4px;
        padding: 8px 16px;
        color: {c['TEXT_MAIN']};
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: {c['BTN_HOVER_BG']};
        border-color: {c['ACCENT']};
        color: {c['ACCENT']};
    }}
    QPushButton:pressed {{
        background-color: {c['BTN_PRESS_BG']};
        border-color: {c['ACCENT']};
    }}
    QSpinBox, QDoubleSpinBox {{
        background-color: {c['INPUT_BG']};
        border: 1px solid {c['BORDER']};
        color: {c['ACCENT']};
        padding: 5px;
        border-radius: 3px;
        font-family: "Consolas";
        font-weight: bold;
    }}
    QLineEdit {{
        background: {c['INPUT_BG']};
        color: {c['ACCENT']};
        border: 1px solid {c['BORDER']};
        padding: 4px;
        border-radius: 3px;
        font-family: "Consolas";
    }}
    QScrollBar:vertical {{
        border: none;
        background: {c['BG']};
        width: 6px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {c['SCROLL_HANDLE']};
        min-height: 20px;
        border-radius: 3px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {c['SCROLL_HANDLE_HV']};
    }}
"""

# Current stylesheet and dark-mode flag
STYLESHEET = ""
_IS_DARK = True


def apply_theme(is_dark):
    """Switch between dark and light themes (updates module-level globals)."""
    global COLOR_BG, COLOR_PANEL, COLOR_PANEL_LIGHT, COLOR_ACCENT
    global COLOR_TEXT_MAIN, COLOR_TEXT_SUB, COLOR_KEY_OFF, COLOR_KEY_ON
    global COLOR_BORDER, COLOR_DANGER, COLOR_WARNING, COLOR_SUCCESS, COLOR_NO_SHOT
    global STYLESHEET, _IS_DARK

    c = _DARK if is_dark else _LIGHT
    COLOR_BG = c['BG']
    COLOR_PANEL = c['PANEL']
    COLOR_PANEL_LIGHT = c['PANEL_LIGHT']
    COLOR_ACCENT = c['ACCENT']
    COLOR_TEXT_MAIN = c['TEXT_MAIN']
    COLOR_TEXT_SUB = c['TEXT_SUB']
    COLOR_KEY_OFF = c['KEY_OFF']
    COLOR_KEY_ON = c['KEY_ON']
    COLOR_BORDER = c['BORDER']
    COLOR_DANGER = c['DANGER']
    COLOR_WARNING = c['WARNING']
    COLOR_SUCCESS = c['SUCCESS']
    COLOR_NO_SHOT = c['NO_SHOT']
    STYLESHEET = _build_stylesheet(c)
    _IS_DARK = is_dark


# Initialize with dark theme
apply_theme(True)

def resource_path(relative_path):
    """ 
    获取资源的绝对路径 (兼容 PyInstaller 和 Nuitka Standalone) 
    """
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# --- Custom Widgets ---

class BackgroundWidget(QWidget):
    """ Container supporting background image and Tech-style grid """
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.pixmap = None
        self._bg_visible = False
        if os.path.exists(image_path):
            self.pixmap = QPixmap(image_path)

    def set_bg_visible(self, visible):
        self._bg_visible = visible
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(COLOR_BG))
        
        if self.pixmap and self._bg_visible:
            scaled = self.pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
        
        self.draw_grid(painter)

    def draw_grid(self, painter):
        painter.setPen(QColor(255, 255, 255, 3))
        grid_size = 40
        w, h = self.width(), self.height()
        for x in range(0, w, grid_size):
            painter.drawLine(x, 0, x, h)
        for y in range(0, h, grid_size):
            painter.drawLine(0, y, w, y)

class KeyCapWidget(QLabel):
    """ UI Component simulating a keyboard key (Tech Style) """
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignCenter)
        self.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
        self.setFixedSize(64, 64)
        
        self.default_style = f"""
            background-color: {COLOR_KEY_OFF};
            color: #555;
            border: 1px solid #333;
            border-radius: 8px;
            border-bottom: 5px solid #111;
            margin-bottom: 2px;
        """
        self.active_style = f"""
            background-color: rgba(0, 243, 255, 0.15);
            color: {COLOR_KEY_ON};
            border: 1px solid {COLOR_KEY_ON};
            border-radius: 8px;
            border-bottom: 2px solid {COLOR_KEY_ON};
            margin-top: 3px;
            margin-bottom: 0px;
            box-shadow: 0 0 10px {COLOR_KEY_ON};
        """
        self.setStyleSheet(self.default_style)

    def set_active(self, active):
        self.setStyleSheet(self.active_style if active else self.default_style)

class ModernDialog(QDialog):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setStyleSheet(STYLESHEET)

class OptionDialog(ModernDialog):
    def __init__(self, title, options, parent=None):
        super().__init__(title, parent)
        layout = QVBoxLayout(self)
        self.button_group = QButtonGroup(self)
        for option in options:
            rb = QRadioButton(option)
            rb.setStyleSheet(f"color: {COLOR_TEXT_MAIN}; padding: 8px;")
            self.button_group.addButton(rb)
            layout.addWidget(rb)
            if option == options[0]: rb.setChecked(True)
        
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        layout.addLayout(btn_layout)
    
    def set_selected_option(self, text):
        for btn in self.button_group.buttons():
            if btn.text() == text:
                btn.setChecked(True)
                break

    def get_selected_option(self):
        return self.button_group.checkedButton().text() if self.button_group.checkedButton() else None

class KeyMappingDialog(ModernDialog):
    def __init__(self, current_mappings, parent=None):
        super().__init__("按键映射设置", parent)
        self.new_mappings = current_mappings.copy()
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        self.inputs = {}
        
        hint = QLabel("请输入对应 WASD 功能的实际按键（单个字母）")
        hint.setStyleSheet(f"color: {COLOR_TEXT_SUB}; margin-bottom: 10px;")
        layout.addWidget(hint)

        for key in ['W', 'A', 'S', 'D']:
            le = QLineEdit(current_mappings.get(key, key))
            le.setMaxLength(1)
            self.inputs[key] = le
            label = QLabel(f"功能 {key}:")
            label.setStyleSheet(f"color: {COLOR_TEXT_MAIN}; font-weight: bold;")
            form_layout.addRow(label, le)
        
        layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("保存")
        ok_btn.clicked.connect(self.save)
        ok_btn.setStyleSheet(f"background-color: rgba(0, 243, 255, 0.1); border: 1px solid {COLOR_ACCENT}; color: {COLOR_ACCENT};")
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        
        reset_btn = QPushButton("恢复默认")
        reset_btn.clicked.connect(self.reset_default)
        reset_btn.setStyleSheet(f"color: {COLOR_WARNING};")
        
        btn_layout.addWidget(reset_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def save(self):
        temp = {}
        seen = set()
        for k, le in self.inputs.items():
            val = le.text().upper().strip()
            if not val or not val.isalnum():
                QMessageBox.warning(self, "错误", f"{k} 键映射无效")
                return
            if val in seen:
                QMessageBox.warning(self, "错误", f"按键 {val} 重复")
                return
            seen.add(val)
            temp[k] = val
        self.new_mappings = temp
        self.accept()

    def reset_default(self):
        for k in ['W', 'A', 'S', 'D']:
            self.inputs[k].setText(k)

    def get_mappings(self):
        return self.new_mappings

class PrinciplesDialog(ModernDialog):
    def __init__(self, parent=None):
        super().__init__("核心原理 (Core Logic)", parent)
        self.resize(750, 600)
        layout = QVBoxLayout(self)
        
        browser = QTextBrowser()
        browser.setStyleSheet(f"background: {COLOR_PANEL}; color: {COLOR_TEXT_MAIN}; border: none; font-size: 14px; line-height: 1.6;")
        
        html = f"""
        <style>
            h3 {{ color: {COLOR_ACCENT}; margin-top: 25px; margin-bottom: 10px; }}
            b {{ color: #ffffff; }}
            .highlight {{ color: {COLOR_SUCCESS}; font-weight: bold; }}
            .path {{ background-color: #222; padding: 10px; border-radius: 6px; font-family: Consolas; color: #ddd; border: 1px dashed {COLOR_BORDER}; margin-bottom: 15px; }}
            li {{ margin-bottom: 8px; }}
        </style>
        
        <h3>1. 信号路径演示</h3>
        <p>键盘信号到达本软件的完整路径如下：</p>
        <div class="path">
        [手指触轴] → [键盘MCU处理] → [USB传输线] → [Windows操作系统] → <b style="color:{COLOR_ACCENT}">[软件钩子截获时间戳]</b> → [屏幕显示]
        </div>
        <p>本工具在<b>“软件钩子截获”</b>这一步打上时间戳（T1, T2）。</p>

        <h3>2. 为什么软件是准确的？(Delta Time)</h3>
        <p>我们计算的是两个按键的<b>时间差 (ΔT)</b>。</p>
        <ul>
            <li>假设你的电脑存在 5ms 的系统延迟（USB回报率+系统调度）。</li>
            <li>按下 A 键：软件接收时刻 = 物理时刻A + 5ms</li>
            <li>按下 D 键：软件接收时刻 = 物理时刻D + 5ms</li>
            <li><b>计算结果：</b> (物理时刻D + 5ms) - (物理时刻A + 5ms) = <span class="highlight">物理时刻D - 物理时刻A</span></li>
        </ul>
        <p><b>结论：</b>只要系统延迟是稳定的，它们就会在减法运算中<b>互相抵消</b>。因此，软件测出的就是你手指动作的真实时间差。</p>

        <h3>3. 关于 CPU 响应与测试误差</h3>
        <p>经常有用户问：<i>“我的 CPU 比较慢，会不会导致测试不准？”</i></p>
        <ul>
            <li><b>采集端 (准确)：</b> 软件使用独立线程监听底层信号，优先级非常高。只要电脑没有卡死（CPU 100%），信号的<b>采集时间</b>都是准确的纳秒级时间戳。</li>
            <li><b>显示端 (无关)：</b> 就算 CPU 慢导致界面动画卡顿、数字显示慢了 0.5 秒，这只影响你<b>看到结果</b>的快慢，完全不影响<b>结果数值本身</b>的准确性。</li>
        </ul>
        """
        browser.setHtml(html)
        layout.addWidget(browser)
        
        btn = QPushButton("明白")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

class AnalysisReportDialog(ModernDialog):
    def __init__(self, records, parent=None):
        super().__init__("后台记录分析报告", parent)
        self.resize(500, 400)
        layout = QVBoxLayout(self)
        
        if not records:
            label = QLabel("期间未检测到有效的急停操作。")
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)
        else:
            diffs = [abs(r['time_diff'] * 1000) for r in records]
            raw_diffs = [r['time_diff'] * 1000 for r in records]
            
            count = len(records)
            avg_abs = statistics.mean(diffs)
            avg_raw = statistics.mean(raw_diffs)
            stdev = statistics.stdev(diffs) if count > 1 else 0.0
            best = min(diffs)
            worst = max(diffs)
            
            grade = "S" if avg_abs < 10 and stdev < 5 else "A" if avg_abs < 20 else "B" if avg_abs < 40 else "C"
            grade_color = COLOR_SUCCESS if grade == "S" else COLOR_ACCENT if grade == "A" else COLOR_WARNING
            
            html = f"""
            <style>
                h2 {{ color: {grade_color}; text-align: center; font-size: 36px; margin: 0; }}
                .stat-box {{ background: {COLOR_PANEL_LIGHT}; padding: 10px; border-radius: 6px; margin-bottom: 5px; }}
                .label {{ color: {COLOR_TEXT_SUB}; font-size: 12px; }}
                .val {{ color: {COLOR_TEXT_MAIN}; font-size: 18px; font-weight: bold; font-family: Consolas; }}
            </style>
            <div style="text-align: center;">
                <span style="font-size: 14px; color: #888;">综合评级</span>
                <h2>{grade}</h2>
                <p>共记录 <b>{count}</b> 次急停</p>
            </div>
            
            <div class="stat-box">
                <span class="label">平均误差 (越低越好)</span><br>
                <span class="val">{avg_abs:.1f} ms</span>
                <span style="color: #666; font-size: 12px;">(整体偏差: {avg_raw:+.1f} ms)</span>
            </div>
            
            <div class="stat-box">
                <span class="label">稳定性 (标准差)</span><br>
                <span class="val">{stdev:.1f}</span>
            </div>
            
            <div style="display: flex; justify-content: space-between;">
                <div class="stat-box" style="width: 45%;">
                    <span class="label">最佳</span><br>
                    <span class="val" style="color: {COLOR_SUCCESS}">{best:.1f} ms</span>
                </div>
                <div class="stat-box" style="width: 45%;">
                    <span class="label">最差</span><br>
                    <span class="val" style="color: {COLOR_DANGER}">{worst:.1f} ms</span>
                </div>
            </div>
            """
            
            browser = QTextBrowser()
            browser.setStyleSheet("background: transparent; border: none;")
            browser.setHtml(html)
            layout.addWidget(browser)

        btn = QPushButton("关闭报告")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

# --- Main Window ---

class MainWindow(QMainWindow):
    feedback_signal = pyqtSignal(str, QColor)
    history_signal = pyqtSignal(str, object, float, dict, QColor)
    key_state_signal = pyqtSignal(str, bool) 
    start_timer_signal = pyqtSignal(str, int)
    stop_timer_signal = pyqtSignal(str)
    key_press_signal = pyqtSignal(str, float)
    key_release_signal = pyqtSignal(str, float)
    mouse_click_signal = pyqtSignal(bool, float)
    log_signal = pyqtSignal(str)
    update_dashboard_signal = pyqtSignal(float, float)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CS2 急停评估工具 - Pro (Tech Edition)")
        self.resize(1150, 750)
        
        # Parameters
        self.human_reaction_time = 150.0 
        self.key_mappings = {'W': 'W', 'A': 'A', 'S': 'S', 'D': 'D'}
        self.reverse_key_mappings = {v: k for k, v in self.key_mappings.items()}
        self.key_state = {k: {'pressed': False, 'time': None} for k in ['W', 'A', 'S', 'D']}
        self.waiting_for_opposite_key = {}
        self.ad_data = deque(maxlen=200)
        self.ws_data = deque(maxlen=200)
        self.record_count = 20
        self.filter_threshold = 120
        self.last_record_time = 0
        self.min_time_between_records = 0.05
        self.same_direction_detection = False
        self.shot_detection_window = 0.25
        self.shot_pre_window = 0.05
        self.mouse_left_pressed = False
        self.recent_left_press_time = None
        self.pending_shot_events = []
        
        self.background_recording_active = False
        self.background_buffer = []

        self.setup_ui()
        self.init_plots()
        self.setup_signals()
        self.start_listener()

    def setup_ui(self):
        QApplication.instance().setStyleSheet(STYLESHEET)
        
        background_path = resource_path("background.png")
        central_widget = BackgroundWidget(background_path, self)
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Left Panel
        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)
        
        self.feedback_label = QLabel("等待输入...")
        self.feedback_label.setAlignment(Qt.AlignCenter)
        self.feedback_label.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        self.feedback_label.setFixedHeight(50)
        self.feedback_label.setStyleSheet(f"""
            background-color: {COLOR_PANEL}; 
            color: {COLOR_TEXT_SUB}; 
            border-radius: 4px; 
            border-left: 4px solid {COLOR_BORDER};
        """)
        left_panel.addWidget(self.feedback_label)
        
        key_container = QWidget()
        key_layout = QGridLayout(key_container)
        key_layout.setContentsMargins(0, 10, 0, 10)
        key_layout.setAlignment(Qt.AlignCenter)
        
        self.key_widgets = {k: KeyCapWidget(k) for k in ['W', 'A', 'S', 'D']}
        key_layout.addWidget(self.key_widgets['W'], 0, 1)
        key_layout.addWidget(self.key_widgets['A'], 1, 0)
        key_layout.addWidget(self.key_widgets['S'], 1, 1)
        key_layout.addWidget(self.key_widgets['D'], 1, 2)
        left_panel.addWidget(key_container)
        
        self.tab_widget = QTabWidget()
        self.history_list = QListWidget()
        self.history_list.setFocusPolicy(Qt.NoFocus)
        # --- 修改点: 禁用交替背景，确保全黑 ---
        self.history_list.setAlternatingRowColors(False) 
        self.tab_widget.addTab(self.history_list, "历史数据")
        
        self.output_list = QListWidget()
        self.output_list.setStyleSheet(f"color: {COLOR_TEXT_SUB};")
        self.tab_widget.addTab(self.output_list, "系统日志")

        self.direction_analysis_view = QTextBrowser()
        self.direction_analysis_view.setStyleSheet(f"""
            QTextBrowser {{
                background-color: {COLOR_BG};
                border: 1px solid {COLOR_BORDER};
                border-radius: 4px;
                color: {COLOR_TEXT_MAIN};
                font-family: "Microsoft YaHei UI";
            }}
        """)
        self.tab_widget.addTab(self.direction_analysis_view, "方向分析")
        self.update_direction_analysis()
        left_panel.addWidget(self.tab_widget, stretch=1)
        
        self.controls_frame = QFrame()
        self.controls_frame.setStyleSheet(f"background-color: {COLOR_PANEL}; border-radius: 6px;")
        controls_layout = QVBoxLayout(self.controls_frame)
        controls_layout.setSpacing(8)
        
        row1 = QHBoxLayout()
        self.record_count_button = QPushButton(f"显示: {self.record_count}")
        self.record_count_button.clicked.connect(self.set_record_count)
        self.filter_threshold_button = QPushButton(f"阈值: {self.filter_threshold}ms")
        self.filter_threshold_button.clicked.connect(self.set_filter_threshold)
        self.same_direction_btn = QPushButton("同向检测: 关")
        self.same_direction_btn.clicked.connect(self.toggle_same_direction_detection)
        self.theme_toggle_btn = QPushButton("主题: 暗色")
        self.theme_toggle_btn.clicked.connect(self.toggle_theme)
        row1.addWidget(self.record_count_button)
        row1.addWidget(self.filter_threshold_button)
        row1.addWidget(self.same_direction_btn)
        row1.addWidget(self.theme_toggle_btn)
        
        row2 = QHBoxLayout()
        self.key_mapping_button = QPushButton("按键映射")
        self.key_mapping_button.clicked.connect(self.show_key_mapping_dialog)
        self.shot_window_button = QPushButton(f"射击窗口: {int(self.shot_detection_window * 1000)}ms")
        self.shot_window_button.clicked.connect(self.set_shot_detection_window)
        self.principle_button = QPushButton("核心原理")
        self.principle_button.clicked.connect(self.show_principle_dialog)
        row2.addWidget(self.key_mapping_button)
        row2.addWidget(self.shot_window_button)
        row2.addWidget(self.principle_button)
        
        row3 = QHBoxLayout()
        self.bg_record_btn = QPushButton("后台记录 (不渲染)")
        self.bg_record_btn.clicked.connect(self.toggle_background_recording)
        self.bg_record_btn.setStyleSheet(f"border: 1px dashed {COLOR_ACCENT}; color: {COLOR_ACCENT};")
        self.refresh_button = QPushButton("重置数据")
        self.refresh_button.clicked.connect(self.refresh)
        self.refresh_button.setStyleSheet(f"color: {COLOR_DANGER};")
        row3.addWidget(self.bg_record_btn)
        row3.addWidget(self.refresh_button)
        
        controls_layout.addLayout(row1)
        controls_layout.addLayout(row2)
        controls_layout.addLayout(row3)
        left_panel.addWidget(self.controls_frame)

        # Right Panel
        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)

        self.dashboard_frame = QFrame()
        self.dashboard_frame.setStyleSheet(f"background-color: {COLOR_PANEL}; border-radius: 6px;")
        dashboard_layout = QHBoxLayout(self.dashboard_frame)
        
        input_layout = QVBoxLayout()
        self.input_label = QLabel("生理反应基准 (ms):")
        self.input_label.setStyleSheet(f"color: {COLOR_TEXT_SUB}; font-size: 12px;")
        self.reaction_spin = QDoubleSpinBox()
        self.reaction_spin.setRange(50, 500)
        self.reaction_spin.setValue(150.0)
        self.reaction_spin.setSuffix(" ms")
        self.reaction_spin.valueChanged.connect(self.update_reaction_time)
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.reaction_spin)
        input_layout.addStretch()
        
        self.impact_label = QLabel()
        self.impact_label.setAlignment(Qt.AlignCenter)
        self.impact_label.setText(f"<span style='color:{COLOR_TEXT_SUB}; font-size:14px;'>等待操作数据...</span>")
        dashboard_layout.addLayout(input_layout, 1)
        dashboard_layout.addWidget(self.impact_label, 3)
        right_panel.addWidget(self.dashboard_frame)

        # Charts
        self.ad_figure = Figure(figsize=(5, 4), dpi=100); self.ad_figure.patch.set_alpha(0)
        self.ad_canvas = FigureCanvas(self.ad_figure); self.ad_canvas.setStyleSheet("background-color: transparent;")
        self.ad_chart_label = QLabel("AD 急停趋势", styleSheet=f"color:{COLOR_TEXT_SUB};font-weight:bold;")
        ad_layout = QVBoxLayout(); ad_layout.addWidget(self.ad_chart_label); ad_layout.addWidget(self.ad_canvas)
        right_panel.addLayout(ad_layout)

        self.ws_figure = Figure(figsize=(5, 4), dpi=100); self.ws_figure.patch.set_alpha(0)
        self.ws_canvas = FigureCanvas(self.ws_figure); self.ws_canvas.setStyleSheet("background-color: transparent;")
        self.ws_chart_label = QLabel("WS 急停趋势", styleSheet=f"color:{COLOR_TEXT_SUB};font-weight:bold;")
        ws_layout = QVBoxLayout(); ws_layout.addWidget(self.ws_chart_label); ws_layout.addWidget(self.ws_canvas)
        right_panel.addLayout(ws_layout)

        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(right_panel, 2)

    def setup_signals(self):
        self.feedback_signal.connect(self.update_feedback)
        self.history_signal.connect(self.update_history)
        self.key_state_signal.connect(self.update_key_state_display)
        self.start_timer_signal.connect(self.start_timer)
        self.stop_timer_signal.connect(self.stop_timer)
        self.key_press_signal.connect(self.on_key_press_main_thread)
        self.key_release_signal.connect(self.on_key_release_main_thread)
        self.mouse_click_signal.connect(self.on_mouse_click_main_thread)
        self.log_signal.connect(self.append_log)
        self.update_dashboard_signal.connect(self.update_dashboard_ui)

        self.timers = {'AD': QTimer(self), 'WS': QTimer(self)}
        for t in self.timers.values(): t.setSingleShot(True)
        self.timers['AD'].timeout.connect(lambda: self.reset_quick_stop('AD'))
        self.timers['WS'].timeout.connect(lambda: self.reset_quick_stop('WS'))

    def start_listener(self):
        try:
            self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
            self.listener.start()
            self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click)
            self.mouse_listener.start()
            self.append_log("键盘/鼠标监听器已就绪")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"监听启动失败: {e}")

    def init_plots(self):
        self.ax_ad_line = self.ad_figure.add_subplot(211); self.ax_ad_box = self.ad_figure.add_subplot(212)
        self.ax_ws_line = self.ws_figure.add_subplot(211); self.ax_ws_box = self.ws_figure.add_subplot(212)
        for ax in [self.ax_ad_line, self.ax_ad_box, self.ax_ws_line, self.ax_ws_box]: self.setup_axes_style(ax)
        self.ad_figure.tight_layout(); self.ws_figure.tight_layout()

    def setup_axes_style(self, ax):
        ax.set_facecolor('none')
        ax.tick_params(colors=COLOR_TEXT_SUB, labelsize=8)
        for spine in ax.spines.values(): spine.set_color(COLOR_BORDER)
        ax.grid(True, linestyle='--', alpha=0.1, color=COLOR_TEXT_MAIN)

    def update_reaction_time(self, val): self.human_reaction_time = val

    def on_press(self, key):
        try: self.key_press_signal.emit(key.char.upper(), time.perf_counter())
        except AttributeError: pass

    def on_release(self, key):
        try: self.key_release_signal.emit(key.char.upper(), time.perf_counter())
        except AttributeError: pass

    def on_mouse_click(self, x, y, button, pressed):
        if button == mouse.Button.left:
            self.mouse_click_signal.emit(pressed, time.perf_counter())

    @pyqtSlot(bool, float)
    def on_mouse_click_main_thread(self, pressed, event_time):
        self.mouse_left_pressed = pressed
        if pressed:
            self.recent_left_press_time = event_time
            self.update_pending_shot_events(event_time)

    @pyqtSlot(str, float)
    def on_key_press_main_thread(self, orig_char, press_time):
        mapped = self.reverse_key_mappings.get(orig_char)
        if not mapped: return

        if not self.key_state[mapped]['pressed']:
            self.key_state[mapped]['pressed'] = True
            self.key_state[mapped]['time'] = press_time
            if not self.background_recording_active:
                self.key_state_signal.emit(mapped, True)

            key_type = self.get_key_type(mapped)
            if not key_type:
                return

            if key_type in self.waiting_for_opposite_key and mapped in self.waiting_for_opposite_key[key_type]['allowed_keys']:
                current_time = time.perf_counter()
                if current_time - self.last_record_time >= self.min_time_between_records:
                    waiting = self.waiting_for_opposite_key[key_type]
                    release_time = waiting['release_time']
                    diff_ms = (press_time - release_time) * 1000
                    transition = f"{waiting['released_key']}->{mapped}"
                    self.process_stop_event(key_type, diff_ms, press_time, transition)
                    self.last_record_time = current_time
                del self.waiting_for_opposite_key[key_type]
                self.stop_timer_signal.emit(key_type)
            elif key_type in self.waiting_for_opposite_key and mapped in self.get_axis_keys(key_type):
                del self.waiting_for_opposite_key[key_type]
                self.stop_timer_signal.emit(key_type)

            other_type = 'WS' if key_type == 'AD' else 'AD'
            if other_type in self.waiting_for_opposite_key:
                del self.waiting_for_opposite_key[other_type]
                self.stop_timer_signal.emit(other_type)

    @pyqtSlot(str, float)
    def on_key_release_main_thread(self, orig_char, release_time):
        mapped = self.reverse_key_mappings.get(orig_char)
        if not mapped: return

        if self.key_state[mapped]['pressed']:
            self.key_state[mapped]['pressed'] = False
            if not self.background_recording_active:
                self.key_state_signal.emit(mapped, False)
            
            key_type = self.get_key_type(mapped)
            if not key_type: return

            opp_mapped = 'D' if mapped == 'A' else 'A' if key_type == 'AD' else 'S' if mapped == 'W' else 'W'
            opp_state = self.key_state[opp_mapped]

            if opp_state['pressed']:
                current_time = time.perf_counter()
                if current_time - self.last_record_time >= self.min_time_between_records:
                    diff_ms = (opp_state['time'] - release_time) * 1000
                    transition = f"{mapped}->{opp_mapped}"
                    self.process_stop_event(key_type, diff_ms, release_time, transition)
                    self.last_record_time = current_time
                if key_type in self.waiting_for_opposite_key:
                    del self.waiting_for_opposite_key[key_type]
                    self.stop_timer_signal.emit(key_type)
                return

            allowed_keys = {opp_mapped}
            if self.same_direction_detection:
                allowed_keys.add(mapped)
            self.waiting_for_opposite_key[key_type] = {
                'released_key': mapped,
                'allowed_keys': allowed_keys,
                'release_time': release_time
            }
            self.start_timer_signal.emit(key_type, self.filter_threshold + 20)

    def process_stop_event(self, key_type, diff_ms, event_time, transition):
        if abs(diff_ms) > self.filter_threshold: return

        shot_type, shot_delay_ms = self.classify_shot_type(event_time)

        if self.background_recording_active:
            entry = {
                'time': event_time,
                'wall_time': datetime.datetime.now(),
                'time_diff': diff_ms / 1000.0,
                'key_type': key_type,
                'transition': transition,
                'shot_type': shot_type,
                'shot_delay_ms': shot_delay_ms
            }
            self.background_buffer.append(entry)
            if key_type == 'AD': self.ad_data.append(entry)
            else: self.ws_data.append(entry)
            self.queue_no_shot_update(entry)
            return

        impact_percentage = (abs(diff_ms) / self.human_reaction_time) * 100
        data_entry = {
            'time': event_time,
            'wall_time': datetime.datetime.now(),
            'time_diff': diff_ms / 1000.0,
            'key_type': key_type,
            'transition': transition,
            'shot_type': shot_type,
            'shot_delay_ms': shot_delay_ms
        }
        color = self.get_record_color(data_entry)
        timing_str = "完美" if abs(diff_ms) <= 5 else ("太快" if diff_ms < 0 else "太慢")

        self.feedback_signal.emit(f"[{key_type} {transition} {self.format_shot_tag(data_entry)}] {timing_str}: {diff_ms:+.1f} ms", color)
        self.update_dashboard_signal.emit(diff_ms, impact_percentage)

        if key_type == 'AD': self.ad_data.append(data_entry)
        else: self.ws_data.append(data_entry)

        self.history_signal.emit("", data_entry['wall_time'], diff_ms / 1000.0, data_entry, color)
        self.update_plots_efficiently()
        self.update_direction_analysis()
        self.queue_no_shot_update(data_entry)

    def classify_shot_type(self, event_time):
        if self.mouse_left_pressed:
            return "Spray", None
        if self.recent_left_press_time is None:
            return "No shot", None
        if 0 <= event_time - self.recent_left_press_time <= self.shot_pre_window:
            return "Shot", (event_time - self.recent_left_press_time) * 1000
        return "No shot", None

    def queue_no_shot_update(self, entry):
        if entry.get('shot_type') != "No shot":
            return
        self.pending_shot_events.append(entry)
        QTimer.singleShot(int(self.shot_detection_window * 1000), lambda: self.finalize_pending_shot_event(entry))

    def finalize_pending_shot_event(self, entry):
        if entry in self.pending_shot_events:
            self.pending_shot_events.remove(entry)

    def update_pending_shot_events(self, press_time):
        updated = False
        for entry in list(self.pending_shot_events):
            delta = press_time - entry['time']
            if delta < 0:
                continue
            if delta <= self.shot_detection_window:
                entry['shot_type'] = "Shot"
                entry['shot_delay_ms'] = delta * 1000
                self.pending_shot_events.remove(entry)
                self.refresh_record_display(entry)
                updated = True
            else:
                self.pending_shot_events.remove(entry)
        if updated and not self.background_recording_active:
            self.update_plots_efficiently()
            self.update_direction_analysis()

    def refresh_record_display(self, entry):
        item = entry.get('history_item')
        if item is not None:
            item.setText(self.format_history_item_text(entry))
            item.setForeground(QBrush(self.get_record_color(entry)))
            diff_ms = entry['time_diff'] * 1000
            timing_str = "完美" if abs(diff_ms) <= 5 else ("太快" if diff_ms < 0 else "太慢")
            self.feedback_signal.emit(
                f"[{entry['key_type']} {entry['transition']} {self.format_shot_tag(entry)}] {timing_str}: {diff_ms:+.1f} ms",
                self.get_record_color(entry)
            )

    def get_key_type(self, key):
        if key in ['A', 'D']: return 'AD'
        if key in ['W', 'S']: return 'WS'
        return None

    def get_axis_keys(self, key_type):
        return {'A', 'D'} if key_type == 'AD' else {'W', 'S'}

    def toggle_same_direction_detection(self):
        self.same_direction_detection = not self.same_direction_detection
        self.waiting_for_opposite_key.clear()
        for timer in self.timers.values():
            timer.stop()
        self.same_direction_btn.setText(f"同向检测: {'开' if self.same_direction_detection else '关'}")

    def toggle_background_recording(self):
        if not self.background_recording_active:
            self.background_recording_active = True
            self.background_buffer = []
            self.bg_record_btn.setText("停止并分析 (正在记录...)")
            self.bg_record_btn.setStyleSheet(f"background-color: {COLOR_ACCENT}; color: #000; border: none;")
            self.feedback_label.setText("后台记录模式运行中...")
            self.feedback_label.setStyleSheet(f"background-color: {COLOR_PANEL}; color: {COLOR_ACCENT}; border-left: 4px solid {COLOR_ACCENT};")
        else:
            self.background_recording_active = False
            self.bg_record_btn.setText("后台记录 (不渲染)")
            self.bg_record_btn.setStyleSheet(f"border: 1px dashed {COLOR_ACCENT}; color: {COLOR_ACCENT};")
            self.update_plots_efficiently()
            self.update_direction_analysis()
            AnalysisReportDialog(self.background_buffer, self).exec_()
    
    def toggle_theme(self):
        """Switch between dark and light themes."""
        global _IS_DARK
        new_is_dark = not _IS_DARK
        apply_theme(new_is_dark)

        # Re-apply global stylesheet
        QApplication.instance().setStyleSheet(STYLESHEET)

        # Update standalone widget styles that use inline setStyleSheet
        self.feedback_label.setStyleSheet(f"""
            background-color: {COLOR_PANEL};
            color: {COLOR_TEXT_SUB};
            border-radius: 4px;
            border-left: 4px solid {COLOR_BORDER};
        """)
        self.output_list.setStyleSheet(f"color: {COLOR_TEXT_SUB};")
        self.direction_analysis_view.setStyleSheet(f"""
            QTextBrowser {{
                background-color: {COLOR_BG};
                border: 1px solid {COLOR_BORDER};
                border-radius: 4px;
                color: {COLOR_TEXT_MAIN};
                font-family: "Microsoft YaHei UI";
            }}
        """)
        self.controls_frame.setStyleSheet(f"background-color: {COLOR_PANEL}; border-radius: 6px;")
        self.dashboard_frame.setStyleSheet(f"background-color: {COLOR_PANEL}; border-radius: 6px;")
        self.refresh_button.setStyleSheet(f"color: {COLOR_DANGER};")
        self.input_label.setStyleSheet(f"color: {COLOR_TEXT_SUB}; font-size: 12px;")
        chart_label_style = f"color:{COLOR_TEXT_SUB};font-weight:bold;"
        self.ad_chart_label.setStyleSheet(chart_label_style)
        self.ws_chart_label.setStyleSheet(chart_label_style)

        # Update KeyCap widgets
        for key in ['W', 'A', 'S', 'D']:
            w = self.key_widgets[key]
            is_active = self.key_state[key]['pressed']
            key_border_color = '#333333' if _IS_DARK else '#cccccc'
            key_bottom_color = '#111111' if _IS_DARK else '#aaaaaa'
            key_text_color = '#555555' if _IS_DARK else '#999999'
            w.default_style = f"""
                background-color: {COLOR_KEY_OFF};
                color: {key_text_color};
                border: 1px solid {key_border_color};
                border-radius: 8px;
                border-bottom: 5px solid {key_bottom_color};
                margin-bottom: 2px;
            """
            w.active_style = f"""
                background-color: rgba(0, 243, 255, 0.15);
                color: {COLOR_KEY_ON};
                border: 1px solid {COLOR_KEY_ON};
                border-radius: 8px;
                border-bottom: 2px solid {COLOR_KEY_ON};
                margin-top: 3px;
                margin-bottom: 0px;
                box-shadow: 0 0 10px {COLOR_KEY_ON};
            """
            w.setStyleSheet(w.active_style if is_active else w.default_style)

        # Update charts
        self.update_plots_efficiently()
        self.update_direction_analysis()

        # Update toggle button text
        self.theme_toggle_btn.setText(f"主题: {'暗色' if new_is_dark else '亮色'}")

        # Update background recording button if active
        if self.background_recording_active:
            self.bg_record_btn.setStyleSheet(f"background-color: {COLOR_ACCENT}; color: #000; border: none;")
            self.feedback_label.setStyleSheet(f"background-color: {COLOR_PANEL}; color: {COLOR_ACCENT}; border-left: 4px solid {COLOR_ACCENT};")
        else:
            self.bg_record_btn.setStyleSheet(f"border: 1px dashed {COLOR_ACCENT}; color: {COLOR_ACCENT};")

    @pyqtSlot(float, float)
    def update_dashboard_ui(self, diff_ms, percentage):
        abs_diff = abs(diff_ms)
        val_color = "#00e676" if abs_diff <= 10 else "#ff5252"
        text = (
            f"<div style='line-height:1.4;'>"
            f"<span style='font-size:12px; color:{COLOR_TEXT_SUB};'>急停误差</span><br>"
            f"<span style='font-size:24px; font-weight:bold; color:{val_color}; font-family:Consolas;'>{abs_diff:.1f} <span style='font-size:14px;'>ms</span></span>"
            f"<br><br>"
            f"<span style='font-size:12px; color:{COLOR_TEXT_SUB};'>占反应时间</span><br>"
            f"<span style='font-size:24px; font-weight:bold; color:{COLOR_ACCENT}; font-family:Consolas;'>{percentage:.1f}<span style='font-size:14px;'>%</span></span>"
            f"</div>"
        )
        self.impact_label.setText(text)

    @pyqtSlot(str, QColor)
    def update_feedback(self, text, color):
        self.feedback_label.setText(text)
        self.feedback_label.setStyleSheet(f"background-color: {COLOR_PANEL}; color: {color.name()}; border-left: 4px solid {color.name()};")

    @pyqtSlot(str, object, float, dict, QColor)
    def update_history(self, k_type, t, diff, detail, color):
        if isinstance(detail, dict) and detail:
            item = QListWidgetItem(self.format_history_item_text(detail))
            detail['history_item'] = item
        else:
            ms = diff * 1000
            if isinstance(t, datetime.datetime):
                time_str = t.strftime("%H:%M:%S.%f")[:-3]
            else:
                time_str = datetime.datetime.fromtimestamp(t).strftime("%H:%M:%S.%f")[:-3]
            item = QListWidgetItem(f"[{k_type}] {time_str} │ {ms:+.1f}ms")
        item.setForeground(QBrush(color))
        self.history_list.addItem(item); self.history_list.scrollToBottom()

    def format_history_item_text(self, entry):
        time_str = entry['wall_time'].strftime("%H:%M:%S.%f")[:-3]
        ms = entry['time_diff'] * 1000
        return f"[{entry['key_type']} {entry['transition']} {self.format_shot_tag(entry)}] {time_str} │ {ms:+.1f}ms"

    def format_shot_tag(self, entry):
        shot_type = entry.get('shot_type', 'No shot')
        if shot_type != "Shot":
            return shot_type
        delay = entry.get('shot_delay_ms')
        return "Shot" if delay is None else f"Shot L:{delay:+.0f}ms"

    @pyqtSlot(str, bool)
    def update_key_state_display(self, key, pressed):
        if key in self.key_widgets: self.key_widgets[key].set_active(pressed)

    def update_plots_efficiently(self):
        self._update_single_figure(self.ad_data, self.ax_ad_line, self.ax_ad_box, self.ad_canvas)
        self._update_single_figure(self.ws_data, self.ax_ws_line, self.ax_ws_box, self.ws_canvas)

    def update_direction_analysis(self):
        records = list(self.ad_data) + list(self.ws_data)
        sections = {}
        for transition in ['A->D', 'D->A', 'W->S', 'S->W']:
            transition_records = [record for record in records if record.get('transition') == transition]
            sections[transition] = self.format_direction_section(transition, transition_records)

        self.direction_analysis_view.setHtml(f"""
        <style>
            body {{
                background: {COLOR_BG};
                color: {COLOR_TEXT_MAIN};
                font-family: "Microsoft YaHei UI";
                font-size: 12px;
            }}
            .card {{
                background: {COLOR_PANEL};
                border: 1px solid {COLOR_BORDER};
                border-radius: 6px;
                padding: 9px;
                margin-bottom: 8px;
            }}
            .title {{
                color: {COLOR_ACCENT};
                font-size: 15px;
                font-weight: bold;
                margin-bottom: 6px;
            }}
            .empty {{
                color: {COLOR_TEXT_SUB};
                line-height: 1.6;
            }}
            .label {{
                color: {COLOR_TEXT_SUB};
            }}
            .value {{
                color: {COLOR_TEXT_MAIN};
                font-family: Consolas;
                font-weight: bold;
            }}
            .grade {{
                font-size: 20px;
                font-weight: bold;
                font-family: Consolas;
            }}
        </style>
        <table width="100%" cellspacing="8" cellpadding="0">
            <tr>
                <td width="50%" valign="top">{sections['A->D']}</td>
                <td width="50%" valign="top">{sections['D->A']}</td>
            </tr>
            <tr>
                <td width="50%" valign="top">{sections['W->S']}</td>
                <td width="50%" valign="top">{sections['S->W']}</td>
            </tr>
        </table>
        """)

    def format_direction_section(self, transition, records):
        title = transition.replace("->", "")
        if not records:
            return f"""
            <div class="card">
                <div class="title">{title} <span style="color:{COLOR_TEXT_SUB}; font-size:11px;">({transition})</span></div>
                <div class="empty">暂无有效样本</div>
            </div>
            """

        values = [record['time_diff'] * 1000 for record in records]
        abs_values = [abs(value) for value in values]
        count = len(values)
        avg_abs = statistics.mean(abs_values)
        avg_raw = statistics.mean(values)
        stdev = statistics.stdev(abs_values) if count > 1 else 0.0
        best = min(abs_values)
        worst = max(abs_values)
        grade, grade_color = self.get_accuracy_grade(avg_abs, stdev)
        bias = "偏慢" if avg_raw > 5 else "偏快" if avg_raw < -5 else "均衡"
        bias_color = self.get_color(avg_raw).name()
        shot_count = sum(1 for record in records if record.get('shot_type') == "Shot")
        spray_count = sum(1 for record in records if record.get('shot_type') == "Spray")
        no_shot_count = sum(1 for record in records if record.get('shot_type') == "No shot")
        shot_delays = [
            record['shot_delay_ms']
            for record in records
            if record.get('shot_type') == "Shot" and record.get('shot_delay_ms') is not None
        ]
        if shot_delays:
            avg_shot_delay = statistics.mean(shot_delays)
            ideal_count = sum(1 for delay in shot_delays if 40 <= delay <= 90)
            ideal_pct = ideal_count / len(shot_delays) * 100
            shot_timing_html = (
                f"<span class=\"value\">"
                f"{avg_shot_delay:+.0f} ms / 合理 {ideal_count}/{len(shot_delays)} ({ideal_pct:.0f}%)"
                f"</span>"
            )
        else:
            shot_timing_html = f"<span class=\"value\" style=\"color:{COLOR_TEXT_SUB};\">暂无 Shot 时机</span>"

        return f"""
        <div class="card">
            <div class="title">{title} <span style="color:{COLOR_TEXT_SUB}; font-size:11px;">({transition})</span></div>
            <div><span class="label">评级</span> <span class="grade" style="color:{grade_color};">{grade}</span></div>
            <div><span class="label">样本</span> <span class="value">{count}</span></div>
            <div><span class="label">平均误差</span> <span class="value">{avg_abs:.1f} ms</span></div>
            <div><span class="label">平均偏向</span> <span class="value" style="color:{bias_color};">{avg_raw:+.1f} ms ({bias})</span></div>
            <div><span class="label">稳定性</span> <span class="value">{stdev:.1f}</span></div>
            <div><span class="label">最佳/最差</span> <span class="value">{best:.1f} / {worst:.1f} ms</span></div>
            <div><span class="label">射击分组</span> <span class="value">Shot {shot_count} / Spray {spray_count} / <span style="color:{COLOR_NO_SHOT};">No shot {no_shot_count}</span></span></div>
            <div><span class="label">左键时机</span> {shot_timing_html}</div>
        </div>
        """

    def get_accuracy_grade(self, avg_abs, stdev):
        if avg_abs <= 10 and stdev <= 5:
            return "S", COLOR_SUCCESS
        if avg_abs <= 20:
            return "A", COLOR_ACCENT
        if avg_abs <= 40:
            return "B", COLOR_WARNING
        return "C", COLOR_DANGER

    def _update_single_figure(self, data_deque, ax_line, ax_box, canvas):
        if not data_deque:
            ax_line.clear(); self.setup_axes_style(ax_line)
            ax_box.clear(); self.setup_axes_style(ax_box)
            canvas.draw_idle()
            return
        y = [d['time_diff'] * 1000 for d in list(data_deque)[-self.record_count:]]
        x = range(1, len(y) + 1)
        ax_line.clear(); self.setup_axes_style(ax_line)
        records = list(data_deque)[-self.record_count:]
        ax_line.scatter(x, y, c=[self.get_record_color(record).name() for record in records], s=50, alpha=0.9)
        if y: ax_line.axhline(statistics.mean(y), color=COLOR_ACCENT, linestyle='--', alpha=0.5)
        ax_box.clear(); self.setup_axes_style(ax_box)
        if len(y) >= 5:
            ax_box.boxplot(y, vert=False, patch_artist=True, boxprops=dict(facecolor=COLOR_ACCENT, alpha=0.2))
            ax_box.set_yticks([])
        canvas.draw_idle()

    def get_color(self, ms):
        """Return a high-contrast color based solely on strafe timing error.

        Dark theme  → bright / neon colors against black.
        Light theme → dark / saturated colors against white.
        """
        val = abs(ms)
        if _IS_DARK:
            if val <= 5:       return QColor("#00ff88")   # bright green  — perfect
            if ms < 0:
                if val <= 20:  return QColor("#40c4ff")   # sky blue      — slightly fast
                if val <= 50:  return QColor("#b388ff")   # soft purple   — moderately fast
                return QColor("#ea80fc")                   # pink          — very fast
            if val <= 20:      return QColor("#ffea00")   # bright yellow — slightly slow
            if val <= 50:      return QColor("#ff9100")   # orange        — moderately slow
            return QColor("#ff5252")                       # red           — very slow
        else:
            if val <= 5:       return QColor("#008a00")   # dark green    — perfect
            if ms < 0:
                if val <= 20:  return QColor("#01579b")   # dark blue     — slightly fast
                if val <= 50:  return QColor("#4527a0")   # dark purple   — moderately fast
                return QColor("#880e4f")                   # dark magenta  — very fast
            if val <= 20:      return QColor("#e65100")   # dark amber    — slightly slow
            if val <= 50:      return QColor("#bf360c")   # dark orange   — moderately slow
            return QColor("#b71c1c")                       # dark red      — very slow

    def get_record_color(self, record):
        if record.get('shot_type') == "No shot":
            return QColor(COLOR_NO_SHOT)
        return self.get_color(record['time_diff'] * 1000)

    def get_shot_timing_color(self, delay_ms):
        """Deprecated: left-click timing is no longer color-highlighted.
        Returns a neutral color so callers still compile."""
        return QColor(COLOR_TEXT_SUB)

    def get_shot_timing_background(self, record):
        """Left-click timing no longer adds background tint — always transparent."""
        return QColor(0, 0, 0, 0)

    @pyqtSlot(str, int)
    def start_timer(self, k, i): self.timers[k].start(i)

    @pyqtSlot(str)
    def stop_timer(self, k): self.timers[k].stop()

    def reset_quick_stop(self, k):
        if k in self.waiting_for_opposite_key: del self.waiting_for_opposite_key[k]

    def refresh(self):
        self.ad_data.clear(); self.ws_data.clear(); self.background_buffer.clear()
        self.pending_shot_events.clear()
        self.waiting_for_opposite_key.clear()
        self.last_record_time = 0
        for timer in self.timers.values():
            timer.stop()
        for state in self.key_state.values():
            state['pressed'] = False
            state['time'] = None
        for key_widget in self.key_widgets.values():
            key_widget.set_active(False)

        self.history_list.clear(); self.output_list.clear()
        self.feedback_label.setText("数据已重置")
        self.feedback_label.setStyleSheet(f"""
            background-color: {COLOR_PANEL};
            color: {COLOR_TEXT_SUB};
            border-radius: 4px;
            border-left: 4px solid {COLOR_BORDER};
        """)
        self.impact_label.setText(f"<span style='color:{COLOR_TEXT_SUB}; font-size:14px;'>等待操作数据...</span>")
        self.update_plots_efficiently()
        self.update_direction_analysis()

    def append_log(self, msg):
        self.output_list.addItem(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}")
        self.output_list.scrollToBottom()

    def set_record_count(self):
        dlg = OptionDialog("显示点数", ["10", "20", "50", "100", "200"], self)
        if dlg.exec_() == QDialog.Accepted:
            self.record_count = int(dlg.get_selected_option())
            self.record_count_button.setText(f"显示: {self.record_count}")
            self.update_plots_efficiently()

    def set_filter_threshold(self):
        dlg = OptionDialog("过滤阈值", ["50ms", "100ms", "120ms", "150ms", "200ms"], self)
        if dlg.exec_() == QDialog.Accepted:
            self.filter_threshold = int(dlg.get_selected_option().replace("ms",""))
            self.filter_threshold_button.setText(f"阈值: {self.filter_threshold}ms")

    def set_shot_detection_window(self):
        dlg = ModernDialog("射击窗口", self)
        layout = QVBoxLayout(dlg)

        hint = QLabel("急停后左键按下仍归类为 Shot 的最大滞后时间")
        hint.setStyleSheet(f"color: {COLOR_TEXT_SUB}; margin-bottom: 8px;")
        layout.addWidget(hint)

        spin = QDoubleSpinBox()
        spin.setRange(50, 1000)
        spin.setDecimals(0)
        spin.setSingleStep(10)
        spin.setValue(self.shot_detection_window * 1000)
        spin.setSuffix(" ms")
        layout.addWidget(spin)

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(dlg.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(dlg.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        if dlg.exec_() == QDialog.Accepted:
            selected_ms = int(spin.value())
            self.shot_detection_window = selected_ms / 1000.0
            self.shot_window_button.setText(f"射击窗口: {selected_ms}ms")

    def show_key_mapping_dialog(self):
        dlg = KeyMappingDialog(self.key_mappings, self)
        if dlg.exec_() == QDialog.Accepted:
            self.key_mappings = dlg.get_mappings(); self.reverse_key_mappings = {v: k for k, v in self.key_mappings.items()}

    def show_principle_dialog(self): PrinciplesDialog(self).exec_()

    def closeEvent(self, event):
        if self.background_recording_active:
            reply = QMessageBox.warning(
                self, "后台记录进行中",
                "后台记录正在运行，关闭窗口将丢失所有未保存的记录数据。\n确定要退出吗？",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.No:
                event.ignore()
                return
        if hasattr(self, 'listener'):
            self.listener.stop()
            self.listener.join(timeout=1.0)
        if hasattr(self, 'mouse_listener'):
            self.mouse_listener.stop()
            self.mouse_listener.join(timeout=1.0)
        super().closeEvent(event)

if __name__ == "__main__":
    if hasattr(Qt, 'AA_EnableHighDpiScaling'): QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
