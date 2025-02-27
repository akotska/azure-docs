# Azure Resource Exporter and Documentation Generator

A tool for exporting Azure resources from selected subscriptions and generating comprehensive documentation for each resource type.

## Features

- Connect to Azure using your existing credentials
- Select one or more Azure subscriptions to export
- Export detailed resource information for all resource groups
- Generate comprehensive documentation for all resources
- Support for multiple output formats (Markdown, JSON, YAML)

## Prerequisites

- Python 3.8 or higher
- Azure subscription with appropriate permissions
- Azure CLI installed and authenticated or other valid Azure credentials
- WSL (Windows Subsystem for Linux) if running on Windows

## Installation and Setup

### Using Virtual Environment (Recommended)

1. Open WSL terminal and navigate to your project directory:
   ```bash
   cd /path/to/your/project
   ```

2. Create a new virtual environment:
   ```bash
   python3 -m venv azure-docs
   ```

3. Activate the virtual environment:
   ```bash
   source azure-docs/bin/activate
   ```

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the application:
   ```bash
   python main.py
   ```

6. When finished, deactivate the virtual environment:
   ```bash
   deactivate
   ```

### Standard Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/azure-resource-exporter.git
   cd azure-resource-exporter
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the application with default settings:
```bash
python main.py
```

### Command Line Options

- `--output`: Specify the output directory (default: ./output)
- `--format`: Specify the documentation format - markdown, json, or yaml (default: markdown)
- `--non-interactive`: Use default credentials instead of interactive login

## Output Structure

```
output/
├── data/
│   └── azure_resources_{timestamp}.json
└── docs/
    ├── index.md
    └── {subscription_id}/
        ├── overview.md
        └── {resource_group}/
            ├── overview.md
            ├── virtualmachines.md
            ├── virtualnetworks.md
            └── ...
``` 