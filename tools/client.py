"""
Google Ads API Client

HTTP client for making authenticated requests to the Google Ads API.
"""

import os
import json
from typing import Any, Dict, Optional
import requests

from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request


SCOPES = ['https://www.googleapis.com/auth/adwords']
API_VERSION = "v19"


def format_customer_id(customer_id: str) -> str:
    """Format customer ID to ensure it's 10 digits without dashes."""
    customer_id = str(customer_id)
    customer_id = customer_id.replace('\"', '').replace('"', '')
    customer_id = ''.join(char for char in customer_id if char.isdigit())
    return customer_id.zfill(10)


class GoogleAdsClient:
    """Google Ads API Client for making authenticated requests."""

    def __init__(
        self,
        credentials_path: Optional[str] = None,
        developer_token: Optional[str] = None,
        login_customer_id: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ):
        """
        Initialize the Google Ads client.

        Args:
            credentials_path: Path to credentials JSON file
            developer_token: Google Ads developer token
            login_customer_id: Login customer ID for MCC accounts
            client_id: OAuth client ID (if not using credentials file)
            client_secret: OAuth client secret (if not using credentials file)
        """
        self.credentials_path = credentials_path or os.environ.get("GOOGLE_ADS_CREDENTIALS_PATH")
        self.developer_token = developer_token or os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN")
        self.login_customer_id = login_customer_id or os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "")
        self.client_id = client_id or os.environ.get("GOOGLE_ADS_CLIENT_ID")
        self.client_secret = client_secret or os.environ.get("GOOGLE_ADS_CLIENT_SECRET")
        self._credentials = None

        # Detect mock mode based on credentials
        self.using_mock_data = self._detect_mock_mode()

    def _detect_mock_mode(self) -> bool:
        """Detect if we should use mock data based on credentials."""
        mock_patterns = ['mock', 'test', 'demo', 'fake', 'placeholder']

        # Check developer token
        if self.developer_token:
            token_lower = self.developer_token.lower()
            if any(p in token_lower for p in mock_patterns):
                return True

        # Check credentials path
        if self.credentials_path:
            path_lower = self.credentials_path.lower()
            if any(p in path_lower for p in mock_patterns):
                return True
            # Check if file doesn't exist
            if not os.path.exists(self.credentials_path):
                return True

        # If no credentials are configured at all, use mock mode
        if not self.developer_token and not self.credentials_path:
            return True

        return False

    @property
    def base_url(self) -> str:
        return f"https://googleads.googleapis.com/{API_VERSION}"

    def _get_credentials(self) -> Credentials:
        """Get and refresh OAuth credentials."""
        if self._credentials and self._credentials.valid:
            return self._credentials

        creds = None
        client_config = None

        if not self.credentials_path:
            raise ValueError("GOOGLE_ADS_CREDENTIALS_PATH environment variable not set")

        # Check if token file exists and load credentials
        if os.path.exists(self.credentials_path):
            with open(self.credentials_path, 'r') as f:
                creds_data = json.load(f)
                if "installed" in creds_data:
                    client_config = creds_data
                else:
                    creds = Credentials.from_authorized_user_info(creds_data, SCOPES)

        # If credentials don't exist or are invalid, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not client_config:
                    if not self.client_id or not self.client_secret:
                        raise ValueError(
                            "GOOGLE_ADS_CLIENT_ID and GOOGLE_ADS_CLIENT_SECRET must be set "
                            "if no client config file exists"
                        )

                    client_config = {
                        "installed": {
                            "client_id": self.client_id,
                            "client_secret": self.client_secret,
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
                        }
                    }

                flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the credentials
            with open(self.credentials_path, 'w') as f:
                f.write(creds.to_json())

        self._credentials = creds
        return creds

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for Google Ads API requests."""
        if not self.developer_token:
            raise ValueError("GOOGLE_ADS_DEVELOPER_TOKEN environment variable not set")

        creds = self._get_credentials()
        headers = {
            'Authorization': f'Bearer {creds.token}',
            'developer-token': self.developer_token,
            'content-type': 'application/json'
        }

        if self.login_customer_id:
            headers['login-customer-id'] = format_customer_id(self.login_customer_id)

        return headers

    def get(self, endpoint: str) -> Dict[str, Any]:
        """Make a GET request to the Google Ads API."""
        url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers()

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise Exception(f"API Error: {response.text}")

        return response.json()

    def search(
        self,
        customer_id: str,
        query: str,
    ) -> Dict[str, Any]:
        """Execute a GAQL search query."""
        formatted_id = format_customer_id(customer_id)
        url = f"{self.base_url}/customers/{formatted_id}/googleAds:search"
        headers = self._get_headers()

        payload = {"query": query}
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            raise Exception(f"API Error: {response.text}")

        return response.json()

    def mutate(
        self,
        customer_id: str,
        operations: list,
    ) -> Dict[str, Any]:
        """Execute mutate operations (create, update, delete)."""
        formatted_id = format_customer_id(customer_id)
        url = f"{self.base_url}/customers/{formatted_id}/googleAds:mutate"
        headers = self._get_headers()

        payload = {"mutateOperations": operations}
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            raise Exception(f"API Error: {response.text}")

        return response.json()


def create_client(
    credentials_path: Optional[str] = None,
    developer_token: Optional[str] = None,
    login_customer_id: Optional[str] = None,
) -> GoogleAdsClient:
    """
    Create a Google Ads client.

    Args:
        credentials_path: Path to credentials JSON file
        developer_token: Google Ads developer token
        login_customer_id: Login customer ID for MCC accounts

    Returns:
        Configured GoogleAdsClient instance
    """
    return GoogleAdsClient(
        credentials_path=credentials_path,
        developer_token=developer_token,
        login_customer_id=login_customer_id,
    )
