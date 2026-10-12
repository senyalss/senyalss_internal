import sys
import json
import os
import threading
import keyboard
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QPixmap, QPainter, QBrush, QPen, QIcon
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QLineEdit,
                             QTextEdit, QFrame, QGraphicsDropShadowEffect)

CONFIG_FILE = "config.json"

ASCII_LOGO = """
==================================================
  ___ _____ _   ___   _  _   _   _    ___ ___ 
 / __| ____| \ | \ \ / //_\ | | | |  / __/ __|
 \__ \  _| |  \| |\ V // _ \| |_| |__\__ \__ \\

 |___/___|_|_|\_| |_/_/_\_\_\___/____|___/___/
              INTERNAL KEY CUSTOMIZER
==================================================
 Данное приложение разрабатывалось с участием нейросети Gemini
 // Инициализация ядра... Успешно.
 // Ожидание загрузки правил конфигурации...
"""


class GameCustomizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.hue = 0
        self.is_active = False
        self.setWindowTitle("senyalss internal")
        self.setFixedSize(840, 500)

        self.setStyleSheet("""
            QMainWindow { background-color: #030303; }
            QFrame#Card { background-color: #08080a; border: 1px solid #121214; border-radius: 8px; }
            QLabel { color: #ffffff; font-family: 'Segoe UI', 'Impact', sans-serif; font-size: 11px; letter-spacing: 2px; font-weight: 800; }
            QLineEdit { 
                background-color: #030303; 
                color: #ffffff; 
                border: 1px solid #16161a; 
                border-radius: 4px; 
                padding: 11px; 
                font-size: 13px; 
                font-family: 'Consolas', monospace; 
            }
            QLineEdit:focus { border: 1px solid #444455; color: #45f3ff; }
            QTextEdit { 
                background-color: #030303; 
                color: #00ff66; 
                border: 1px solid #16161a; 
                border-radius: 4px; 
                padding: 12px; 
                font-size: 12px; 
                font-family: 'Consolas', 'Courier New', monospace; 
            }
            QPushButton#MenuBtn { background-color: transparent; color: #44444a; border: none; font-weight: 900; font-size: 12px; font-family: 'Segoe UI', sans-serif; letter-spacing: 2px; }
            QPushButton#MenuBtn:hover { color: #ffffff; }
            QPushButton#ActionBtn { 
                background-color: #0d0d11; 
                color: #ffffff; 
                border: 1px solid #1c1c22; 
                border-radius: 4px; 
                padding: 10px; 
                font-weight: 800; 
                font-size: 11px; 
                font-family: 'Segoe UI', sans-serif;
                letter-spacing: 1px;
            }
            QPushButton#ActionBtn:hover { background-color: #16161f; border: 1px solid #2d2d3d; color: #45f3ff; }
        """)

        self.remap_rules = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    self.remap_rules = json.load(f)
            except:
                pass

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        window_layout = QVBoxLayout(main_widget)
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.setSpacing(0)

        self.rgb_line = QFrame()
        self.rgb_line.setFixedHeight(3)
        window_layout.addWidget(self.rgb_line)

        header = QWidget()
        header.setStyleSheet("background-color: #060608; border-bottom: 1px solid #0d0d0f;")
        header.setFixedHeight(55)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(30, 0, 30, 0)

        # Вернули фирменный жирный стиль текста в шапку меню
        logo_lbl = QLabel("senyalss internal")
        logo_lbl.setStyleSheet("color: #ffffff; font-size: 13px; font-weight: 900; letter-spacing: 3px;")
        header_layout.addWidget(logo_lbl)
        header_layout.addStretch()

        self.tab_remap = QPushButton("CORE_REMAP")
        self.tab_remap.setObjectName("MenuBtn")
        self.tab_remap.setStyleSheet("color: #ffffff;")
        self.tab_remap_line = QFrame()
        self.tab_remap_line.setFixedHeight(2)

        t1_layout = QVBoxLayout()
        t1_layout.addWidget(self.tab_remap)
        t1_layout.addWidget(self.tab_remap_line)
        header_layout.addLayout(t1_layout)
        window_layout.addWidget(header)

        content_area = QWidget()
        content_layout = QHBoxLayout(content_area)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(25)
        window_layout.addWidget(content_area)

        left_card = QFrame()
        left_card.setObjectName("Card")
        left_layout = QVBoxLayout(left_card)
        left_layout.setContentsMargins(20, 20, 20, 20)

        lbl = QLabel("[ CONTROL_PANEL ]")
        lbl.setStyleSheet("color: #4c4c54;")
        left_layout.addWidget(lbl)
        left_layout.addSpacing(20)

        self.input_key = QLineEdit()
        self.input_key.setPlaceholderText("Исходная клавиша (напр. caps lock)")
        self.input_target = QLineEdit()
        self.input_target.setPlaceholderText("Новое действие (напр. backspace)")

        left_layout.addWidget(self.input_key)
        left_layout.addSpacing(12)
        left_layout.addWidget(self.input_target)
        left_layout.addSpacing(20)

        self.btn_add = QPushButton("ДОБАВИТЬ МАКРОС")
        self.btn_add.setObjectName("ActionBtn")
        self.btn_add.clicked.connect(self.add_rule_logic)
        left_layout.addWidget(self.btn_add)
        left_layout.addStretch()

        self.btn_activate = QPushButton("LAUNCH SYSTEM")
        self.btn_activate.setMinimumHeight(45)
        self.btn_activate.setFont(QFont('Segoe UI', 11, QFont.Weight.ExtraBold))
        self.btn_activate.clicked.connect(self.toggle_system_logic)

        self.glow = QGraphicsDropShadowEffect()
        self.glow.setBlurRadius(20)
        self.glow.setOffset(0, 0)
        self.btn_activate.setGraphicsEffect(self.glow)
        left_layout.addWidget(self.btn_activate)

        right_card = QFrame()
        right_card.setObjectName("Card")
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(20, 20, 20, 20)

        lbl2 = QLabel("[ CORE_LOGS ]")
        lbl2.setStyleSheet("color: #4c4c54;")
        right_layout.addWidget(lbl2)
        right_layout.addSpacing(20)

        self.rules_display = QTextEdit()
        self.rules_display.setReadOnly(True)

        if not self.remap_rules:
            self.rules_display.setText(ASCII_LOGO)
        else:
            self.update_logs_display()

        right_layout.addWidget(self.rules_display)
        content_layout.addWidget(left_card, stretch=4)
        content_layout.addWidget(right_card, stretch=5)

        rgb_timer = QTimer(self)
        rgb_timer.timeout.connect(self.update_rgb_effects)
        rgb_timer.start(25)

    def update_logs_display(self):
        t = ASCII_LOGO + "\n // Обнаружены сохраненные хуки:\n"
        for key, val in self.remap_rules.items():
            t += f" [>] hook_active: {key.upper()} -> {val.upper()}\n"
        self.rules_display.setText(t)

    def add_rule_logic(self):
        k = self.input_key.text().strip().lower()
        v = self.input_target.text().strip().lower()
        if k and v:
            self.remap_rules[k] = v
            with open(CONFIG_FILE, "w") as f: json.dump(self.remap_rules, f, indent=4)
            self.input_key.clear()
            self.input_target.clear()
            self.update_logs_display()

    def toggle_system_logic(self):
        if not self.is_active:
            self.is_active = True
            self.btn_activate.setText("SYSTEM INJECTED")
            self.btn_activate.setStyleSheet(
                "background-color: #00ff66; color: #000000; border: none; border-radius: 4px;")
            self.glow.setColor(QColor(0, 255, 102))
            self.rules_display.setText(
                self.rules_display.toPlainText() + "\n // [SUCCESS] Перехват клавиш успешно активирован!")

            def hook():
                for key, target in self.remap_rules.items(): keyboard.remap_key(key, target)
                keyboard.wait()

            threading.Thread(target=hook, daemon=True).start()
        else:
            self.is_active = False
            keyboard.unhook_all()
            self.btn_activate.setText("LAUNCH SYSTEM")
            self.update_logs_display()

    def update_rgb_effects(self):
        self.hue = (self.hue + 1) % 360
        color = QColor.fromHsv(self.hue, 180, 255)
        c1 = QColor.fromHsv(self.hue, 180, 255).name()
        c2 = QColor.fromHsv((self.hue + 60) % 360, 180, 255).name()
        grad = f"border: none; background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {c1}, stop:1 {c2});"

        self.rgb_line.setStyleSheet(grad)
        self.tab_remap_line.setStyleSheet(grad)

        # Динамически перерисовываем иконку для окна Windows и панели задач
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(Qt.GlobalColor.transparent))
        painter.drawEllipse(2, 2, 28, 28)
        painter.setBrush(QBrush(QColor("#030303")))
        painter.drawEllipse(9, 9, 14, 14)
        painter.end()

        # Применяем RGB-иконку к окну ОС
        self.setWindowIcon(QIcon(pixmap))

        if not self.is_active:
            self.btn_activate.setStyleSheet(f"color: #ffffff; border-radius: 4px; {grad}")
            self.glow.setColor(color)


if True:
    app = QApplication(sys.argv)
    window = GameCustomizer()
    window.show()
    sys.exit(app.exec())
