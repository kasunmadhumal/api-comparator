import requests
import json
import time
from typing import Dict, Any, Optional
from requests.auth import HTTPBasicAuth

class APIManager:
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()
    
    def _prepare_headers(self, auth_details: Dict) -> Dict[str, str]:
        """Prepare authentication headers"""
        headers = {"Content-Type": "application/json"}
        
        if auth_details.get('type') == 'bearer':
            headers['Authorization'] = f"Bearer {auth_details['token']}"
        elif auth_details.get('type') == 'api_key':
            headers[auth_details['key_name']] = auth_details['key']
        
        return headers
    
    def _prepare_auth(self, auth_details: Dict) -> Optional[HTTPBasicAuth]:
        """Prepare basic authentication"""
        if auth_details.get('type') == 'basic':
            return HTTPBasicAuth(auth_details['username'], auth_details['password'])
        return None
    
    def execute_request(self, config: Dict, payload: Dict = None, 
                       query_params: str = "") -> Dict[str, Any]:
        """
        Execute an API request
        
        Args:
            config: API configuration dictionary
            payload: Request payload (for POST, PUT)
            query_params: Query parameters string (for GET)
        
        Returns:
            Dictionary containing response data, status code, and response time
        """
        try:
            # Parse authentication details
            auth_details = json.loads(config.get('auth_details', '{}'))
            
            # Prepare headers and authentication
            headers = self._prepare_headers(auth_details)
            auth = self._prepare_auth(auth_details)
            
            # Prepare URL
            url = config['api_url']
            if query_params and config['method'] == 'GET':
                url = f"{url}?{query_params}"
            
            # Start timer
            start_time = time.time()
            
            # Execute request based on method
            method = config['method'].upper()
            
            if method == 'GET':
                response = self.session.get(
                    url,
                    headers=headers,
                    auth=auth,
                    timeout=self.timeout
                )
            elif method == 'POST':
                response = self.session.post(
                    url,
                    json=payload,
                    headers=headers,
                    auth=auth,
                    timeout=self.timeout
                )
            elif method == 'PUT':
                response = self.session.put(
                    url,
                    json=payload,
                    headers=headers,
                    auth=auth,
                    timeout=self.timeout
                )
            elif method == 'DELETE':
                response = self.session.delete(
                    url,
                    headers=headers,
                    auth=auth,
                    timeout=self.timeout
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Try to parse JSON response
            try:
                response_body = response.json()
            except json.JSONDecodeError:
                response_body = {"raw_response": response.text}
            
            return {
                "status_code": response.status_code,
                "body": response_body,
                "response_time": response_time,
                "headers": dict(response.headers)
            }
        
        except requests.exceptions.Timeout:
            return {
                "status_code": 0,
                "body": {"error": "Request timeout"},
                "response_time": self.timeout,
                "headers": {}
            }
        except requests.exceptions.ConnectionError as e:
            return {
                "status_code": 0,
                "body": {"error": f"Connection error: {str(e)}"},
                "response_time": 0,
                "headers": {}
            }
        except Exception as e:
            return {
                "status_code": 0,
                "body": {"error": f"Unexpected error: {str(e)}"},
                "response_time": 0,
                "headers": {}
            }
    
    def batch_execute(self, config: Dict, payloads: list) -> list:
        """
        Execute multiple requests with different payloads
        
        Args:
            config: API configuration
            payloads: List of payloads to test
        
        Returns:
            List of response dictionaries
        """
        results = []
        for payload in payloads:
            result = self.execute_request(config, payload)
            results.append(result)
        return results
