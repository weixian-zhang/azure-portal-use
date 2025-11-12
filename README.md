# Azure Portal Use Agent

An AI agent that automates Azure resource management tasks in Azure Portal using browser automation.

## Features

- 🤖 AI-powered browser automation using LangChain and Azure OpenAI
- 🌐 Automated Azure Portal navigation and interactions
- 🔐 Secure credential management with environment variables
- 🎯 Multi-factor authentication support

## Installation

### Using pip

```bash
# Clone the repository
git clone https://github.com/weixian-zhang/azure-portal-use.git
cd azure-portal-use

# Install the package
pip install -e .

# Or with optional dependencies
pip install -e ".[dev,azure]"
```

### Using uv (recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create a virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

## Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Update `.env` with your credentials:
   ```bash
   # Azure Portal Credentials
   AZURE_PORTAL_USERNAME=your-username@domain.onmicrosoft.com
   AZURE_PORTAL_PASSWORD=your-password

   # Azure OpenAI Configuration
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
   OPENAI_API_KEY=your-api-key
   OPENAI_MODEL_NAME=gpt-4o
   ```

## Usage

### Command Line

```bash
# Run the agent
azure-portal-use

# Or using Python module
python -m azure_portal_use.main
```

### Programmatic Usage

```python
from azure_portal_use.main import setup_environment, create_llm, create_task, run_agent
import asyncio

# Setup
env_vars = setup_environment()
llm = create_llm(
    azure_endpoint=env_vars["azure_endpoint"],
    api_key=env_vars["api_key"],
    model=env_vars["model"],
)

# Create and run agent
task = create_task(
    username=env_vars["username"],
    password=env_vars["password"],
)
asyncio.run(run_agent(llm, task))
```

## Development

### Setup Development Environment

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Install Playwright browsers
playwright install
```

### Code Quality Tools

```bash
# Format code
black src/
isort src/

# Lint code
ruff check src/

# Type checking
mypy src/

# Run tests
pytest
```

## Project Structure

```
azure-portal-use/
├── src/
│   └── azure_portal_use/
│       ├── __init__.py
│       └── main.py
├── tests/
├── misc_tests/
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
└── pyproject.toml
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.