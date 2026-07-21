# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-07-21

### Added
- Initial project structure and architecture
- FastAPI backend with JWT authentication and RBAC
- PostgreSQL database with full schema (Users, Addresses, Transactions, Investigations, Risk Assessments, Reports, Alerts, Audit Logs)
- Neo4j graph database integration for transaction graph analysis
- Redis caching layer
- Celery background task processing
- Multi-chain address validation (Bitcoin, Ethereum, Tron, BNB Chain, Polygon, Arbitrum, Optimism, Base, Solana, Litecoin, Dogecoin)
- AML Risk Scoring Engine with 30+ risk factors (OFAC, EU/UK Sanctions, Tornado Cash, Mixers, Darknet, Phishing, etc.)
- Behavioral analysis module (anomaly detection, pattern recognition, clustering)
- Machine learning module (Isolation Forest, DBSCAN, feature engineering)
- AI Investigator with LLM integration (OpenAI + Ollama)
- Professional PDF report generation
- Demo blockchain data provider with realistic synthetic data
- React + TypeScript frontend with TailwindCSS
- Interactive transaction graph visualization (Cytoscape.js)
- Dashboard with 15+ analytics widgets (Plotly, Recharts)
- Investigation management with search, filters, tags, comments
- Docker Compose infrastructure (PostgreSQL, Redis, Neo4j, Nginx)
- Comprehensive test suite
- CI/CD pipeline (GitHub Actions)
