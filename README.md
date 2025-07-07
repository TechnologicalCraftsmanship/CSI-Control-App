# CSI Data Acquisition System

This repository contains the software components for a **Channel State Information (CSI) Data Acquisition System**. The system is designed to capture real-time CSI data from a Wi-Fi network using an ESP32 device and store it for analysis. It provides both a desktop and a mobile application for intuitive control and data management.

## Overview

The system is composed of three primary components that work in synergy:

1.  **ESP32 Receiver Node (Firmware):** The embedded software running on an ESP32 microcontroller, responsible for Wi-Fi connectivity, traffic generation, CSI extraction, and data transmission.
2.  **CSI Collector Desktop Application (`csicollector.py`):** A Python-based desktop application (built with Flet) that serves as a robust control station for configuring the ESP32, initiating/terminating data collection sessions, and saving received CSI data.
3.  **CSI Collector Mobile Application (Android):** A native Android application that offers a portable and convenient way to perform the same provisioning and data collection tasks as the desktop application, directly from your Android device.

## System Components

### 1. ESP32 Receiver Node Firmware

The firmware is the core of the data collection process, flashed onto an ESP32 device. Its key functionalities include:

* **Provisioning Mode:** Upon first power-on or after a factory reset, the ESP32 creates a temporary Wi-Fi Access Point named `ESP_PROV`. In this mode, it listens for network credentials sent from either the Desktop or Mobile Collector Application.
* **Flexible Connectivity:** Capable of connecting to various network types, including open networks, WPA2-PSK (Personal), and WPA2-Enterprise (PEAP), making it suitable for diverse environments like universities and corporations.
* **Traffic Generation:** Once connected to the main network, it generates the necessary Wi-Fi traffic for CSI measurement by sending ping packets to the network router (gateway).
* **Data Transmission:** It captures the CSI data from the ping responses and streams it in real-time via UDP to the host device (running either the desktop or mobile collector application).
* **Power Management:** To conserve energy, the ESP32 enters a deep sleep cycle between measurement sessions, waking only to listen for new commands.
* **Factory Reset:** Allows the user to erase all stored network configurations by holding the "BOOT" button on the ESP32 during startup.

### 2. CSI Collector Desktop Application (`csicollector.py`)

This Python application, built using the Flet framework, provides a cross-platform graphical user interface for managing the CSI acquisition process.

**Key Features:**

* **Graphical User Interface:** An intuitive visual environment for system control.
* **Provisioning Wizard:** Guides the user through sending Wi-Fi network credentials to a new ESP32.
* **Device Discovery:** Automatically searches for and finds the IP address of the ESP32 on the local network.
* **Acquisition Control:** Allows users to define parameters such as measurement duration and associate data with experimental scenarios.
* **Real-time Console:** Displays incoming CSI data in real-time as it's received from the ESP32.
* **Data Storage:** Saves all collected CSI data sessions into a single, organized SQLite database file, including important metadata like the scenario and timestamp.

### 3. CSI Collector Mobile Application (Android)

The Android application offers the same core functionalities as its desktop counterpart, providing flexibility for on-the-go data collection.

**Key Features:**

* **Mobile Provisioning:** Connects to the ESP32's provisioning network and sends primary Wi-Fi credentials.
* **Local IP Detection:** Automatically detects the mobile device's local IP address for server configuration.
* **Acquisition Control:** Configures measurement duration and experimental scenarios.
* **Data Reception:** Listens for and receives CSI data streams from the provisioned ESP32.
* **Local Data Storage:** Saves collected data directly to a SQLite database file on the Android device's storage.

---

## Unified User Manual

This manual outlines the two main operational workflows for the **CSI Data Acquisition System**: the **Initial System Configuration (Provisioning)** and the **Standard Data Acquisition Procedure**.

### Workflow 1: Initial System Configuration (Provisioning)

**Execute these steps only for the first-time use of a new ESP32 or after a factory reset.**

1.  **Power on the ESP32.** It will create a temporary Wi-Fi Access Point named `ESP_PROV`.
2.  **Launch a CSI Collector Application:**
    * **Desktop App:** Run `csicollector.py`. On the initial screen, click **"No, Configure Now"**.
    * **Mobile App:** Open the application. Navigate to the provisioning section.
3.  **Connect to the Provisioning Network:**
    * On your computer or mobile device, go to your Wi-Fi settings and connect to the **`ESP_PROV`** Wi-Fi network.
        * **Default Password:** `12345678`
    * **Desktop App:** Return to the application and click **"I Am Connected"**.
    * **Mobile App:** The app might automatically detect the connection or have a prompt to continue.
4.  **Fill in Network Details:** In the provisioning form (either desktop or mobile), fill in the details of your **primary Wi-Fi network** (the one the ESP32 and your PC/mobile will use for data collection).
    * Select the correct **Authentication Protocol** (WPA2-PSK or WPA2-Enterprise/PEAP).
    * Enter the **Network Name (SSID)**.
    * Enter the **Password** (and **Identity** for PEAP).
    * Confirm that the **Server IP** matches the IP your PC/mobile device will have on the primary network. (The applications will attempt to pre-fill this with your local IP).
    * Keep the **Server Port** as `50001` (default).
5.  **Submit Configuration:** Click **"Submit Configuration"** (Desktop) or **"Send Configuration"** (Mobile).
    * The ESP32 will receive the data, save it, and then restart.
    * After rebooting, the ESP32 will automatically connect to your primary network.

---

### Workflow 2: Data Acquisition

**Execute these steps for each measurement session after the ESP32 has been provisioned.**

1.  **Ensure Connectivity:**
    * Ensure the **ESP32 is powered on** and has successfully connected to your primary Wi-Fi network.
    * Ensure your **computer or mobile device is connected to the same primary Wi-Fi network** as the ESP32.
2.  **Launch a CSI Collector Application:**
    * **Desktop App:** Run `csicollector.py` and click **"Yes, Already Provisioned"**.
    * **Mobile App:** Open the application and navigate to the data collection screen.
3.  **Configure Acquisition:** On the acquisition configuration screen:
    * **Discover ESP32:** Click **"Discover"** for the application to find your ESP32's IP address on the local network. (This will auto-fill the IP field).
    * **Set Duration:** Enter the **Acquisition Duration** in seconds.
    * **Describe Scenario:** Provide a descriptive **Experimental Scenario** (e.g., "Walking in hallway," "Device stationary, clear LoS").
    * **Select Database:** Click **"Select Database"** (Desktop) or **"Select/Create .db File"** (Mobile) to choose an existing SQLite database file or create a new one where your CSI data will be saved.
4.  **Start Acquisition:** Click **"Start Acquisition"** (Desktop) or **"Start Collection"** (Mobile).
    * The application will send the start command to the ESP32.
    * The application will switch to a **Console screen** (Desktop) or display real-time logs (Mobile).
5.  **Monitor & Save:**
    * In the Console/Logs, you will see the CSI data arriving in real-time.
    * The collection will stop automatically once the configured duration is reached.
    * When the collection is finished, click **"Save Data"** (Desktop) or wait for automatic saving (Mobile, if implemented) to store the session in your selected database file.
6.  **New Session:** You can then click **"Return"** (Desktop) or navigate back (Mobile) to configure and start a new collection.

---
