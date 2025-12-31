"""COMCheck API service module for making HTTP requests to the COMCheck API."""

import os
from typing import Any, Dict, Literal, Optional
import logging
import httpx

from comcheck_api.types.api_types import (
    AssembliesUValuesArgs,
    EndpointCallArgs,
    RunSimulationResponse,
    SimulationStatusResponse,
    SimulationResultResponse,
)

logger = logging.getLogger(__name__)

TimeoutLike = httpx.Timeout | float | None

class COMCheckApiService:
    """COMCheck API service class for interacting with the COM API."""

    BASE_URL: str = "https://becp-dev.pnl.gov/ahj/COM"  # COM API base URL'
    DEFAULT_TIMEOUT: float = 30.0

    def __init__(self, api_key: str = None,  timeout: TimeoutLike = None) -> None:
        """Initialize COMCheck API service.

        Args:
            api_key: API key for authentication
            timeout: HTTP client timeout configuration
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
        self.timeout = timeout if isinstance(timeout, httpx.Timeout) else httpx.Timeout(timeout or self.DEFAULT_TIMEOUT)
        self.api_key = api_key
        self._client: Optional[httpx.Client] = None

        self._define_endpoints()

    def _define_endpoints(self):
        self.endpoints = {
            "get_project": AHJEndpoint(
                "/project/{project_id}",
                "GET"
            ),
            "update_project": AHJEndpoint(
                "/project/{project_id}",
                "PUT"
            ),
            "get_project_list": AHJEndpoint(
                "/projects",
                "GET"
            ),
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
            "run_simulation": AHJEndpoint(
                "/compliance/start-run-simulation",
            ),
            "get_simulation_status": AHJEndpoint(
                "/compliance/get-status-simulation",
                "GET",
            ),
            "get_simulation_result": AHJEndpoint(
                "/compliance/get-result-simulation",
                "GET",
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
                timeout=self.timeout,
            )
        return self._client
    
    def close(self) -> None:
        """Close the HTTP client connection."""
        if self._client is not None:
            self._client.close()
            self._client = None

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
            logger.error(f"HTTP error occurred: {error}")
            logger.error(f"Status: {error.response.status_code}")
            logger.error(f"Response data: {error.response.text}")
            logger.error(f"Response headers: {error.response.headers}")
        elif isinstance(error, httpx.RequestError):
            logger.error(f"Request error occurred: {error}")
            logger.error(f"Request: {error.request}")
        else:
            logger.error(f"Unexpected error: {error}")

    def call_endpoint(
        self,
        args: EndpointCallArgs,
    ) -> Dict[str, Any]:
        """
        Generic method to call any configured endpoint.

        Args:
            args: EndpointCallArgs containing endpoint name, path params, query params, and payload
        """
        if args.endpoint_name not in self.endpoints:
            error = ValueError(f"Unknown endpoint: {args.endpoint_name}")
            self._handle_api_error(error)
            raise error

        endpoint = self.endpoints[args.endpoint_name]

        try:
            path = endpoint.path_template.format(**(args.path_params or {}))
        except KeyError as exc:
            missing = exc.args[0]
            raise ValueError(f"Missing required path parameter: {missing}") from exc

        logger.info(
            "Calling %s %s | payload=%s | query=%s",
            endpoint.method,
            path,
            args.payload,
            args.query_params,
        )

        json_payload = args.payload
        if hasattr(json_payload, "model_dump"):
            json_payload = json_payload.model_dump(mode="json")

        return self._request(
            endpoint.method,
            path,
            json=json_payload,
            params=args.query_params,
        )

    def _request(
        self,
        method: str,
        url: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        client = self._get_client()

        try:
            response = client.request(
                method,
                url,
                json=json,
                params=params,
            )
            response.raise_for_status()
        except Exception as error:
            self._handle_api_error(error)
            raise

        return response.json()

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
        args = EndpointCallArgs(
            endpoint_name="get_project",
            path_params={"project_id": project_id},
        )
        return self.call_endpoint(args)

    def get_project_list(self) -> Dict[str, Any]:
        """Get a list of all projects.

        Returns:
            API response data as dictionary

        Raises:
            httpx.HTTPStatusError: If the API returns an error status
            httpx.RequestError: If the request fails
        """
        args = EndpointCallArgs(
            endpoint_name="get_project_list",
        )
        return self.call_endpoint(args)

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
        args = EndpointCallArgs(
            endpoint_name="update_project",
            path_params={"project_id": project_id},
            payload=project_data,
        )
        return self.call_endpoint(args)

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
        args = EndpointCallArgs(
            endpoint_name="run_simulation",
            payload=project_data,
        )
        return RunSimulationResponse(**self.call_endpoint(args))

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
        args = EndpointCallArgs(    
            endpoint_name="get_simulation_status",
            path_params={"session_id": session_id},
        )
        return SimulationStatusResponse(**self.call_endpoint(args))

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
        args = EndpointCallArgs(
            endpoint_name="get_simulation_result",
            path_params={"session_id": session_id},
        )
        return SimulationResultResponse(**self.call_endpoint(args))

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
    ):
        self.path_template = path_template
        self.method = method

