#!/usr/bin/env python3
"""
Azure Resource Exporter and Documentation Generator
"""
import os
import argparse
from rich.console import Console
from rich.prompt import Prompt, Confirm

from azure_client import AzureClient
from exporter import ResourceExporter
from documentation_generator import DocumentationGenerator

console = Console()

def main():
    parser = argparse.ArgumentParser(description="Export Azure resources and generate documentation")
    parser.add_argument("--output", default="./output", help="Output directory for exported data and documentation")
    parser.add_argument("--format", choices=["json", "yaml", "markdown"], default="markdown", 
                        help="Output format for documentation")
    parser.add_argument("--non-interactive", action="store_true", 
                        help="Use default credentials instead of interactive login")
    args = parser.parse_args()
    
    # Ensure output directory exists
    os.makedirs(args.output, exist_ok=True)
    
    console.print("[bold green]Azure Resource Exporter and Documentation Generator[/bold green]")
    
    # Create Azure client and login
    azure_client = AzureClient(interactive=not args.non_interactive)
    
    console.print("Authenticating with Azure...")
    if not azure_client.login():
        console.print("[bold red]Authentication failed. Please check your credentials and try again.[/bold red]")
        return
    
    # Get available tenants
    console.print("Retrieving available Azure tenants...")
    tenants = azure_client.get_tenants()
    
    if not tenants:
        console.print("[bold red]No tenants found. Please check your Azure account.[/bold red]")
        return
    
    console.print(f"[green]Found {len(tenants)} tenants[/green]")
    
    # Let the user select a tenant
    selected_tenant = select_tenant(tenants)
    
    if not selected_tenant:
        console.print("[yellow]No tenant selected. Exiting.[/yellow]")
        return
    
    # Set the selected tenant
    tenant_id, tenant_name = selected_tenant
    console.print(f"Using tenant: [cyan]{tenant_name}[/cyan]")
    azure_client.set_tenant(tenant_id)
    
    # Get available subscriptions for the selected tenant
    console.print("Retrieving available subscriptions...")
    subscriptions = azure_client.get_subscriptions()
    
    if not subscriptions:
        console.print("[bold red]No subscriptions found in the selected tenant. Please check your permissions.[/bold red]")
        return
    
    console.print(f"[green]Found {len(subscriptions)} subscriptions[/green]")
    
    # Let the user select subscriptions
    selected_subscriptions = select_subscriptions(subscriptions)
    
    if not selected_subscriptions:
        console.print("[yellow]No subscriptions selected. Exiting.[/yellow]")
        return
    
    # Initialize the exporter
    exporter = ResourceExporter(azure_client)
    
    # Export resources from selected subscriptions
    console.print("[bold]Exporting resources from selected subscriptions...[/bold]")
    
    all_resources = {}
    for sub_id, sub_name in selected_subscriptions:
        console.print(f"Processing subscription: [cyan]{sub_name}[/cyan]")
        resources = exporter.export_resources(sub_id)
        all_resources[sub_id] = {
            "name": sub_name,
            "resources": resources
        }
    
    # Generate documentation
    console.print("[bold]Generating documentation...[/bold]")
    doc_generator = DocumentationGenerator(args.output, args.format)
    doc_generator.generate(all_resources)
    
    console.print(f"[bold green]Export and documentation completed![/bold green]")
    console.print(f"Output saved to: {os.path.abspath(args.output)}")

def select_tenant(tenants):
    """Let the user select a tenant"""
    console.print("[bold]Available Azure tenants:[/bold]")
    
    for i, (tenant_id, tenant_name) in enumerate(tenants, 1):
        console.print(f"{i}. [cyan]{tenant_name}[/cyan] ({tenant_id})")
    
    selected_index = Prompt.ask(
        "Enter tenant number to use",
        default="1"
    )
    
    try:
        index = int(selected_index.strip())
        if 1 <= index <= len(tenants):
            return tenants[index-1]
        else:
            console.print("[bold red]Invalid selection. Please enter a valid tenant number.[/bold red]")
            return select_tenant(tenants)
    except (ValueError, IndexError):
        console.print("[bold red]Invalid selection. Please enter a valid tenant number.[/bold red]")
        return select_tenant(tenants)

def select_subscriptions(subscriptions):
    """Let the user select one or more subscriptions"""
    console.print("[bold]Available subscriptions:[/bold]")
    
    for i, (sub_id, sub_name) in enumerate(subscriptions, 1):
        console.print(f"{i}. [cyan]{sub_name}[/cyan] ({sub_id})")
    
    select_all = Confirm.ask("Select all subscriptions?")
    
    if select_all:
        return subscriptions
    
    selected_indices = Prompt.ask(
        "Enter subscription numbers to process (comma-separated)",
        default="1"
    )
    
    try:
        indices = [int(idx.strip()) for idx in selected_indices.split(",")]
        selected = [subscriptions[i-1] for i in indices if 1 <= i <= len(subscriptions)]
        return selected
    except (ValueError, IndexError):
        console.print("[bold red]Invalid selection. Please enter valid subscription numbers.[/bold red]")
        return select_subscriptions(subscriptions)

if __name__ == "__main__":
    main() 