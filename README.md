# ADK Agentic AI

An AI agent project built with Google's Agent Development Kit (ADK), featuring a Gemini 2.0 Flash-powered assistant capable of performing various tasks.

## Overview

This project implements an agentic AI system using Google's ADK framework. The main agent, `genie_agent`, leverages the Gemini 2.0 Flash model to provide intelligent assistance across a variety of tasks.

## Features

- **Gemini 2.0 Flash Integration**: Powered by Google's latest language model
- **Extensible Agent Architecture**: Built on Google ADK for easy customization
- **Task Versatility**: Designed to handle diverse assistance requests

## Project Structure

```
adk-agentic-ai/
├── genie_agent/
│   ├── __init__.py
│   └── agent.py          # Main agent implementation
├── main.py               # Entry point
├── pyproject.toml        # Project configuration
├── .env.example          # Environment variables template
└── README.md             # This file
```

## Setup

1. **Prerequisites**: Python 3.13 or higher

2. **Environment Setup**:
   ```bash
   # Copy environment template
   cp .env.example .env

   # Edit .env with your configuration
   # (Add required API keys and settings)
   ```

3. **Install Dependencies**:
   ```bash
   # Using uv (recommended)
   uv sync

   # Or using pip
   pip install -e .
   ```

## Usage

Run the main application:

```bash
python main.py
```

## Development

### Code Quality

The project uses Ruff for code formatting and linting:

```bash
# Install development dependencies
uv sync --group dev

# Run linting
ruff check

# Format code
ruff format
```

## License

[Add your license information here]

## Contributing

[Add contributing guidelines here]
