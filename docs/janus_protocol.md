# JANUS Protocol Integration

The JANUS protocol enables DolphinROV to communicate seamlessly with other underwater systems.

## Features
- Low-bandwidth acoustic communication.
- Interoperability with NATO-compliant devices.

## Commands
- **COMMAND: STOP**: Halts all operations.
- **DATA: DEPTH=Xm**: Sends depth data.

## Setup
1. Navigate to `software/communication/janus/`.
2. Customize the JANUS decoder in `janus_decoder.py`.

## Testing
- Use simulated acoustic signals to verify functionality.