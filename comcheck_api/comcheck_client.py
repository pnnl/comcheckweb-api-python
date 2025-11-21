"""COMcheck Client module for simplified API interactions."""

from typing import Any, Dict, Optional

from comcheck_api.api.api_services import COMCheckApiService
from comcheck_api.constants.building_area_constants import DEFAULT_BUILDING_AREA


class COMcheckClient:
    """COMcheck Client class for simplified project operations."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize COMcheck client.

        Args:
            api_key: Optional API key for authentication. Can be set later with set_api_key()
        """
        self._api_service: Optional[COMCheckApiService] = None
        if api_key:
            self.set_api_key(api_key)

    def set_api_key(self, api_key: str) -> None:
        """Set the API key and initialize the API service.

        Args:
            api_key: API key for authentication

        Raises:
            ValueError: If API key is not provided
        """
        if not api_key:
            raise ValueError("API key is required.")
        self._api_service = COMCheckApiService(api_key)

    @property
    def _service(self) -> COMCheckApiService:
        """Get the API service instance.

        Returns:
            COMCheckApiService instance

        Raises:
            RuntimeError: If API key has not been set
        """
        if self._api_service is None:
            raise RuntimeError(
                "API key not set. Call set_api_key() before using the client."
            )
        return self._api_service

    def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get a single project by ID.

        Args:
            project_id: The project ID to retrieve

        Returns:
            API response data as dictionary
        """
        return self._service.get_project(project_id)

    def list_projects(self) -> Dict[str, Any]:
        """Get a list of all projects.

        Returns:
            API response data as dictionary
        """
        return self._service.get_project_list()

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
            ValueError: If project is not found
        """
        # Get existing project
        old_project = self.get_project(project_id)

        if "data" not in old_project:
            raise ValueError(f"Project with ID {project_id} not found.")

        # Preserve user project reference
        user_project = old_project["data"]["userProject"]
        project_data["userProject"] = user_project

        # Preserve IDs from existing project
        project_data["envelope"]["id"] = old_project["data"]["envelope"]["id"]
        project_data["lighting"]["id"] = old_project["data"]["lighting"]["id"]
        project_data["hvac"]["id"] = old_project["data"]["hvac"]["id"]

        # Ensure each building area has interiorLightingSpace initialized
        for building_area in project_data["lighting"]["wholeBldgUse"]:
            building_area["interiorLightingSpace"] = {
                **DEFAULT_BUILDING_AREA["interiorLightingSpace"]
            }

        return self._service.update_project(project_id, project_data)

    def close(self) -> None:
        """Close the API service connection."""
        if self._api_service is not None:
            self._api_service.close()

    def __enter__(self) -> "COMcheckClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()
