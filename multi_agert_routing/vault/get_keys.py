import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

class KeyVaultClient:
    def __init__(self, key_vault_name: str):
        # Construct the Key Vault URI from the Key Vault name
        self.vault_uri = f"https://{key_vault_name}.vault.azure.net/"
        # Use DefaultAzureCredential to authenticate via managed identity or other methods
        self.credential = DefaultAzureCredential()
        # Create a SecretClient to interact with Key Vault
        self.client = SecretClient(vault_url=self.vault_uri, credential=self.credential)

    def get_secret(self, secret_name: str):
        """
        Fetches the secret value from Key Vault by the given secret name.
        """
        try:
            # Retrieve the secret from the Key Vault
            retrieved_secret = self.client.get_secret(secret_name)
            return retrieved_secret.value
        except Exception as e:
            print(f"Failed to retrieve secret '{secret_name}': {str(e)}")
            return None

