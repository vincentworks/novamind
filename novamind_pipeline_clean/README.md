# NovaMind AI Marketing Content Pipeline

## Overview

This project implements an end-to-end AI-powered marketing pipeline for a fictional startup, NovaMind. Starting from a single topic, the system generates blog and newsletter content, segments contacts, simulates campaign distribution, and analyzes performance to recommend future improvements.

The pipeline is designed to show how a startup growth team could connect content generation, CRM operations, and analytics in one modular workflow.

## Architecture Overview

Input Topic
    ↓
AI Content Generation (Open AI and Mock Fallback)
    ↓
Structured Content Storage (JSON)
    ↓
CRM Segmentation (Persona-based)
    ↓
HubSpot Contact Upsert (Real API)
    ↓
Campaign Distribution (Simulated Payloads)
    ↓
Performance Simulation and Aggregation
    ↓
Insight Generation 

This creates a closed-loop system: content → segmentation → distribution → performance → optimization.

## System Components

### 1. Content Generation (`src/generate_content.py`)
- Accepts a topic as input
- Generates:
  - blog title, outline, and draft (400–600 words)
  - persona-specific newsletters (3 segments)
- Supports:
  - OpenAI API generation
  - deterministic mock fallback if API is unavailable
- Normalizes output formatting (e.g., consistent “AI” capitalization)
- Stores output in:
  - `data/generated_content.json`

### 2. CRM Simulation (`src/crm_simulation.py`)
- Loads contacts from:
  - `data/contacts.json`
- Uses a standardized `custom_persona` field for segmentation
- Maps each contact to the appropriate newsletter variant
- Handles multiple newsletter formats (mock + OpenAI-generated)
- Builds a structured campaign object with:
  - audience segmentation
  - personalized subject/body
  - campaign metadata
- Stores output in:
  - `data/campaign_log.json`

### 3. HubSpot Integration (`src/hubspot_integration.py`)
- Integrates with the real HubSpot CRM API:
  - `POST /crm/v3/objects/contacts/batch/upsert`
- Creates or updates contacts using email as the unique identifier
- Writes a custom `custom_persona` property to each contact
- Demonstrates realistic CRM usage with:
  - structured payloads
  - authenticated API requests
- Generates simulated “single-send” email payloads (non-executed)
- Stores:
  - request + response data
  - mocked send payloads
- Output file:
  - `data/hubspot_payloads.json`

### 4. Performance Logging & Analysis (`src/analyze_performance.py`)
- Simulates campaign performance metrics:
  - open rate
  - click-through rate
  - unsubscribe rate
- Aggregates results:
  - per contact
  - per persona segment
- Uses persona-based benchmarks to simulate realistic variation
- Generates a natural-language performance summary
- Stores output in:
  - `data/performance_log.json`

## Tools, APIs, and Models Used

- Python 3  
- HubSpot CRM API  
  - `/crm/v3/objects/contacts/batch/upsert`  
- OpenAI API (optional, with fallback)  
- `requests` for HTTP calls  
- `python-dotenv` for environment configuration  
- JSON files for structured local storage  

## Assumptions

- Performance metrics are simulated using predefined persona benchmarks  
- Email delivery is modeled via realistic HubSpot payloads, not executed sends  
- OpenAI integration is optional and falls back to deterministic mock content  
- HubSpot integration requires:
  - a developer account
  - a private app token with contact write permissions  
- All outputs are stored locally for reproducibility and review  

## How to Run Locally

### 1. Open the project folder

```bash
cd novamind_pipeline
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create an `.env` file in the project root

```bash
HUBSPOT_PRIVATE_APP_TOKEN=your_token_here
OPENAI_API_KEY=your_key_here
```

Notes:
- `HUBSPOT_PRIVATE_APP_TOKEN` is only needed for the HubSpot integration step.
- `OPENAI_API_KEY` is optional. If omitted, the content generation script uses pre-selected mock content.

### 5. Run the full pipeline

```bash
python3 src/generate_content.py --topic "AI in creative automation"
python3 src/crm_simulation.py
python3 src/hubspot_integration.py
python3 src/analyze_performance.py
```

## Outputs

The following files are written to `data/`:

- `generated_content.json` → AI-generated blog and newsletter content
- `campaign_log.json` → Segmented campaign and personalized messaging
- `hubspot_payloads.json` → HubSpot/CRM API payloads and responses + simulated sends
- `performance_log.json` → Campaign performance and optimization insights

## Future Improvements

- Replace simulated performance metrics with real campaign analytics
- Add A/B testing for subject lines and content variants
- Add a lightweight dashboard for monitoring campaign performance
- Use historical performance data to influence future content generation
