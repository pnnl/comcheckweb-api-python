"""COMCheck API service module for making HTTP requests to the COMCheck API."""

"""Note: Service layer accepts raw data types (dicts) as inputs to stay simple and
HTTP-library-friendly, but returns validated Pydantic models to provide type safety
and catch API schema mismatches at the boundary."""

import logging
import os
from typing import Any, Dict, Optional

import httpx

from comcheck_api.types.api_types import (
    RunSimulationResponse,
    SimulationStatusResponse,
    SimulationResultResponse,
)


class COMCheckApiService:
    """COMCheck API service class for interacting with the COM API."""

    def __init__(self, api_key: str) -> None:
        """Initialize COMCheck API service.

        Args:
            api_key: API key for authentication

        Raises:
            ValueError: If API key is not provided
        """
        if not api_key:
            raise ValueError(
                "COM_API_KEY is not set. Please provide it as a constructor parameter "
                "or set it in your environment variables."
            )
        self.api_key = api_key
        self.base_url: str = os.getenv(
            "COMCHECK_API_URL", "https://becp-dev.pnl.gov/ahj/COM"
        )
        self._client: Optional[httpx.Client] = None

    def _get_client(self) -> httpx.Client:
        """Get or create HTTP client instance.

        Returns:
            Configured httpx.Client instance
        """
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.base_url,
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
        logger = logging.getLogger(__name__)

        if isinstance(error, httpx.HTTPStatusError):
            logger.error(
                "HTTP error occurred: %s (Status: %s)",
                error,
                error.response.status_code,
                exc_info=True,
                extra={
                    "response_data": error.response.text,
                    "response_headers": dict(error.response.headers),
                },
            )
        elif isinstance(error, httpx.RequestError):
            logger.error(
                "Request error occurred: %s",
                error,
                exc_info=True,
                extra={"request": str(error.request)},
            )
        else:
            logger.error("Unexpected error: %s", error, exc_info=True)

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
