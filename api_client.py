"""
Google Ads API Client

Provides authentication and API request functionality for Google Ads.
Used by both the MCP server and CLI tools.
"""

import os
import json
import requests
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List

from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('google_ads_client')

# Constants
SCOPES = ['https://www.googleapis.com/auth/adwords']
API_VERSION = "v19"


def format_customer_id(customer_id: str) -> str:
    """Format customer ID to ensure it's 10 digits without dashes."""
    customer_id = str(customer_id)
    customer_id = customer_id.replace('\"', '').replace('"', '')
    customer_id = ''.join(char for char in customer_id if char.isdigit())
    return customer_id.zfill(10)


class GoogleAdsClient:
    """Client for Google Ads API operations."""

    def __init__(
        self,
        credentials_path: Optional[str] = None,
        developer_token: Optional[str] = None,
        login_customer_id: Optional[str] = None,
        auth_type: str = "oauth"
    ):
        self.credentials_path = credentials_path or os.environ.get("GOOGLE_ADS_CREDENTIALS_PATH")
        self.developer_token = developer_token or os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN")
        self.login_customer_id = login_customer_id or os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "")
        self.auth_type = auth_type or os.environ.get("GOOGLE_ADS_AUTH_TYPE", "oauth")
        self._credentials = None

    @property
    def credentials(self):
        """Get or refresh credentials."""
        if self._credentials is None:
            self._credentials = self._get_credentials()
        return self._credentials

    def _get_credentials(self):
        """Get credentials based on auth type."""
        if not self.credentials_path:
            raise ValueError("GOOGLE_ADS_CREDENTIALS_PATH not set")

        # Check if auth type is service_account OR if the file looks like a service account
        if self.auth_type.lower() == "service_account":
            return self._get_service_account_credentials()

        # Auto-detect service account file
        if os.path.exists(self.credentials_path):
            try:
                with open(self.credentials_path, 'r') as f:
                    creds_data = json.load(f)
                    if creds_data.get('type') == 'service_account':
                        logger.info("Auto-detected service account credentials file")
                        return self._get_service_account_credentials()
            except Exception:
                pass

        return self._get_oauth_credentials()

    def _get_service_account_credentials(self):
        """Get credentials using a service account key file."""
        logger.info(f"Loading service account credentials from {self.credentials_path}")

        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(f"Service account key file not found at {self.credentials_path}")

        credentials = service_account.Credentials.from_service_account_file(
            self.credentials_path,
            scopes=SCOPES
        )

        impersonation_email = os.environ.get("GOOGLE_ADS_IMPERSONATION_EMAIL")
        if impersonation_email:
            logger.info(f"Impersonating user: {impersonation_email}")
            credentials = credentials.with_subject(impersonation_email)

        return credentials

    def _get_oauth_credentials(self):
        """Get and refresh OAuth user credentials."""
        creds = None
        client_config = None
        token_path = self.credentials_path

        if os.path.exists(token_path):
            try:
                with open(token_path, 'r') as f:
                    creds_data = json.load(f)
                    if "installed" in creds_data or "web" in creds_data:
                        client_config = creds_data
                    else:
                        creds = Credentials.from_authorized_user_info(creds_data, SCOPES)
            except (json.JSONDecodeError, Exception) as e:
                logger.warning(f"Error loading credentials: {str(e)}")
                creds = None

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except RefreshError:
                    creds = None

            if not creds:
                if not client_config:
                    client_id = os.environ.get("GOOGLE_ADS_CLIENT_ID")
                    client_secret = os.environ.get("GOOGLE_ADS_CLIENT_SECRET")

                    if not client_id or not client_secret:
                        raise ValueError("GOOGLE_ADS_CLIENT_ID and GOOGLE_ADS_CLIENT_SECRET must be set")

                    client_config = {
                        "installed": {
                            "client_id": client_id,
                            "client_secret": client_secret,
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
                        }
                    }

                flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
                creds = flow.run_local_server(port=0)

            try:
                os.makedirs(os.path.dirname(token_path), exist_ok=True)
                with open(token_path, 'w') as f:
                    f.write(creds.to_json())
            except Exception as e:
                logger.warning(f"Could not save credentials: {str(e)}")

        return creds

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        if not self.developer_token:
            raise ValueError("GOOGLE_ADS_DEVELOPER_TOKEN not set")

        creds = self.credentials

        if isinstance(creds, service_account.Credentials):
            auth_req = Request()
            creds.refresh(auth_req)
            token = creds.token
        else:
            if not creds.valid:
                if creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    raise ValueError("OAuth credentials are invalid")
            token = creds.token

        headers = {
            'Authorization': f'Bearer {token}',
            'developer-token': self.developer_token,
            'content-type': 'application/json'
        }

        if self.login_customer_id:
            headers['login-customer-id'] = format_customer_id(self.login_customer_id)

        return headers

    def query(self, customer_id: str, query: str) -> Dict[str, Any]:
        """Execute a GAQL query."""
        formatted_id = format_customer_id(customer_id)
        url = f"https://googleads.googleapis.com/{API_VERSION}/customers/{formatted_id}/googleAds:search"

        response = requests.post(url, headers=self._get_headers(), json={"query": query})

        if response.status_code != 200:
            raise Exception(f"API error: {response.text}")

        return response.json()

    def get(self, endpoint: str, params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Make a GET request to the API."""
        url = f"https://googleads.googleapis.com/{API_VERSION}/{endpoint}"
        response = requests.get(url, headers=self._get_headers(), params=params)

        if response.status_code != 200:
            raise Exception(f"API error: {response.text}")

        return response.json()

    def list_accessible_customers(self) -> List[str]:
        """List all accessible customer accounts."""
        url = f"https://googleads.googleapis.com/{API_VERSION}/customers:listAccessibleCustomers"
        response = requests.get(url, headers=self._get_headers())

        if response.status_code != 200:
            raise Exception(f"API error: {response.text}")

        data = response.json()
        return [name.split('/')[-1] for name in data.get('resourceNames', [])]


def create_client(
    credentials_path: Optional[str] = None,
    developer_token: Optional[str] = None,
    login_customer_id: Optional[str] = None,
    auth_type: Optional[str] = None
) -> GoogleAdsClient:
    """Create a Google Ads client instance."""
    return GoogleAdsClient(
        credentials_path=credentials_path,
        developer_token=developer_token,
        login_customer_id=login_customer_id,
        auth_type=auth_type or "oauth"
    )
