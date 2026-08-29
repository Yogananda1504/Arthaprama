# Arthaprama (अर्थप्रमा) - Technical IPO Analysis Engine

[![CI Pipeline](https://github.com/Yogananda1504/Arthaprama/actions/workflows/ci.yml/badge.svg)](https://github.com/Yogananda1504/Arthaprama/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Model Context Protocol](https://img.shields.io/badge/MCP-Enabled-orange.svg)](https://modelcontextprotocol.io/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/badge/linter-ruff-red.svg)](https://github.com/astral-sh/ruff)

> **Philosophical Root**: In Indian epistemology, *"Prama"* signifies accurate, foundational, and valid knowledge. **Arthaprama** translates this concept into technical financial analysis for Indian Initial Public Offerings (IPOs).

---

## 📌 Overview

**Arthaprama** is a production-grade quantitative analytical framework designed specifically for evaluating Indian IPOs. It integrates:
- Mathematical models for **Growth**, **Risk**, and **Valuation**.
- An adaptive **100-Point Composite Scoring Engine** tailored to investor risk profiles.
- A high-performance **FastAPI REST API** with schema validation and batch file upload support.
- A **Model Context Protocol (MCP) Server** enabling AI agents (Claude, Gemini, ChatGPT) to perform structured IPO evaluations over SSE and stdio transports.

---

## 🏗️ Core Architecture & Modules

### 1. Growth Engine (`arthaprama.ipo.growth`)
- **Compounding & Momentum**: 3-Year Revenue & PAT CAGR, YoY growth rates for Revenue, EBITDA, and EPS.
- **Operating Efficiencies**: EBITDA Margin, PAT Margin, and Cash Flow from Operations (CFO) trajectory.
- **Capital Productivity**: Return on Equity (ROE) and Return on Capital Employed (ROCE).

### 2. Risk Engine (`arthaprama.ipo.risk`)
- **Solvency & Coverage**: Debt-to-Equity (D/E), Net Debt to EBITDA, and Interest Coverage Ratio.
- **Liquidity & Working Capital**: Current Ratio, Quick Ratio, and Working Capital cycle health.
- **Governance & Concentration**: Single-customer revenue concentration, promoter share pledging, and contingent liabilities relative to net worth.

### 3. Valuation Engine (`arthaprama.ipo.valuation`)
- **Multiples Analysis**: P/E, P/B, EV/EBITDA, EV/Sales, and PEG ratio.
- **Discounted Cash Flow (DCF)**: Fair value modeling and discount/premium estimations.
- **Peer Group Benchmarking**: Relative premium/discount against sector median multiples.

### 4. Adaptive Scoring Matrix (`arthaprama.ipo.scoring`)
Scores companies out of **100 points** across four pillars dynamically calibrated by investor strategy:
- **Balanced Profile** (Default: 30 Growth / 30 Risk / 30 Valuation / 10 IPO Quality)
- **Conservative Profile** (Safety-first, heavier risk weighting)
- **Aggressive Growth Profile** (Momentum & expansion weighting)
- **Deep Value Profile** (Multiple margin-of-safety weighting)

### 5. AI Agent MCP Server (`backend.mcp_server`)
Exposes domain tools under the Model Context Protocol:
- `calculate_ipo_growth`
- `calculate_ipo_risk`
- `calculate_ipo_valuation`
- `generate_composite_score`
- `run_full_ipo_workflow`

---

## 📁 Project Structure

```text
Arthaprama/
├── arthaprama/                  # Core calculation & financial domain engines
│   ├── ipo/
│   │   ├── growth.py            # Growth & compounding metrics
│   │   ├── risk.py              # Balance sheet & risk metrics
│   │   ├── valuation.py         # Multiples & valuation models
│   │   ├── scoring.py           # 100-point scoring algorithm
│   │   └── workflow.py          # Unified orchestration workflow
│   ├── config.py                # Investor profiles & threshold configs
│   └── utils.py                 # INR currency formatters & math helpers
├── backend/                     # API & MCP service layer
│   ├── routes/
│   │   └── ipo.py               # FastAPI REST endpoints
│   ├── main.py                  # ASGI server & lifespan management
│   ├── mcp_server.py            # MCP server implementation (SSE + stdio)
│   └── schemas.py               # Pydantic v2 validation models
├── tests/                       # Automated test suite
│   ├── unit/                    # Math & domain formula tests
│   ├── integration/             # FastAPI endpoint tests
│   ├── test_mcp.py              # MCP tool invocation tests
│   └── test_workflow.py         # End-to-end workflow tests
├── pyproject.toml               # Poetry package & tool configuration
└── README.md                    # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites
- Python `3.10` or higher
- [Poetry](https://python-poetry.org/docs/#installation) package manager

### 1. Installation

Clone the repository and install all dependencies:
```bash
git clone https://github.com/Yogananda1504/Arthaprama.git
cd Arthaprama
poetry install
```

### 2. Running the FastAPI Server

Launch the REST API with hot reloading:
```bash
poetry run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```
- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc UI**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **MCP SSE Endpoint**: [http://localhost:8000/sse](http://localhost:8000/sse)

### 3. Running the MCP Server for AI Agents

For local AI assistant desktop clients (e.g., Claude Desktop, Antigravity):
```bash
poetry run python backend/mcp_server.py
```

---

## 🧪 Testing & Code Quality

Execute the test suite with coverage report:
```bash
poetry run pytest tests/ --cov=arthaprama --cov=backend --cov-report=term-missing
```

Run linting and style validation:
```bash
# Check formatting with Ruff
poetry run ruff check .

# Verify Black formatting
poetry run black --check arthaprama backend tests
```

---

## 📄 License

Distributed under the Apache 2.0 License. See `LICENSE` for more information.
