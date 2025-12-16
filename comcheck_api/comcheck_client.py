"""COMcheck Client module for simplified API interactions."""

"""Note: Client layer provides user-friendly methods that accept Pydantic models as inputs
and return either Pydantic models, primitives, or raw dicts depending on the operation."""

from typing import Any, Dict, List, Literal, Optional, Union, overload

from comcheck_api.api.api_services import COMCheckApiService
from comcheck_api.constants.building_area_constants import DEFAULT_BUILDING_AREA
from comcheck_api.types.api_types import SimulationResultInfo, StatusInfo
from comcheck_api.types.core_types import ComBuilding

Mode = Literal["python", "json"]


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

    @overload
    def get_project(
        self,
        project_id: str,
        mode: Literal["python"] = "python",
    ) -> Optional["ComBuilding"]: ...

    @overload
    def get_project(
        self,
        project_id: str,
        mode: Literal["json"],
    ) -> Optional[Dict[str, Any]]: ...

    def get_project(
        self,
        project_id: str,
        mode: Literal["python", "json"] = "python",
    ) -> Optional[Union["ComBuilding", Dict[str, Any]]]:
        resp = self._service.get_project(project_id)
        data = resp.get("data")
        for building_area in data["lighting"]["wholeBldgUse"]:
            building_area["interiorLightingSpace"] = {
                **DEFAULT_BUILDING_AREA.interiorLightingSpace.model_dump(
                    mode="json", exclude_unset=True
                )
            }

        if data is None:
            return None
        if mode == "python":
            return ComBuilding(**data)
        return data

    def list_projects(self) -> Dict[str, Any]:
        """Get a list of all projects.

        Returns:
            API response data as dictionary
        """
        return self._service.get_project_list().get("data", {})

    def update_project(
        self, project_id: str, project_data: ComBuilding
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
        old_project = self.get_project(project_id, mode="json")

        if not old_project:
            raise ValueError(f"Project with ID {project_id} not found.")

        project_data_json = project_data.model_dump(mode="json", exclude_unset=True)

        # Preserve user project reference
        user_project = old_project["userProject"]
        project_data_json["userProject"] = user_project

        # Preserve IDs from existing project
        for section in [
            "envelope",
            "lighting",
            "hvac",
            "control",
            "project",
            "location",
            "renewable",
        ]:
            project_data_json[section]["id"] = old_project[section]["id"]
        project_data_json["id"] = old_project["id"]

        # Ensure each building area has interiorLightingSpace initialized
        for building_area in project_data_json["lighting"]["wholeBldgUse"]:
            building_area["interiorLightingSpace"] = {
                **DEFAULT_BUILDING_AREA.interiorLightingSpace.model_dump(
                    mode="json", exclude_unset=True
                )
            }

        # TODO: need to verify if other componets also need to remove None IDs (auto-generated through pydantic )
        # Remove None IDs from envelope components
        if "envelope" in project_data_json:
            envelope = project_data_json["envelope"]
            for component_type in [
                "roof",
                "agWall",
                "bgWall",
                "floor",
                "skylight",
                "window",
                "door",
            ]:
                if component_type in envelope and isinstance(
                    envelope[component_type], list
                ):
                    for component in envelope[component_type]:
                        if isinstance(component, dict) and component.get("id") is None:
                            component.pop("id", None)
                        # Also remove None IDs from nested components (skylights in roofs, windows/doors in walls)
                        if component_type == "roof" and "skylight" in component:
                            for skylight in component.get("skylight", []):
                                if (
                                    isinstance(skylight, dict)
                                    and skylight.get("id") is None
                                ):
                                    skylight.pop("id", None)
                        elif component_type in ["agWall", "bgWall"]:
                            for nested_type in ["window", "door", "thermalBridge"]:
                                if nested_type in component:
                                    for nested in component.get(nested_type, []):
                                        if (
                                            isinstance(nested, dict)
                                            and nested.get("id") is None
                                        ):
                                            nested.pop("id", None)

        return self._service.update_project(project_id, project_data_json)

    def start_run_simulation(self, project: ComBuilding) -> str:
        """Start a simulation run for a given project ID.

        Args:
            project: The project data to run the simulation
        Returns:
            Simulation session ID
        """
        project_data = project.model_dump(mode="json", exclude_unset=True)
        return self._service.start_run_simulation(project_data).data.sessionId

    def get_simulation_status(self, sessionId: str) -> StatusInfo:
        """Get the status of a simulation run by session ID.

        Args:
            sessionId: The simulation session ID

        Returns:
            Simulation status information
        """
        return self._service.get_simulation_status(sessionId).data

    def get_simulation_result(self, sessionId: str) -> SimulationResultInfo:
        """Get the result of a simulation run by session ID.

        Args:
            sessionId: The simulation session ID

        Returns:
            Simulation result information
        """
        return self._service.get_simulation_result(sessionId).data

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
