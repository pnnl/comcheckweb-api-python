"""COMCheck API service module for making HTTP requests to the COMCheck API."""

import os
from typing import Any, Callable, Dict, Literal, Optional
from urllib.parse import urlencode
import logging

from comcheck_api.types.api_types import (
    AssembliesUValuesArgs,
    EndpointCallArgs,
)
import httpx
import requests

from comcheck_api.types.api_types import (
    RunSimulationResponse,
    SimulationStatusResponse,
    SimulationResultResponse,
)


class COMCheckApiService:
    """COMCheck API service class for interacting with the COM API."""

    BASE_URL: str = "https://becp-dev.pnl.gov/ahj/COM"  # COM API base URL

    def __init__(self, api_key: str = None) -> None:
        """Initialize COMCheck API service.

        Args:
            api_key: API key for authentication

        Raises:
            ValueError: If API key is not provided
        """
        if api_key is None:
            api_key = os.getenv("COM_API_KEY")
        if not api_key:
            raise ValueError(
                "COM_API_KEY is not set. Please provide it as a constructor parameter "
                "or set it in your environment variables."
            )
        self.api_key = api_key
        self._client: Optional[httpx.Client] = None
        self.session = requests.Session()

        self._define_endpoints()

    def _define_endpoints(self):
        self.endpoints = {
            "allowed_wattage": AHJEndpoint(
                "/{code_version}/activity-use/allowed-wattage",
            ),
            "water_heater_efficiency": AHJEndpoint(
                "/{code_version}/mechanical/water-heaters/efficiency",
            ),
            "hvac_system_efficiency": AHJEndpoint(
                "/{code_version}/mechanical/hvac-systems/efficiency",
            ),
            "hvac_plant_efficiency": AHJEndpoint(
                "/{code_version}/mechanical/plants/efficiency",
            ),
            "assemblies_u_values": AHJEndpoint(
                "/{code_version}/assemblies/uvalues",
            ),
        }

    def _get_client(self) -> httpx.Client:
        """Get or create HTTP client instance.

        Returns:
            Configured httpx.Client instance
        """
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.BASE_URL,
                headers=self._prepare_headers(),
                timeout=30.0,
            )
        return self._client

    def _prepare_headers(self) -> Dict[str, str]:
        """Prepare headers for API requests.

        Returns:
            HTTP headers dictionary
        """
        return {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _handle_api_error(self, error: Exception) -> None:
        """Handle API errors with detailed logging.

        Args:
            error: The error object to handle
        """
        if isinstance(error, httpx.HTTPStatusError):
            print(f"HTTP error occurred: {error}")
            print(f"Status: {error.response.status_code}")
            print(f"Response data: {error.response.text}")
            print(f"Response headers: {error.response.headers}")
        elif isinstance(error, httpx.RequestError):
            print(f"Request error occurred: {error}")
            print(f"Request: {error.request}")
        else:
            print(f"Unexpected error: {error}")

    def call_endpoint(
        self,
        args: EndpointCallArgs,
    ) -> Dict[str, Any]:
        """
        Generic method to call any configured endpoint.

        Args:
            endpoint_name: Key from self.endpoints
            path_params: Path parameters for URL template (e.g., {"code_version": "2021"})
            query_params: Query parameters for URL template (e.g., {"code_version": "2021"})
            payload: Direct payload dict
        """
        if not self.api_key:
            return self._handle_api_error("Missing AHJ_API_KEY")

        if args.endpoint_name not in self.endpoints:
            print(args.endpoint_name, self.endpoints)
            return self._handle_api_error(f"Unknown endpoint: {args.endpoint_name}")

        endpoint = self.endpoints[args.endpoint_name]
        try:
            path = endpoint.path_template.format(**(args.path_params or {}))
            url = f"{self.BASE_URL}{path}"

            if args.query_params:
                query_string = urlencode(args.query_params)
                url = f"{url}?{query_string}"

        except KeyError as e:
            return self._handle_api_error("Missing path parameter")

        headers = self._prepare_headers()

        logging.info(
            "Calling %s %s | payload=%s | query=%s",
            endpoint.method,
            path,
            args.payload,
            args.query_params,
        )

        try:
            resp = self.session.request(
                endpoint.method, url, headers=headers, json=args.payload
            )
        except Exception as e:
            return self._handle_api_error(e)

        return resp

    def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get a single project by ID.

        Args:
            project_id: The project ID to retrieve

        Returns:
            API response data as dictionary

        Raises:
            httpx.HTTPStatusError: If the API returns an error status
            httpx.RequestError: If the request fails
        """
        try:
            client = self._get_client()
            response = client.get(f"/project/{project_id}")
            response.raise_for_status()
            return response.json()
        except Exception as error:
            self._handle_api_error(error)
            raise

    def get_project_list(self) -> Dict[str, Any]:
        """Get a list of all projects.

        Returns:
            API response data as dictionary

        Raises:
            httpx.HTTPStatusError: If the API returns an error status
            httpx.RequestError: If the request fails
        """
        try:
            client = self._get_client()
            response = client.get("/projects")
            response.raise_for_status()
            return response.json()
        except Exception as error:
            self._handle_api_error(error)
            raise

    def update_project(
        self, project_id: str, project_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a project by ID.

        Args:
            project_id: The project ID to update
            project_data: The project data to send in the request body

        Returns:
            API response data as dictionary

        Raises:
            httpx.HTTPStatusError: If the API returns an error status
            httpx.RequestError: If the request fails
        """
        try:
            client = self._get_client()
            response = client.put(f"/project/{project_id}", json=project_data)
            response.raise_for_status()
            return response.json()
        except Exception as error:
            self._handle_api_error(error)
            raise

    def get_assemblies_u_values(
        self, code_version: str, payload: AssembliesUValuesArgs
    ) -> Dict[str, Any]:
        """Convenience method for retrieving U values for assemblies"""
        args = EndpointCallArgs(
            endpoint_name="assemblies_u_values",
            path_params={"code_version": code_version},
            payload=payload,
        )
        return self.call_endpoint(args)
    
    def start_run_simulation(
        self, project_data: Dict[str, Any]
    ) -> RunSimulationResponse:
        """Start a simulation.

        Args:
            project_data: The project data to send in the request body

        Returns:
            RunSimulationResponse with session information

        Raises:
            httpx.HTTPStatusError: If the API returns an error status
            httpx.RequestError: If the request fails
        """
        try:
            client = self._get_client()
            response = client.post(
                f"/compliance/start-run-simulation", json=project_data
            )
            response.raise_for_status()
            return RunSimulationResponse.model_construct(**response.json())
        except Exception as error:
            self._handle_api_error(error)
            raise

    def get_simulation_status(self, session_id: str) -> SimulationStatusResponse:
        """Get status of a simulation.

        Args:
            session_id: The session ID of the simulation

        Returns:
            SimulationStatusResponse with status information

        Raises:
            httpx.HTTPStatusError: If the API returns an error status
            httpx.RequestError: If the request fails
        """
        try:
            client = self._get_client()
            response = client.get(
                f"/compliance/get-status-simulation?sessionId={session_id}"
            )
            response.raise_for_status()
            return SimulationStatusResponse.model_construct(**response.json())
        except Exception as error:
            self._handle_api_error(error)
            raise

    def get_simulation_result(self, session_id: str) -> SimulationResultResponse:
        """Get result of a simulation.

        Args:
            session_id: The session ID of the simulation

        Returns:
            SimulationResultResponse with simulation results

        Raises:
            httpx.HTTPStatusError: If the API returns an error status
            httpx.RequestError: If the request fails
        """
        try:
            client = self._get_client()
            response = client.get(
                f"/compliance/get-result-simulation?sessionId={session_id}"
            )
            response.raise_for_status()
            return SimulationResultResponse.model_construct(**response.json())
        except Exception as error:
            self._handle_api_error(error)
            raise

    def close(self) -> None:
        """Close the HTTP client connection."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self) -> "COMCheckApiService":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()


class AHJEndpoint:
    """Configuration for an AHJ API endpoint."""

    def __init__(
        self,
        path_template: str,
        method: Literal["GET", "POST", "PUT", "DELETE"] = "POST",
        response_parser: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    ):
        self.path_template = path_template
        self.method = method
        self.response_parser = response_parser or self._default_parser

    def _default_parser(self, response_body: Dict[str, Any]) -> Dict[str, Any]:
        return response_body.get("data", response_body)
