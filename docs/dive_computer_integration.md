# Dive Computer Integration

DolphinROV interfaces with modern dive computers to provide real-time data and redundancy.

## Supported Models
- Shearwater Perdix
- Suunto D5
- Garmin Descent

## Features
- Data relay: Depth, gas pressure, and decompression stops.
- Backup display: Surface team can monitor diver status remotely.

## Implementation
- APIs for Bluetooth and acoustic modem connections.
- Refer to `software/communication/dive_computer/`.

## Testing
- Connect a supported dive computer and verify data relay using `dive_computer_interface.py`.
