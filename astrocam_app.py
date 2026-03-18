#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from datetime import datetime
from pathlib import Path
import subprocess

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QSlider, QCheckBox, QMessageBox,
    QComboBox
)
from PyQt5.QtCore import Qt

from picamera2 import Picamera2
from picamera2.previews.qt import QGlPicamera2


# ============================================================
# CONFIG WINDOW (Before Starting Stream)
# ============================================================

class ConfigWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Astro Camera Setup")
        self.resize(400, 300)

        layout = QVBoxLayout()

        # Preview resolution
        layout.addWidget(QLabel("Preview Resolution"))
        self.preview_combo = QComboBox()
        self.preview_combo.addItems([
            "640x480",
            "800x480",
            "1280x720",
            "1640x1232"
        ])
        layout.addWidget(self.preview_combo)

        # Capture resolution
        layout.addWidget(QLabel("Capture Resolution"))
        self.capture_combo = QComboBox()
        self.capture_combo.addItems([
            "1640x1232",
            "3280x2464"
        ])
        layout.addWidget(self.capture_combo)

        # FPS
        layout.addWidget(QLabel("Preview FPS"))
        self.fps_combo = QComboBox()
        self.fps_combo.addItems(["30", "60"])
        layout.addWidget(self.fps_combo)

        start_btn = QPushButton("Start Session")
        start_btn.clicked.connect(self.start_session)
        layout.addWidget(start_btn)

        self.setLayout(layout)

    def start_session(self):
        self.preview_res = tuple(map(int, self.preview_combo.currentText().split("x")))
        self.capture_res = tuple(map(int, self.capture_combo.currentText().split("x")))
        self.fps = int(self.fps_combo.currentText())

        self.main = AstroApp(self.preview_res,
                             self.capture_res,
                             self.fps)
        self.main.show()
        self.close()


# ============================================================
# MAIN ASTRO APPLICATION
# ============================================================

class AstroApp(QWidget):

    def __init__(self, preview_res, capture_res, fps):
        super().__init__()

        self.preview_res = preview_res
        self.capture_res = capture_res
        self.fps = fps

        self.setWindowTitle("OpenGL Astro Camera")
        self.resize(400, 700)

        # Create folders
        base = Path.home() / "astro_captures"
        self.lights_dir = base / "lights"
        self.darks_dir = base / "darks"
        self.flats_dir = base / "flats"
        for d in [self.lights_dir, self.darks_dir, self.flats_dir]:
            d.mkdir(parents=True, exist_ok=True)

        self.build_ui()
        self.start_preview()

    # =========================================================
    # UI
    # =========================================================

    def build_ui(self):

        layout = QVBoxLayout()

        # RAW
        self.raw_check = QCheckBox("Capture RAW (DNG)")
        self.raw_check.setChecked(True)
        layout.addWidget(self.raw_check)

        # Burst
        self.burst_check = QCheckBox("Burst Mode")
        layout.addWidget(self.burst_check)

        layout.addWidget(QLabel("Burst Count"))
        self.burst_slider = QSlider(Qt.Horizontal)
        self.burst_slider.setMinimum(1)
        self.burst_slider.setMaximum(30)
        self.burst_slider.setValue(5)
        self.burst_slider.valueChanged.connect(self.update_burst_label)
        layout.addWidget(self.burst_slider)

        self.burst_label = QLabel("Will capture: 5")
        layout.addWidget(self.burst_label)

        # Exposure
        layout.addWidget(QLabel("Exposure (1/X seconds)"))
        self.exp_slider = QSlider(Qt.Horizontal)
        self.exp_slider.setMinimum(5)    # 1/5s
        self.exp_slider.setMaximum(100)  # 1/100s
        self.exp_slider.setValue(10)
        self.exp_slider.valueChanged.connect(self.update_exposure_label)
        layout.addWidget(self.exp_slider)

        self.exp_label = QLabel("Exposure: 1/10 s")
        layout.addWidget(self.exp_label)

        # ISO
        layout.addWidget(QLabel("ISO"))
        self.iso_slider = QSlider(Qt.Horizontal)
        self.iso_slider.setMinimum(100)
        self.iso_slider.setMaximum(1600)
        self.iso_slider.setValue(100)
        self.iso_slider.valueChanged.connect(self.update_iso_label)
        layout.addWidget(self.iso_slider)

        self.iso_label = QLabel("ISO: 100")
        layout.addWidget(self.iso_label)

        # Preview Brightness
        layout.addWidget(QLabel("Preview Brightness (Display Only)"))
        self.preview_brightness_slider = QSlider(Qt.Horizontal)
        self.preview_brightness_slider.setMinimum(-100)
        self.preview_brightness_slider.setMaximum(100)
        self.preview_brightness_slider.setValue(0)
        self.preview_brightness_slider.valueChanged.connect(
            self.update_preview_brightness
        )
        layout.addWidget(self.preview_brightness_slider)

        self.preview_brightness_label = QLabel("Preview Brightness: 0")
        layout.addWidget(self.preview_brightness_label)

        # Capture buttons
        btn_l = QPushButton("Capture Lights")
        btn_l.clicked.connect(lambda: self.capture(self.lights_dir))
        layout.addWidget(btn_l)

        btn_d = QPushButton("Capture Darks")
        btn_d.clicked.connect(lambda: self.capture(self.darks_dir))
        layout.addWidget(btn_d)

        btn_f = QPushButton("Capture Flats")
        btn_f.clicked.connect(lambda: self.capture(self.flats_dir))
        layout.addWidget(btn_f)

        self.setLayout(layout)

    # =========================================================
    # UI Update Functions
    # =========================================================

    def update_burst_label(self):
        self.burst_label.setText(
            f"Will capture: {self.burst_slider.value()}"
        )

    def update_exposure_label(self):
        denom = self.exp_slider.value()
        self.exp_label.setText(f"Exposure: 1/{denom} s")

    def update_iso_label(self):
        val = self.iso_slider.value()
        self.iso_label.setText(f"ISO: {val}")

    def update_preview_brightness(self):
        val = self.preview_brightness_slider.value()
        self.preview_brightness_label.setText(
            f"Preview Brightness: {val}"
        )

        if hasattr(self, "picam2") and self.picam2:
            self.picam2.set_controls({
                "Brightness": val / 100.0
            })

    # =========================================================
    # PREVIEW CONTROL
    # =========================================================

    def start_preview(self):
        self.picam2 = Picamera2()

        config = self.picam2.create_preview_configuration(
            main={"size": self.preview_res},
            controls={"FrameRate": self.fps}
        )

        self.picam2.configure(config)

        self.preview = QGlPicamera2(self.picam2)
        self.preview.show()

        self.picam2.start()

    def stop_preview(self):
        if hasattr(self, "preview") and self.preview:
            self.preview.close()

        if hasattr(self, "picam2") and self.picam2:
            self.picam2.stop()
            self.picam2.close()

    # =========================================================
    # CAPTURE (ISO + SHUTTER FIXED)
    # =========================================================

    def capture(self, directory):

        count = self.burst_slider.value() if self.burst_check.isChecked() else 1

        denom = self.exp_slider.value()
        exposure_us = int(1_000_000 / denom)

        iso_value = self.iso_slider.value()
        analogue_gain = iso_value / 100.0

        self.stop_preview()

        cam = Picamera2()

        if self.raw_check.isChecked():
            config = cam.create_still_configuration(
                main={"size": self.capture_res},
                raw={}
            )
        else:
            config = cam.create_still_configuration(
                main={"size": self.capture_res}
            )

        cam.configure(config)

        # Apply manual exposure + ISO
        cam.set_controls({
            "AeEnable": False,
            "AwbEnable": False,
            "ExposureTime": exposure_us,
            "AnalogueGain": analogue_gain
        })

        cam.start()

        for i in range(count):

            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            suffix = f"_B{i+1:02d}" if count > 1 else ""

            if self.raw_check.isChecked():
                cam.capture_file(str(directory / f"{ts}{suffix}.dng"),
                                 name="raw")
            else:
                cam.capture_file(str(directory / f"{ts}{suffix}.jpg"))

        cam.stop()
        cam.close()

        self.start_preview()

        QMessageBox.information(
            self,
            "Done",
            f"Captured {count} frame(s)"
        )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConfigWindow()
    window.show()
    sys.exit(app.exec_())
