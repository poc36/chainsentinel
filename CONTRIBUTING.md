# Contributing to ChainSentinel

Thank you for your interest in contributing to ChainSentinel! This document provides guidelines and instructions for contributing.

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Node.js 20+
- Docker & Docker Compose
- Git

### Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/chainsentinel.git
cd chainsentinel

# Start infrastructure
docker-compose -f docker-compose.dev.yml up -d postgres redis neo4j

# Backend setup
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt -r requirements-dev.txt

# Run migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --reload --port 8000

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

## 📋 Development Workflow

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/your-feature`
3. **Write** code following our conventions
4. **Test** your changes: `pytest` (backend), `npm test` (frontend)
5. **Lint** your code: `ruff check .` and `mypy .`
6. **Commit** with conventional commits: `feat:`, `fix:`, `docs:`, etc.
7. **Push** and create a Pull Request

## 🏗️ Code Standards

### Python (Backend)
- **Formatter**: Black (line length: 100)
- **Linter**: Ruff
- **Type Checker**: Mypy (strict mode)
- **Testing**: Pytest with async support
- **Style**: PEP 8, Google docstrings
- **Max file length**: 300 lines

### TypeScript (Frontend)
- **Linter**: ESLint
- **Formatter**: Prettier
- **Style**: Functional components, hooks-based

### Architecture Principles
- SOLID, DRY, KISS
- Clean Architecture with clear layer separation
- Domain-Driven Design for core business logic
- Each module must be independently testable

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest --cov=app tests/

# Type checking
mypy app/

# Linting
ruff check app/
```

## 📝 Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation
- `style:` — Code style (formatting, no logic change)
- `refactor:` — Code refactoring
- `test:` — Adding or updating tests
- `chore:` — Build process, dependencies

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.
