# Dexter 🤖

Dexter is an autonomous Hyperliquid crypto futures agent that thinks, plans, and executes from end to end. It can look up market structure, inspect your account, reason about funding and risk, and—when asked—submit, amend, or cancel orders on the Hyperliquid exchange. Think of it as a focused teammate that understands derivative trading workflows instead of equity research.

<img width="979" height="651" alt="Screenshot 2025-10-14 at 6 12 35 PM" src="https://github.com/user-attachments/assets/5a2859d4-53cf-4638-998a-15cef3c98038" />

## Overview

Dexter converts trading objectives into clear, auditable plans. It selects the right Hyperliquid MCP tools, optimises arguments, validates results, and synthesises a concise response with the numbers that matter. Each run is bounded by strict safety limits and loop detection so the agent never free-runs.

**Key Capabilities**
- **Structured Trade Planning** – break complex goals into market checks, risk analysis, and execution steps.
- **Hyperliquid MCP Integration** – call the same tooling exposed by the `hyperliquid-mcp` server for market data, leverage control, and order management.
- **Self-Validation** – confirm whether each task is complete before moving on, catching missing data or failed orders.
- **Execution Logging** – highlight risky calls like `place_order` or `withdraw` and show compact summaries of tool outputs.

## Prerequisites

- Python 3.10 or newer
- [uv](https://github.com/astral-sh/uv) package manager
- OpenAI API key (get [here](https://platform.openai.com/api-keys))
- Hyperliquid credentials:
  - `HYPERLIQUID_PRIVATE_KEY` – required for trading actions
  - `HYPERLIQUID_USER_ADDRESS` – optional override for account queries
  - `HYPERLIQUID_TESTNET` – set to `true` to stay on the testnet while iterating

> ⚠️ **Safety**  
> Always test on Hyperliquid testnet first. The agent will happily place or cancel orders if instructed and your environment is configured for trading.

## Installation

```bash
git clone https://github.com/virattt/dexter.git
cd dexter
uv sync
```

Copy the environment template and add your keys:

```bash
cp env.example .env
```

Then edit `.env` with:

```
OPENAI_API_KEY=sk-...
HYPERLIQUID_PRIVATE_KEY=0x...
HYPERLIQUID_USER_ADDRESS=0x...(optional)
HYPERLIQUID_TESTNET=true
```

## Usage

Start the interactive CLI:

```bash
uv run dexter-agent
```

Example prompts:

- “Show my current BTC and SOL positions on Hyperliquid testnet.”
- “What are the last 24h funding rates for ETH and how do they impact a long?”
- “Place a limit buy for 0.25 ETH at 3200 using ALO and confirm the order ID.”
- “Cancel all open orders on ARB then report the remaining exposure.”

## Architecture

Dexter keeps the same multi-agent loop with a new tool stack:

- **Planning Agent** – drafts atomised tasks aligned with Hyperliquid MCP tools.
- **Action Agent** – selects and parameterises the best tool call at each step.
- **Validation Agent** – decides if the task is complete or needs another pass.
- **Answer Agent** – summarises findings, actions, and risks in plain text.

The tool layer (`src/dexter/tools/hyperliquid.py`) wraps the MCP server defined in `hyperliquid-mcp/`, reusing its Pydantic request models and async clients.

## Project Structure

```
dexter/
├── src/
│   └── dexter/
│       ├── agent.py         # Core loop and safety rails
│       ├── cli.py           # Interactive prompt interface
│       ├── model.py         # LLM binding to OpenAI
│       ├── prompts.py       # Trading-focused system prompts
│       ├── schemas.py       # Pydantic schemas for LLM outputs
│       ├── tools/           # Hyperliquid MCP tool adapters
│       └── utils/           # UI + logging helpers
├── hyperliquid-mcp/         # Bundled MCP server implementation
├── pyproject.toml
└── uv.lock
```

## Configuration

```python
from dexter.agent import Agent

agent = Agent(
    max_steps=20,          # Global safety limit
    max_steps_per_task=5   # Cap retries per task
)
```

Tune those limits if you are orchestrating longer market analyses or more conservative execution.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make focused commits
4. Open a pull request describing the change and testing

## License

MIT License.
