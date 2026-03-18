# 🌌 Raspberry Pi OpenGL Astro Camera

A lightweight astrophotography application for the Raspberry Pi using the IMX219 (Pi NoIR) sensor.

This project focuses on **direct sensor-based image capture with full manual control**, enabling astrophotography workflows on extremely low-cost hardware.

It serves as a **budget alternative to dedicated astrophotography cameras**, while still producing usable results when combined with proper techniques like stacking and calibration.

---

## 🔬 Overview

This application captures images **directly from the camera sensor (RAW/DNG)** instead of relying on compressed outputs.  
Even though the IMX219 sensor is small, careful capture + stacking allows you to extract meaningful astronomical detail.

The app is designed for:

- Deep-sky beginners
- DIY telescope setups
- Low-cost astro rigs
- Headless Raspberry Pi systems (VNC)

---

## 🚀 Features

### 🎥 OpenGL Preview
- Hardware-accelerated preview using OpenGL
- Smooth performance over VNC
- Adjustable preview resolution and FPS
- Optimized for Raspberry Pi 3B

---

### 📷 RAW (DNG) Capture
- True sensor data capture (no compression loss)
- Uses Picamera2 raw pipeline
- Ideal for stacking workflows

---

### ⚙️ Manual Camera Control
- Exposure control in **1/X seconds**
- ISO (analogue gain) adjustment
- Auto-exposure disabled during capture for consistency

---

### 🔁 Burst Mode
- Capture multiple frames in sequence
- Automatic filename indexing
- Works with both RAW (DNG) and JPEG

---

### 🌗 Calibration Frames
Dedicated capture modes for:
- Lights
- Darks
- Flats

Images are automatically organized into folders.

---

### 🎛️ Preview-Only Adjustments
- Adjustable preview brightness
- Helps with focusing on faint objects
- Does **not affect captured images**

---

### 🖥️ OpenGL-Based UI
- No Tkinter
- Fully Qt + OpenGL interface
- Startup configuration window for:
  - Preview resolution
  - Capture resolution
  - FPS

---

## ⚙️ Requirements

### Python Packages

picamera2
PyQt5
numpy


### System Dependencies (Raspberry Pi)

sudo apt update
sudo apt install -y
python3-picamera2
python3-pyqt5
libatlas-base-dev
libopenjp2-7


---
OS : BOOKWORM - (DOWN/UP)GRADE FOR NO ISSUES
## ▶️ Usage

Run the application:


python3 main.py


### Startup Configuration
Before the preview starts, you can select:
- Preview resolution (for smooth viewing)
- Capture resolution (for final images)
- FPS

---

### Capture Workflow

1. Adjust:
   - Exposure (1/X seconds)
   - ISO
   - Preview brightness (for visibility only)

2. Select mode:
   - Lights / Darks / Flats

3. (Optional) Enable Burst Mode

4. Capture images

---

## ❄️ Cooling Recommendation

For better results, **cooling the sensor is highly recommended**.

Higher temperatures introduce noise, especially in:
- Long exposures
- High ISO captures

Even simple cooling helps:
- Heatsinks
- Small fans

---

## 💸 Why This Project?

Astrophotography cameras are expensive.

This project provides a **very low-cost alternative** using:
- Raspberry Pi
- Pi NoIR camera (IMX219)

While it won't match dedicated cooled astro cameras, it can still produce **decent results** with:
- Calibration frames
- Image stacking

---

## 🔮 Future Improvements

Planned features:

- 🎬 Video capture (planetary imaging)
- 🧠 Real-time stacking during capture
- 📊 Histogram tools
- 🔍 Focus assist / zoom window
- 🌡️ Temperature-aware capture

---

## ⚠️ Notes

- Designed for Raspberry Pi (low resource environment)
- Optimized for stability over heavy processing
- Best used with stacking software:
  - DeepSkyStacker
  - Siril

---


## 📸 Example Results
![MosaicStackDNGs (Large)](https://github.com/user-attachments/assets/9b21a63e-f149-4fe1-9557-7b2327c80588)
(img compressed - full results are even better!)
