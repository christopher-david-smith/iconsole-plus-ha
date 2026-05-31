# iConsole+ Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Home Assistant integration for iConsole+ compatible exercise equipment (bikes, ellipticals, etc.) via Bluetooth Low Energy (BLE).

This integration uses the [iconsole-plus](https://pypi.org/project/iconsole-plus/) library to communicate directly with the equipment's head unit.

## Features

- **Automatic Discovery**: Discovers your equipment automatically via Bluetooth (UUID or name-based).
- **Device Support**: Groups all entities under a single "iConsole+" device in Home Assistant.
- **Workout Control**: A dedicated switch to start and stop workout sessions (connects/disconnects Bluetooth).
- **Resistance Control**: Real-time resistance adjustment (level 1-32).
- **Live Telemetry**: High-frequency updates for:
  - Speed (km/h)
  - Cadence (RPM)
  - Power (Watts)
  - Distance (km)
  - Calories (kcal)
  - Duration (seconds)
  - Heart Rate (bpm)

## Installation

### Via HACS (Recommended)

1. Open **HACS** in your Home Assistant instance.
2. Click the three dots in the top right corner and select **Custom repositories**.
3. Add `https://github.com/christopher-david-smith/iconsole-plus-ha` with the category **Integration**.
4. Click **Download** on the iConsole+ integration.
5. Restart Home Assistant.

### Manual Installation

1. Copy the `custom_components/iconsole_plus` directory into your `config/custom_components/` directory.
2. Restart Home Assistant.

## Configuration

1. Ensure your equipment is in pairing mode (usually by pedaling/moving it) and **not** connected to any other app (like the official iConsole+ app).
2. Go to **Settings** > **Devices & Services**.
3. The device should be automatically discovered. Click **Configure**.
4. If it's not discovered, click **Add Integration** and search for **iConsole+**.

## Usage

Once added, you will see a **Workout** switch. 
- **Turn the switch ON** to initiate the connection and start the workout session. The bike will beep, and telemetry data will begin streaming.
- **Turn the switch OFF** to end the session and disconnect.

Use the **Resistance** slider to change the difficulty level during your workout.

## Compatibility

This integration is compatible with most exercise equipment that uses the iConsole+ protocol over Bluetooth, typically marketed under various brands like Domyos, Klarstein, Skandika, and others.

## Disclaimer

This project is not affiliated with or endorsed by iConsole+ or any equipment manufacturer. Use at your own risk.
