# Meraki Network Automation Engine

A modular, Python-based automation engine designed to interface with the Cisco Meraki Dashboard API. This project handles global organization health checks, automated hardware inventory reconciliation, and wireless telemetry pipelines, engineered with defensive data parsing and structured JSON logging.

## System Architecture

The engine is decoupled into specialized modules to isolate the network transport layer from internal data processing and environment management:

+-------------------+      +---------------------+      +------------------------+
|     config.py     | ---> |      logger.py      | ---> |       app.py           |
| (python-dotenv)   |      | (Std Lib JSON Logs) |      | (Orchestration Engine) |
+-------------------+      +---------------------+      +------------------------+
|
Queries API via 'requests'
v
+-----------------------+
|   wireless_tele.py    |
| (Telemetry Pipeline)  |
+-----------------------+


### Module Breakdown
- **`config.py`**: Manages runtime variables and securely loads API credentials from local environments.
- **`logger.py`**: Implements structured JSON logging using native serialization to emit machine-readable telemetry events.
- **`wireless_tele.py`**: Handles dedicated wireless client, RSSI, and performance metric retrieval loops.
- **`app.py`**: The primary execution entry point coordinating inventory audits and state evaluation.

---

## Defensive Design Principles

- **Failing Loudly & Safely**: The engine relies on top-level `try/except` boundaries to catch upstream network drops or token failures immediately. Rather than muting errors, it cuts execution to prevent downstream logic from operating on incomplete payloads.
- **Data-Driven Logic Evaluation**: Avoids relying on HTTP response metrics for individual asset validation. Instead, it inspects internal object key-value states directly (e.g., evaluating `.get('networkId')`), ensuring unassigned cold-spares are processed without triggering runtime `KeyError` or `AttributeError` exceptions.

---

## Setup & Installation

### 1. Configure the Environment
Ensure your local environment contains a `.env` file that is excluded from source control via your `.gitignore`:

```text
MERAKI_API_TOKEN=your_secret_api_key_here
MERAKI_ORG_ID=your_target_organization_id_here
2. Install Dependencies
Install the required packages grouped by their target modules:

Bash
pip install -r requirements.txt
Usage
Run the primary automation orchestration script from your terminal:

Bash
python app.py

---

### 💻 Step 2: Push the Documentation Upstream

Once you have saved the file locally, fire off your standard Git routine to stage, commit, and push the new `README.md` up to your private GitHub repo:

```bash
# 1. Stage the new markdown file
git add README.md

# 2. Commit the documentation layer
git commit -m "Docs: Initialized comprehensive system architecture README"

# 3. Push to GitHub
git push
