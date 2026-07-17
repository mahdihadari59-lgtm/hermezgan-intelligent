🌊 Hermezgan Intelligent (HDP AI Platform)

"Version" (https://img.shields.io/badge/version-2.0.0-blue)
"Status" (https://img.shields.io/badge/status-Active-success)
"License" (https://img.shields.io/badge/license-MIT-green)
"Python" (https://img.shields.io/badge/python-3.10+-blue)
"Node.js" (https://img.shields.io/badge/node.js-18+-green)

---

AI Platform for Hormozgan Province

Hermezgan Intelligent (HDP) is an integrated AI platform designed specifically for Hormozgan Province.

The project combines artificial intelligence, geographic information, local knowledge, transportation services, tourism, public services and conversational AI into a unified platform.

The long-term vision is to build an intelligent digital infrastructure capable of understanding local Persian language, geographic context and regional knowledge.

---

What's New in Version 2.0

New Bridge Layer

Version 2 introduces a completely modular Bridge architecture.

bridge/
├── archive/
│   └── v0/
└── v1/
    ├── api.py
    ├── bridge_service.py
    ├── database_bridge.py
    ├── logger.py
    ├── utils.py
    ├── exceptions.py
    └── service

Features:

- Database abstraction
- Unified service layer
- Logging system
- Exception handling
- Modular APIs
- Future scalability

---

Geographic Migration System

database/migrations/
└── 001_normalize_geo.sql

Supports:

- Geographic normalization
- Cities
- Districts
- Roads
- POIs
- Administrative hierarchy

---

BND Knowledge Dataset

bnd.json

Persian structured knowledge dataset used by the AI engine.

Importer:

import_bnd.py

---

Improved Chat Interface

The React frontend has been updated with:

- Modern chat layout
- Better responsive UI
- Cleaner message rendering
- CSS improvements
- Component optimization

---

Project Structure

hermezgan-intelligent/

├── backend/
├── frontend/
├── bridge/
├── database/
├── docs/
├── scripts/

├── bnd.json
├── import_bnd.py
├── docker-compose.yml
├── LICENSE
└── README.md

---

Main Features

- Persian AI Chat
- Geographic Knowledge Base
- Interactive Map Support
- SQLite Database
- Geographic Search
- Local Knowledge
- Bridge API
- Migration System
- Modular Backend
- React Frontend

---

Technology Stack

Backend

- Python
- FastAPI
- SQLite
- REST API

Frontend

- React
- JavaScript
- CSS

AI

- Persian NLP
- Knowledge Base
- Retrieval Pipeline
- Bridge Architecture

Database

- SQLite
- SQL Migration
- Geographic Data

---

Getting Started

Clone repository

git clone https://github.com/mahdihadari59-lgtm/hermezgan-intelligent.git

cd hermezgan-intelligent

Backend

cd backend

python -m venv venv

source venv/bin/activate

pip install -r requirements.txt

Frontend

cd frontend

npm install

npm start

---

Development Roadmap

Version 2.x

- Voice Assistant
- Offline AI
- Vosk Speech Recognition
- Semantic Search
- Embedding Search
- Tourism Services
- Transportation Module

Version 3.x

- Knowledge Graph Engine
- AI Driver Assistant
- Smart Traffic Prediction
- Recommendation Engine
- Multi-Agent AI
- Advanced Analytics

---

Repository

Branch:
main

Current Version

2.0.0

---

License

This project is released under the MIT License.

---

Author

Mahdi Haidari Puri

Founder & Lead Developer

Project:
Hermezgan Intelligent (HDP AI Platform)

---

Vision

Create the first native AI platform dedicated to Hormozgan Province by integrating:

- Artificial Intelligence
- Geographic Intelligence
- Transportation
- Tourism
- Public Services
- Local Knowledge
- Persian Conversational AI

into one scalable, modular and production-ready ecosystem.

---

Current Repository Status

- Modular Bridge Architecture
- Geographic Migration Framework
- Improved React Chat UI
- BND Knowledge Dataset
- SQLite Knowledge Database
- OpenStreetMap Ready
- Production-oriented Project Structure

---

⭐ If you find this project useful, please consider starring the repository and contributing to future development.
## Release Notes

### v2.0.0 (July 2026)

### Added
- Bridge v1 architecture
- Database Bridge layer
- Geographic normalization migration
- BND knowledge dataset
- BND import utility
- Improved React Chat UI
- Modular project structure

### Improved
- Chat interface
- CSS components
- Backend modularization
- Database abstraction

### Planned for v3.0
- Vosk Speech Recognition
- Offline AI Assistant
- Knowledge Graph Engine
- RAG Pipeline
- Embedding Search
- Multi-Agent AI
- Smart Transportation Services
