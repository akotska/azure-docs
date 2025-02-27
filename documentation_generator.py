"""
Generate documentation for exported Azure resources
"""
import os
import json
import yaml
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape

class DocumentationGenerator:
    """Generate documentation from exported resource data"""
    
    def __init__(self, output_dir, format="markdown"):
        self.output_dir = output_dir
        self.format = format
        self.data_dir = os.path.join(output_dir, "data")
        self.docs_dir = os.path.join(output_dir, "docs")
        self.consolidated_dir = os.path.join(output_dir, "consolidated")
        
        # Create directories
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.docs_dir, exist_ok=True)
        os.makedirs(self.consolidated_dir, exist_ok=True)
        
        # Initialize Jinja2 environment for templates
        self.env = Environment(
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    def generate(self, resources):
        """Generate documentation for the given resources"""
        # First, save the raw data
        self._save_raw_data(resources)
        
        # Generate documentation for each subscription
        for sub_id, subscription in resources.items():
            self._generate_subscription_docs(sub_id, subscription)
        
        # Generate index page
        self._generate_index(resources)
        
        # Generate consolidated resource type view
        self._generate_consolidated_view(resources)
    
    def _save_raw_data(self, resources):
        """Save the raw exported data"""
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        filename = f"azure_resources_{timestamp}"
        
        if self.format == "json":
            with open(os.path.join(self.data_dir, f"{filename}.json"), "w") as f:
                json.dump(resources, f, indent=2)
        else:  # yaml
            with open(os.path.join(self.data_dir, f"{filename}.yaml"), "w") as f:
                yaml.dump(resources, f, default_flow_style=False)
    
    def _generate_subscription_docs(self, sub_id, subscription):
        """Generate documentation for a subscription"""
        sub_name = subscription["name"]
        resources = subscription["resources"]
        
        # Create subscription directory
        sub_dir = os.path.join(self.docs_dir, sub_id)
        os.makedirs(sub_dir, exist_ok=True)
        
        # Generate subscription overview
        self._generate_subscription_overview(sub_dir, sub_id, sub_name, resources)
        
        # Generate documentation for each resource group
        for rg_name, resource_types in resources.items():
            self._generate_resource_group_docs(sub_dir, sub_id, sub_name, rg_name, resource_types)
    
    def _generate_subscription_overview(self, sub_dir, sub_id, sub_name, resources):
        """Generate overview documentation for a subscription"""
        # For now, create a simple markdown file
        with open(os.path.join(sub_dir, "overview.md"), "w") as f:
            f.write(f"# Subscription Overview: {sub_name}\n\n")
            f.write(f"Subscription ID: `{sub_id}`\n\n")
            f.write("## Resource Groups\n\n")
            
            for rg_name in resources.keys():
                f.write(f"- [{rg_name}]({rg_name}/overview.md)\n")
    
    def _generate_resource_group_docs(self, sub_dir, sub_id, sub_name, rg_name, resource_types):
        """Generate documentation for a resource group"""
        # Create resource group directory
        rg_dir = os.path.join(sub_dir, rg_name)
        os.makedirs(rg_dir, exist_ok=True)
        
        # Generate resource group overview
        with open(os.path.join(rg_dir, "overview.md"), "w") as f:
            f.write(f"# Resource Group: {rg_name}\n\n")
            f.write(f"Subscription: {sub_name} (`{sub_id}`)\n\n")
            f.write("## Resource Types\n\n")
            
            for resource_type, resources in resource_types.items():
                type_name = resource_type.split('/')[-1]
                f.write(f"- [{type_name}]({type_name}.md) ({len(resources)} resources)\n")
        
        # Generate documentation for each resource type
        for resource_type, resources in resource_types.items():
            self._generate_resource_type_docs(rg_dir, resource_type, resources)
    
    def _generate_resource_type_docs(self, rg_dir, resource_type, resources):
        """Generate documentation for a resource type"""
        type_name = resource_type.split('/')[-1]
        
        # For now, create a simple markdown file
        with open(os.path.join(rg_dir, f"{type_name}.md"), "w") as f:
            f.write(f"# {type_name.capitalize()}\n\n")
            f.write(f"Resource Type: `{resource_type}`\n\n")
            f.write(f"## Resources ({len(resources)})\n\n")
            
            for resource in resources:
                f.write(f"### {resource['name']}\n\n")
                f.write(f"- Location: {resource['location']}\n")
                if resource['tags']:
                    f.write("- Tags:\n")
                    for key, value in resource['tags'].items():
                        f.write(f"  - {key}: {value}\n")
                
                # Write resource-specific properties
                if resource['properties']:
                    f.write("\n#### Properties\n\n")
                    self._write_properties(f, resource['properties'])
                
                f.write("\n")
    
    def _write_properties(self, file, properties, indent=0):
        """Write properties recursively to a file"""
        indent_str = "  " * indent
        
        for key, value in properties.items():
            if isinstance(value, dict):
                file.write(f"{indent_str}- {key}:\n")
                self._write_properties(file, value, indent + 1)
            elif isinstance(value, list):
                file.write(f"{indent_str}- {key}:\n")
                for item in value:
                    if isinstance(item, dict):
                        file.write(f"{indent_str}  -\n")
                        self._write_properties(file, item, indent + 2)
                    else:
                        file.write(f"{indent_str}  - {item}\n")
            else:
                file.write(f"{indent_str}- {key}: {value}\n")
    
    def _generate_index(self, resources):
        """Generate an index page for all documentation"""
        with open(os.path.join(self.docs_dir, "index.md"), "w") as f:
            f.write("# Azure Resources Documentation\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Subscriptions\n\n")
            for sub_id, subscription in resources.items():
                f.write(f"- [{subscription['name']}]({sub_id}/overview.md) (`{sub_id}`)\n")
    
    def _generate_consolidated_view(self, resources):
        """Generate a consolidated view of all resources grouped by type"""
        # Dictionary to store resources by type
        resources_by_type = {}
        
        # Collect all resources across subscriptions and group by type
        for sub_id, subscription in resources.items():
            sub_name = subscription["name"]
            
            for rg_name, resource_types in subscription["resources"].items():
                for resource_type, resource_list in resource_types.items():
                    if resource_type not in resources_by_type:
                        resources_by_type[resource_type] = []
                    
                    # Add subscription and resource group info to each resource
                    for resource in resource_list:
                        resource_info = {
                            "subscription_id": sub_id,
                            "subscription_name": sub_name,
                            "resource_group": rg_name,
                            **resource  # Include all existing resource information
                        }
                        resources_by_type[resource_type].append(resource_info)
        
        # Generate the consolidated view file
        consolidated_file = os.path.join(self.consolidated_dir, "resources_by_type.md")
        with open(consolidated_file, "w") as f:
            f.write("# Consolidated Azure Resources by Type\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Sort resource types alphabetically
            for resource_type in sorted(resources_by_type.keys()):
                resources = resources_by_type[resource_type]
                type_name = resource_type.split('/')[-1]
                
                f.write(f"## {type_name} (`{resource_type}`)\n\n")
                f.write(f"Total Resources: {len(resources)}\n\n")
                
                # Sort resources by subscription, resource group, and name
                resources.sort(key=lambda x: (x["subscription_name"], x["resource_group"], x["name"]))
                
                for resource in resources:
                    f.write(f"### {resource['name']}\n\n")
                    f.write(f"- Subscription: {resource['subscription_name']} (`{resource['subscription_id']}`)\n")
                    f.write(f"- Resource Group: {resource['resource_group']}\n")
                    f.write(f"- Location: {resource['location']}\n")
                    
                    if resource['tags']:
                        f.write("- Tags:\n")
                        for key, value in resource['tags'].items():
                            f.write(f"  - {key}: {value}\n")
                    
                    if resource['properties']:
                        f.write("\n#### Properties\n\n")
                        self._write_properties(f, resource['properties'])
                    
                    f.write("\n")
        
        # Generate a summary file
        summary_file = os.path.join(self.consolidated_dir, "resource_type_summary.md")
        with open(summary_file, "w") as f:
            f.write("# Azure Resource Type Summary\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("| Resource Type | Count |\n")
            f.write("|--------------|-------|\n")
            
            total_resources = 0
            for resource_type in sorted(resources_by_type.keys()):
                count = len(resources_by_type[resource_type])
                total_resources += count
                f.write(f"| `{resource_type}` | {count} |\n")
            
            f.write("\n")
            f.write(f"**Total Resources: {total_resources}**\n") 