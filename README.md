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

### Install UV

1. [See UV Installation Docs](https://docs.astral.sh/uv/getting-started/installation/)

### Standard Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/azure-resource-exporter.git
   cd azure-resource-exporter
   ```

## Usage

UV will install dependencies and run with the default settings:
```bash
uv run
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