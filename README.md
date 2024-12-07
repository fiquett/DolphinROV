# DolphinROV

DolphinROV is a biomimetic robotic dolphin ROV designed for underwater exploration, diver assistance, and research applications. This repository includes components ranging from hardware designs to AI and software modules.

## Features
- **JANUS Protocol**: For underwater communication interoperability.
- **Dive Computer Integration**: Compatible with modern dive computers for real-time monitoring and redundancy.
- **Autonomous Navigation**: Ensures safe, efficient underwater exploration.
- **Decompression Management**: Tracks ascent profiles and assists divers.
- **AI-Driven Behavior**: Intelligent responses for diver safety and exploration tasks.

## Repository Structure
```plaintext
DolphinROV/
├── docs/                # Documentation for setup, usage, and development
├── hardware/            # CAD files, schematics, and hardware details
├── software/            # Codebase for the ROV
│   ├── navigation/      # Autonomous navigation algorithms
│   ├── communication/   # Acoustic and RF communication protocols
│   │   ├── janus/       # JANUS protocol implementation
│   │   ├── dive_computer/ # Dive computer API integrations
│   ├── decompression/   # Decompression management system
│   ├── ai/              # AI modules for decision-making and safety
├── tests/               # Testing scripts for hardware and software
├── simulations/         # Simulation models for virtual testing
├── resources/           # Research papers and references
├── LICENSE              # License for the project
├── README.md            # Overview of the project
└── CONTRIBUTING.md      # Contribution guidelines
```

## Getting Started
- Refer to `docs/` for detailed setup instructions.
- Use the modular structure to customize and extend DolphinROV for your needs.

## Contributions
We welcome contributions! See `CONTRIBUTING.md` for more information.
