"""
Azure client for authentication and accessing resources
"""
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
from azure.mgmt.resource import ResourceManagementClient, SubscriptionClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.sql import SqlManagementClient
from azure.core.exceptions import ClientAuthenticationError
from rich.console import Console

console = Console()

class AzureClient:
    """Client for accessing Azure resources"""
    
    def __init__(self, interactive=True):
        self.interactive = interactive
        self.credential = None
        self.tenant_id = None
        self.resource_clients = {}
        self.network_clients = {}
        self.compute_clients = {}
        self.storage_clients = {}
        self.sql_clients = {}
    
    def login(self):
        """Login to Azure interactively or use default credentials"""
        if self.interactive:
            try:
                console.print("[yellow]Launching browser for interactive Azure login...[/yellow]")
                self.credential = InteractiveBrowserCredential()
                # Force authentication to happen now
                subscription_client = SubscriptionClient(self.credential)
                tenants = list(subscription_client.tenants.list())
                return True
            except Exception as e:
                console.print(f"[red]Error during interactive login: {str(e)}[/red]")
                console.print("[yellow]Falling back to default credentials...[/yellow]")
        
        # Use default credentials as fallback or if not interactive
        try:
            self.credential = DefaultAzureCredential()
            # Test the credential
            subscription_client = SubscriptionClient(self.credential)
            tenants = list(subscription_client.tenants.list())
            return True
        except Exception as e:
            console.print(f"[red]Authentication error: {str(e)}[/red]")
            return False
    
    def get_tenants(self):
        """Get available Azure tenants"""
        if not self.credential:
            if not self.login():
                return []
        
        try:
            subscription_client = SubscriptionClient(self.credential)
            tenants = []
            
            for tenant in subscription_client.tenants.list():
                tenants.append((tenant.tenant_id, tenant.display_name or tenant.tenant_id))
            
            return tenants
        except Exception as e:
            console.print(f"[red]Error retrieving tenants: {str(e)}[/red]")
            return []
    
    def set_tenant(self, tenant_id):
        """Set the current tenant ID"""
        self.tenant_id = tenant_id
        # Clear clients when changing tenant
        self.resource_clients = {}
        self.network_clients = {}
        self.compute_clients = {}
        self.storage_clients = {}
        self.sql_clients = {}
        
        # Re-create credential for specific tenant
        if self.interactive:
            try:
                self.credential = InteractiveBrowserCredential(tenant_id=tenant_id)
            except Exception:
                console.print("[yellow]Error with tenant-specific credential, using default credential[/yellow]")
                self.credential = DefaultAzureCredential()
        else:
            self.credential = DefaultAzureCredential()
    
    def get_subscriptions(self):
        """Get all available subscriptions for the current tenant"""
        if not self.credential:
            if not self.login():
                return []
        
        try:
            subscription_client = SubscriptionClient(self.credential)
            subscriptions = []
            
            for sub in subscription_client.subscriptions.list():
                subscriptions.append((sub.subscription_id, sub.display_name or sub.subscription_id))
            
            return subscriptions
        except ClientAuthenticationError as e:
            console.print(f"[red]Authentication error: {str(e)}[/red]")
            return []
    
    def get_resource_client(self, subscription_id):
        """Get or create a resource client for the given subscription"""
        if subscription_id not in self.resource_clients:
            self.resource_clients[subscription_id] = ResourceManagementClient(
                self.credential, subscription_id)
        return self.resource_clients[subscription_id]
    
    def get_network_client(self, subscription_id):
        """Get or create a network client for the given subscription"""
        if subscription_id not in self.network_clients:
            self.network_clients[subscription_id] = NetworkManagementClient(
                self.credential, subscription_id)
        return self.network_clients[subscription_id]
    
    def get_compute_client(self, subscription_id):
        """Get or create a compute client for the given subscription"""
        if subscription_id not in self.compute_clients:
            self.compute_clients[subscription_id] = ComputeManagementClient(
                self.credential, subscription_id)
        return self.compute_clients[subscription_id]
    
    def get_storage_client(self, subscription_id):
        """Get or create a storage client for the given subscription"""
        if subscription_id not in self.storage_clients:
            self.storage_clients[subscription_id] = StorageManagementClient(
                self.credential, subscription_id)
        return self.storage_clients[subscription_id]
    
    def get_sql_client(self, subscription_id):
        """Get or create a SQL client for the given subscription"""
        if subscription_id not in self.sql_clients:
            self.sql_clients[subscription_id] = SqlManagementClient(
                self.credential, subscription_id)
        return self.sql_clients[subscription_id] 