"""
Exporter for Azure resources
"""
from rich.progress import Progress
from rich.console import Console

console = Console()

class ResourceExporter:
    """Export resources from Azure subscriptions"""
    
    def __init__(self, azure_client):
        self.azure_client = azure_client
    
    def export_resources(self, subscription_id):
        """Export all resources from a subscription"""
        resources = {}
        
        # Get resource client
        resource_client = self.azure_client.get_resource_client(subscription_id)
        
        # Get all resource groups
        resource_groups = list(resource_client.resource_groups.list())
        
        with Progress() as progress:
            task = progress.add_task(f"Exporting resources...", total=len(resource_groups))
            
            for rg in resource_groups:
                resources[rg.name] = self._export_resource_group(subscription_id, rg.name)
                progress.update(task, advance=1)
        
        return resources
    
    def _export_resource_group(self, subscription_id, resource_group_name):
        """Export all resources from a resource group"""
        resource_client = self.azure_client.get_resource_client(subscription_id)
        
        # Get all resources in the resource group
        resources_list = resource_client.resources.list_by_resource_group(resource_group_name)
        
        # Group resources by type
        resources_by_type = {}
        for resource in resources_list:
            resource_type = resource.type
            if resource_type not in resources_by_type:
                resources_by_type[resource_type] = []
            
            # Extract basic information for all resources
            resource_info = {
                "id": resource.id,
                "name": resource.name,
                "location": resource.location,
                "type": resource.type,
                "tags": resource.tags,
                "properties": {}
            }
            
            # Add resource-specific details
            self._add_resource_details(subscription_id, resource, resource_info)
            
            resources_by_type[resource_type].append(resource_info)
        
        return resources_by_type
    
    def _add_resource_details(self, subscription_id, resource, resource_info):
        """Add resource-specific details to the resource info"""
        resource_type = resource.type.lower()
        
        try:
            # Virtual Network
            if "microsoft.network/virtualnetworks" in resource_type:
                network_client = self.azure_client.get_network_client(subscription_id)
                vnet = network_client.virtual_networks.get(
                    resource_group_name=resource.id.split('/')[4],
                    virtual_network_name=resource.name
                )
                
                # Function to safely get subnet address space
                def get_subnet_address_space(subnet):
                    # Try different possible property names
                    if hasattr(subnet, 'address_prefix') and subnet.address_prefix:
                        return subnet.address_prefix
                    elif hasattr(subnet, 'address_prefixes') and subnet.address_prefixes:
                        return subnet.address_prefixes[0] if subnet.address_prefixes else None
                    elif hasattr(subnet, 'address_space') and hasattr(subnet.address_space, 'address_prefixes'):
                        return subnet.address_space.address_prefixes[0] if subnet.address_space.address_prefixes else None
                    else:
                        # If we can't find it, try to get it from the properties dictionary
                        try:
                            if hasattr(subnet, 'properties') and subnet.properties:
                                if 'addressPrefix' in subnet.properties:
                                    return subnet.properties['addressPrefix']
                                elif 'addressPrefixes' in subnet.properties:
                                    return subnet.properties['addressPrefixes'][0]
                        except:
                            pass
                        return "Unknown"
                
                resource_info["properties"] = {
                    "address_space": [prefix for prefix in vnet.address_space.address_prefixes],
                    "subnets": [
                        {
                            "name": subnet.name,
                            "address_prefix": get_subnet_address_space(subnet),
                            "network_security_group": subnet.network_security_group.id if subnet.network_security_group else None,
                            "route_table": subnet.route_table.id if subnet.route_table else None,
                            "service_endpoints": [endpoint.service for endpoint in subnet.service_endpoints] if subnet.service_endpoints else [],
                            "delegations": [delegation.service_name for delegation in subnet.delegations] if subnet.delegations else [],
                            "private_endpoint_network_policies": subnet.private_endpoint_network_policies,
                            "private_link_service_network_policies": subnet.private_link_service_network_policies
                        } for subnet in vnet.subnets
                    ] if vnet.subnets else []
                }
            
            # Network Interface
            elif "microsoft.network/networkinterfaces" in resource_type:
                network_client = self.azure_client.get_network_client(subscription_id)
                nic = network_client.network_interfaces.get(
                    resource_group_name=resource.id.split('/')[4],
                    network_interface_name=resource.name
                )
                resource_info["properties"] = {
                    "ip_configurations": [
                        {
                            "name": ip_config.name,
                            "private_ip_address": ip_config.private_ip_address,
                            "private_ip_allocation_method": ip_config.private_ip_allocation_method,
                            "public_ip_address": ip_config.public_ip_address.id if ip_config.public_ip_address else None
                        } for ip_config in nic.ip_configurations
                    ]
                }
            
            # Virtual Machine
            elif "microsoft.compute/virtualmachines" in resource_type:
                compute_client = self.azure_client.get_compute_client(subscription_id)
                vm = compute_client.virtual_machines.get(
                    resource_group_name=resource.id.split('/')[4],
                    vm_name=resource.name
                )
                resource_info["properties"] = {
                    "vm_size": vm.hardware_profile.vm_size,
                    "os_type": vm.storage_profile.os_disk.os_type,
                    "admin_username": vm.os_profile.admin_username if hasattr(vm.os_profile, 'admin_username') else None,
                    "network_interfaces": [nic.id for nic in vm.network_profile.network_interfaces]
                }
            
            # Storage Account
            elif "microsoft.storage/storageaccounts" in resource_type:
                storage_client = self.azure_client.get_storage_client(subscription_id)
                storage = storage_client.storage_accounts.get_properties(
                    resource_group_name=resource.id.split('/')[4],
                    account_name=resource.name
                )
                resource_info["properties"] = {
                    "sku": storage.sku.name,
                    "kind": storage.kind,
                    "access_tier": storage.access_tier,
                    "https_only": storage.enable_https_traffic_only
                }
            
            # SQL Server
            elif "microsoft.sql/servers" in resource_type:
                sql_client = self.azure_client.get_sql_client(subscription_id)
                server = sql_client.servers.get(
                    resource_group_name=resource.id.split('/')[4],
                    server_name=resource.name
                )
                resource_info["properties"] = {
                    "version": server.version,
                    "administrator_login": server.administrator_login,
                    "fully_qualified_domain_name": server.fully_qualified_domain_name
                }
            
            # For other resource types, we keep the basic info only
        
        except Exception as e:
            console.print(f"[yellow]Warning: Could not fetch details for {resource.name}: {str(e)}[/yellow]") 