"""COMcheck Client module for simplified API interactions."""

"""Note: Client layer provides user-friendly methods that accept Pydantic models as inputs
and return either Pydantic models, primitives, or raw dicts depending on the operation."""

from typing import Any, Dict, List, Literal, Optional, Union, overload

from comcheck_api.api import COMCheckApiService
from comcheck_api.constants.building_area_constants import DEFAULT_BUILDING_AREA
from comcheck_api.types.api_types import SimulationResultInfo, StatusInfo
from comcheck_api.types.core_types import ComBuilding, InteriorLightingSpace

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
        # Ensure each building area has interiorLightingSpace initialized
        for building_area in data["lighting"]["wholeBldgUse"]:  # type: ignore[index]
            building_area["interiorLightingSpace"] = {
                **DEFAULT_BUILDING_AREA.interiorLightingSpace.model_dump(
                    mode="json", exclude_unset=True
                )
            }

        return self._parse_data(data, mode)

    def list_projects(self) -> Dict[str, Any]:
        """Get a list of all projects.

        Returns:
            API response data as dictionary
        """
        return self._service.get_project_list().get("data", {})

    def update_project(
        self,
        project_id: str,
        project_data: ComBuilding,
        mode: Literal["python", "json"] = "python",
    ) -> ComBuilding | dict[str, Any] | None:
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

        self._service.update_project(project_id, project_data_json).get("data")

        # It's necessary that we call return get_project instead of what's returned from
        # the service's update project due to interiorLightingSpace not being updated correctly
        # when returned from the update call
        return self.get_project(project_id=project_id, mode=mode)

    def _parse_data(self, data, mode):
        if data is None:
            return None
        if mode == "python":
            return ComBuilding(**data)
        return data

    def start_run_simulation(
        self, project: ComBuilding, project_id: Optional[int] = None
    ) -> str:
        """Start a simulation run for a given project.

        Args:
            project: The project data to run the simulation
            project_id: Optional project ID, if not provided, project won't be saved
        Returns:
            Simulation session ID
        """

        # 1. The energy code verification is handled by the start_run_simulation method
        # 2. Before start a simulation, need to check the validation, which is handled by compliance api, and also, need to verify the energy code.
        compliance_result = self._service.compliance(
            project.model_dump(mode="json", exclude_unset=True)
        )
        compliance_data = compliance_result.get("data", {})
        status_keys = [
            "envelopeStatus",
            "interiorLightingStatus",
            "exteriorLightingStatus",
            "renewableStatus",
            "energyCreditStatus",
        ]
        status_messages = [
            compliance_data[key]["statusMessage"]
            for key in status_keys
            if compliance_data.get(key, {}).get("statusMessage") is not None
        ]
        if status_messages:
            raise ValueError("\n".join(status_messages))

        if project_id:
            print("Updating project:", project_id)
            self.update_project(str(project_id), project)

        project_data = project.model_dump(mode="json", exclude_unset=True)
        run_result = self._service.start_run_simulation(project_data).data
        if run_result is None:
            raise RuntimeError("Failed to start simulation: no session data returned.")
        return run_result.sessionId

    def get_simulation_status(self, session_id: str) -> StatusInfo:
        """Get the status of a simulation run by session ID.

        Args:
            session_id: The simulation session ID

        Returns:
            Simulation status information: {sessionId, status, message}
        """
        result = self._service.get_simulation_status(session_id).data
        if result is None:
            raise RuntimeError(
                f"Failed to get simulation status for session '{session_id}'."
            )
        return result

    def get_simulation_result(self, session_id: str) -> SimulationResultInfo:
        """Get the result of a simulation run by session ID.

        Args:
            session_id: The simulation session ID

        Returns:
            Simulation result information: {sessionId, performanceRating, energyCreditPerformanceRating, proposedBpf, baselineBpf}
        """
        result = self._service.get_simulation_result(session_id).data
        if result is None:
            raise RuntimeError(
                f"Failed to get simulation result for session '{session_id}'."
            )
        return result

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
