# Colect Service

Industrial data collection service with multi-industry support. This service collects data from multiple industries simultaneously using different protocols (OPC UA, MQTT, etc.) and stores it in MongoDB.

## Features

- Multi-industry support with independent collection threads
- Modular design using Strategy and Abstract Factory patterns
- Support for multiple collection protocols
- Real-time data collection every 30 seconds
- Fault tolerance - failures in one industry don't affect others
- Extensible architecture for adding new industries and protocols

## Installation

```bash
pip install -r requirements.txt