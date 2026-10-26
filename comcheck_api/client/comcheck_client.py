"""COMcheck Client module for simplified API interactions."""

"""Note: Client layer provides user-friendly methods that accept Pydantic models as inputs
and return either Pydantic models, primitives, or raw dicts depending on the operation."""

import logging
import os
from typing import Any, Dict, List, Literal, Optional, Union, overload

import httpx

from comcheck_api.api import COMCheckApiService
from comcheck_api.exceptions import (
    COMCheckAPIError,
    COMCheckProjectNotFoundError,
    COMCheckSimulationError,
)
from comcheck_api.types.api_types import (
    EnergyCreditResult,
    WaterHeaterEfficiency,
    HVACSystemEfficiency,
    EconomizerValidation,
    PlantEfficiency,
    FanSystemComplianceResult,
)
from comcheck_api.types.common_types import InteriorSpace
from comcheck_api.types.core_types import (
    ComBuilding,
    ServiceWaterHeatingSystem,
    HVACSystem,
    HVACPlant,
    FanSystem,
    FanSystemPressureDropCredits,
    Fan,
)

Mode = Literal["python", "json"]


def _optional_float(value: Any) -> Optional[float]:
    """Convert an API numeric value to ``float``, passing ``None`` through."""
    return None if value is None else float(value)


class COMcheckClient:
    """High-level client for the COMcheck Web API.

    Provides user-friendly methods that accept Pydantic models as inputs
    and return either :class:`~comcheck_api.types.core_types.ComBuilding`
    models, primitives, or raw dicts depending on the operation.

    Can be used as a context manager to ensure the underlying HTTP
    connection is closed::

        with COMcheckClient(api_key="your-key") as client:
            project = client.get_project("123")

    Example:
        ```python
        client = COMcheckClient(api_key="your-key")
        projects = client.list_projects()
        project = client.get_project(projects[0]["projectId"])
        client.close()
        ```
    """

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
        """Fetch a single project by ID.

        Args:
            project_id: The project ID to retrieve.
            mode: ``"python"`` returns a ``ComBuilding`` model; ``"json"`` returns a raw dict.

        Returns:
            The project as a ``ComBuilding`` or dict, or ``None`` if not found.
        """
        resp = self._service.get_project(project_id)
        data = resp.get("data")
        return self._parse_data(data, mode)

    def list_projects(self) -> List[Dict[str, Any]]:
        """Get a list of all projects.

        Returns:
            API response data as list of project dictionaries
        """
        return self._service.get_project_list().get("data", [])

    # TODO: return of update_project should be ComBuilding
    @overload
    def update_project(
        self,
        project_id: str,
        project_data: ComBuilding,
        mode: Literal["python"] = "python",
    ) -> Optional["ComBuilding"]: ...

    @overload
    def update_project(
        self,
        project_id: str,
        project_data: ComBuilding,
        mode: Literal["json"],
    ) -> Optional[Dict[str, Any]]: ...

    def update_project(
        self,
        project_id: str,
        project_data: ComBuilding,
        mode: Literal["python", "json"] = "python",
    ) -> ComBuilding | dict[str, Any] | None:
        """Update a project by ID.

        The existing project is fetched first to preserve server-assigned IDs
        and the ``userProject`` reference.  Envelope component IDs that are
        ``None`` (auto-generated by Pydantic) are stripped before submission.

        Args:
            project_id: The project ID to update.
            project_data: A ``ComBuilding`` model with the desired state.
            mode: ``"python"`` returns a ``ComBuilding`` model;
                ``"json"`` returns a raw dict.

        Returns:
            The refreshed project after the update, in the requested format.

        Raises:
            COMCheckProjectNotFoundError: If the project does not exist.
        """
        # Get existing project
        old_project = self.get_project(project_id, mode="json")

        if not old_project:
            raise COMCheckProjectNotFoundError(project_id)

        project_data_json = project_data.model_dump(mode="json")

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
        """Convert raw API data to the requested output format.

        Args:
            data: Raw dict from the API response, or ``None``.
            mode: ``"python"`` wraps data in a ``ComBuilding``; ``"json"`` returns it as-is.

        Returns:
            A ``ComBuilding``, a raw dict, or ``None`` if ``data`` is ``None``.
        """
        if data is None:
            return None
        if mode == "python":
            return ComBuilding(**data)
        return data

    def update_uvalues(self, project: ComBuilding) -> ComBuilding:
        """Calculate assembly u-values and update the project in place.

        Sends the full envelope to the u-value endpoint and writes the returned
        values back onto the matching ``agWall``, ``bgWall``, ``roof``, and
        ``floor`` components (matched by ``assemblyType``). Only these assembly
        types receive calculated u-values; ``effectiveUFactor`` applies to
        ``agWall`` only.

        Args:
            project: The project whose envelope u-values should be refreshed.

        Returns:
            The same ``project`` instance, with u-values updated.
        """
        energy_code = str(project.control.code)
        envelope_data = project.envelope.model_dump(mode="json")
        updated_assembly_uvalues = self._service.assemblies_uvalue(
            envelope_data, energy_code
        )["data"]

        for wall in project.envelope.agWall:
            for uvalue in updated_assembly_uvalues.get("agWall", []):
                if wall.assemblyType == uvalue["assemblyType"]:
                    wall.effectiveUFactor = float(uvalue["effectiveUFactor"])
                    wall.propUValue = float(uvalue["propUValue"])
        for wall in project.envelope.bgWall:
            for uvalue in updated_assembly_uvalues.get("bgWall", []):
                if wall.assemblyType == uvalue["assemblyType"]:
                    wall.propUValue = float(uvalue["propUValue"])
        for roof in project.envelope.roof:
            for uvalue in updated_assembly_uvalues.get("roof", []):
                if roof.assemblyType == uvalue["assemblyType"]:
                    roof.propUValue = float(uvalue["propUValue"])
        for floor in project.envelope.floor:
            for uvalue in updated_assembly_uvalues.get("floor", []):
                if floor.assemblyType == uvalue["assemblyType"]:
                    floor.propUValue = float(uvalue["propUValue"])

        return project

    def area_for_renewable(self, project: ComBuilding) -> ComBuilding:
        """Calculate renewable area metrics and update the project in place.

        Sends the project to the area-for-renewable endpoint and writes the
        returned ``largestThreeFloorArea`` and ``roofAreaForRenewable`` values
        back onto ``project.renewable``.

        Args:
            project: The project whose renewable area metrics should be refreshed.

        Returns:
            The same ``project`` instance, with renewable area metrics updated.
        """
        project_data = project.model_dump(mode="json")
        areas = self._service.area_for_renewable(project_data).get("data") or {}

        renewable = project.renewable
        renewable.largestThreeFloorArea = _optional_float(
            areas.get("largestThreeFloorArea")
        )
        renewable.roofAreaForRenewable = _optional_float(
            areas.get("roofAreaForRenewable")
        )
        return project

    def renewable_capacity(self, project: ComBuilding) -> ComBuilding:
        """Calculate renewable capacity and update the project in place.

        Sends the project to the renewable-capacity endpoint and writes the
        returned values back onto ``project.renewable``:

        - ``requiredRenewableCapacity`` → ``requiredCapacity``
        - ``proposedRenewableCapacity`` → ``proposedCapacity``
        - ``requiredOffsiteRenewableProcurementEnergy`` →
          ``requiredOffsiteRenewableEnergy``
        - ``proposedOffsiteRenewableProcurementEnergy`` →
          ``proposedOffsiteRenewableEnergy``

        The endpoint's ``renewableComplianceStatus`` has no field on the
        project model and is not written back.

        Args:
            project: The project whose renewable capacity should be refreshed.

        Returns:
            The same ``project`` instance, with renewable capacity updated.
        """
        project_data = project.model_dump(mode="json")
        capacity = self._service.renewable_capacity(project_data).get("data") or {}

        renewable = project.renewable
        renewable.requiredCapacity = _optional_float(
            capacity.get("requiredRenewableCapacity")
        )
        renewable.proposedCapacity = _optional_float(
            capacity.get("proposedRenewableCapacity")
        )
        renewable.requiredOffsiteRenewableEnergy = _optional_float(
            capacity.get("requiredOffsiteRenewableProcurementEnergy")
        )
        renewable.proposedOffsiteRenewableEnergy = _optional_float(
            capacity.get("proposedOffsiteRenewableProcurementEnergy")
        )
        return project

    def calculate_energy_credits(self, project: ComBuilding) -> EnergyCreditResult:
        """Calculate the proposed and required energy credits of a project.

        Sends the project to the update-energy-credits endpoint. Nothing is
        written back to the project — the project model has no fields for
        calculated credits.

        Args:
            project: The project whose energy credits should be calculated.

        Returns:
            The credits achieved per building area and credit type, the proposed
            and required totals, and any warnings and user alerts.
        """
        project_data = project.model_dump(mode="json")
        credits = self._service.update_energy_credits(project_data).get("data") or {}
        return EnergyCreditResult.model_validate(credits)

    def calculate_interior_space_allowed_wattage(
        self, interior_space: InteriorSpace, energy_code: str
    ) -> Any:
        """Calculate allowed wattage for a single interior lighting space.

        Args:
            interior_space: The interior space (``InteriorSpace``) to
                calculate allowed wattage for.
            energy_code: The energy code for the api end point path.

        Returns:
            A dict with the calculated wattage, e.g.
            ``{"spaceAllowedWattage": 560}``.
        """
        interior_space_data = interior_space.model_dump(mode="json")
        response = self._service.interior_space_allowed_wattage(
            interior_space_data, energy_code
        )
        return response.get("data")

    def calculate_interior_spaces_allowed_wattage(
        self, interior_spaces: List[InteriorSpace], energy_code: str
    ) -> Any:
        """Calculate allowed wattage for a list of interior lighting spaces.

        Args:
            interior_spaces: The interior spaces (``InteriorSpace`` objects)
                to calculate allowed wattage for.
            energy_code: The energy code for the api end point path.

        Returns:
            A dict keyed by each interior space's ``areaDescription``, e.g.
            ``{"Test Space": 610}``.
        """
        interior_spaces_data = [
            interior_space.model_dump(mode="json") for interior_space in interior_spaces
        ]
        response = self._service.interior_spaces_allowed_wattage(
            interior_spaces_data, energy_code
        )
        return response.get("data")

    def check_UA_compliance(self, project: ComBuilding) -> Any:
        """Check UA path compliance for a project.

        Args:
            project: The project data to evaluate.

        Returns:
            The compliance results payload returned by the API.
        """
        project_data = project.model_dump(mode="json")
        response = self._service.check_UA_compliance(project_data)
        return response.get("data")

    def check_requirements(self, project: ComBuilding) -> Any:
        """Check the applicable requirements for a project.

        Args:
            project: The project data to evaluate.

        Returns:
            The requirements payload returned by the API.
        """
        project_data = project.model_dump(mode="json")
        response = self._service.check_requirements(project_data)
        return response.get("data")

    def generate_report(
        self,
        project: ComBuilding,
        envelope: bool = True,
        extlighting: bool = True,
        intlighting: bool = True,
        mechanical: bool = True,
        use_backstop_compliance: bool = False,
        download: bool = False,
        download_dir: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Generate a PDF report for a project.

        The report PDF is stored in S3; the API returns a presigned URL to
        download it. The URL is short-lived (expires within a few minutes).

        This method does not open the report in a browser — as a library it
        returns the report metadata and lets the caller decide what to do
        (e.g. ``webbrowser.open(report["url"])``, stream it onward, or save it
        via *download*).

        Args:
            project: The project data to generate a report for.
            envelope: Whether to include the envelope section in the report.
            extlighting: Whether to include the exterior lighting section.
            intlighting: Whether to include the interior lighting section.
            mechanical: Whether to include the mechanical section.
            use_backstop_compliance: Whether to evaluate the report using
                backstop compliance (sent as ``useBackstopCompliance``).
            download: When ``True``, fetch the PDF from the presigned URL and
                save it using the server-provided ``fileName``.
            download_dir: Directory to save the PDF into when *download* is
                ``True``. Defaults to the user's ``~/Downloads`` folder.

        Returns:
            The report metadata dict with ``url`` (the presigned S3 URL),
            ``expires``, and ``fileName``.
        """
        report_data = {
            "building": project.model_dump(mode="json"),
            "envelope": envelope,
            "extlighting": extlighting,
            "intlighting": intlighting,
            "mechanical": mechanical,
            "useBackstopCompliance": use_backstop_compliance,
        }
        response = self._service.generate_report(report_data)
        if response and download:
            if download_dir is None:
                download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            os.makedirs(download_dir, exist_ok=True)
            pdf_response = httpx.get(response["url"], timeout=60.0)
            pdf_response.raise_for_status()
            output_path = os.path.join(download_dir, response["fileName"])
            with open(output_path, "wb") as f:
                f.write(pdf_response.content)
        return response

    def start_run_simulation(
        self, project: ComBuilding, project_id: Optional[int] = None
    ) -> str:
        """Start a compliance simulation run for a project.

        If *project_id* is supplied the project is persisted via
        :meth:`update_project` before the simulation is launched.

        Args:
            project: The project data to simulate.
            project_id: Optional server-side project ID.  When given, the
                project is saved before the simulation starts.

        Returns:
            The simulation session ID that can be passed to
            :meth:`get_simulation_status` and :meth:`get_simulation_result`.

        Raises:
            COMCheckSimulationError: If the API returns no session data.
        """
        logger = logging.getLogger(__name__)

        # Always refresh the calculated assembly u-values before simulating.
        project = self.update_uvalues(project)

        if project_id:
            logger.info("Updating project: %s", project_id)
            project = self.update_project(str(project_id), project)

        project_data = project.model_dump(mode="json")
        run_result = self._service.start_run_simulation(project_data)
        if run_result.data is None:
            raise COMCheckSimulationError(
                "Simulation start failed: no session data returned"
            )
        return run_result.data.sessionId

    def get_simulation_status(self, session_id: str) -> Dict[str, Any]:
        """Get the status of a running or completed simulation.

        Args:
            session_id: The session ID returned by :meth:`start_run_simulation`.

        Returns:
            A dict containing ``sessionId``, ``status``, and optional
            ``message``. ``status`` is one of the values defined in
            :class:`comcheck_api.types.SimulationStatus`. Terminal
            values are ``"SUCCESS"`` and ``"FAILED"``.

        Raises:
            COMCheckSimulationError: If the status cannot be retrieved.
        """
        status_response = self._service.get_simulation_status(session_id)
        if status_response.data is None:
            raise COMCheckSimulationError(
                f"Failed to get simulation status for session {session_id}"
            )
        return status_response.data.model_dump(mode="json")

    def get_simulation_result(self, session_id: str) -> Dict[str, Any]:
        """Get the result metrics of a completed simulation.

        Args:
            session_id: The session ID returned by :meth:`start_run_simulation`.

        Returns:
            A dict containing ``sessionId``, ``performanceRating``,
            ``energyCreditPerformanceRating``, ``proposedBpf``, and
            ``baselineBpf``.

        Raises:
            COMCheckSimulationError: If the result cannot be retrieved.
        """
        result_response = self._service.get_simulation_result(session_id)
        if result_response.data is None:
            raise COMCheckSimulationError(
                f"Failed to get simulation result for session {session_id}"
            )
        return result_response.data.model_dump(mode="python")

    def calculate_water_heater_efficiency(
        self,
        water_heaters: Union[ServiceWaterHeatingSystem, List[ServiceWaterHeatingSystem]],
        energy_code: str,
        water_heater_name: Optional[str] = None,
    ) -> Dict[str, WaterHeaterEfficiency]:
        """Calculate efficiency requirements for water heater systems.

        Args:
            water_heaters: A single ``ServiceWaterHeatingSystem`` or a list of them.
            energy_code: The energy code to use.
            water_heater_name: Optional name to match a system description.

        Returns:
            A dict keyed by system description, with efficiency requirements.

        Raises:
            ValueError: If a list contains duplicate descriptions.
        """
        systems = [water_heaters] if not isinstance(water_heaters, list) else water_heaters
        if len(systems) > 1:
            descriptions = [s.description for s in systems]
            if len(descriptions) != len(set(descriptions)):
                raise ValueError("All water heater descriptions must be unique")

        if water_heater_name:
            descriptions = [s.description for s in systems]
            if water_heater_name not in descriptions:
                raise ValueError(
                    f"water_heater_name '{water_heater_name}' does not match any system description"
                )

        swh_data = (
            [s.model_dump(mode="json") for s in systems]
            if len(systems) > 1
            else systems[0].model_dump(mode="json")
        )
        result = self._service.water_heater_efficiency(swh_data, energy_code, water_heater_name)
        data = result.get("data") or {}
        return {
            desc: WaterHeaterEfficiency.model_validate(eff)
            for desc, eff in data.items()
        }

    def calculate_hvac_system_efficiency(
        self,
        hvac_systems: Union[HVACSystem, List[HVACSystem]],
        energy_code: str,
        hvac_name: Optional[str] = None,
    ) -> Dict[str, HVACSystemEfficiency]:
        """Calculate efficiency requirements for HVAC systems.

        Args:
            hvac_systems: A single ``HVACSystem`` or a list of them.
            energy_code: The energy code to use.
            hvac_name: Optional name to match a system description.

        Returns:
            A dict keyed by system description, with efficiency requirements.

        Raises:
            ValueError: If a list contains duplicate descriptions.
        """
        systems = [hvac_systems] if not isinstance(hvac_systems, list) else hvac_systems
        if len(systems) > 1:
            descriptions = [s.description for s in systems]
            if len(descriptions) != len(set(descriptions)):
                raise ValueError("All HVAC system descriptions must be unique")

        if hvac_name:
            descriptions = [s.description for s in systems]
            if hvac_name not in descriptions:
                raise ValueError(
                    f"hvac_name '{hvac_name}' does not match any system description"
                )

        hvac_data = (
            [s.model_dump(mode="json") for s in systems]
            if len(systems) > 1
            else systems[0].model_dump(mode="json")
        )
        result = self._service.hvac_system_efficiency(hvac_data, energy_code, hvac_name)
        data = result.get("data") or {}
        return {
            desc: HVACSystemEfficiency.model_validate(eff)
            for desc, eff in data.items()
        }

    def validate_hvac_system_economizer(
        self, hvac_system: HVACSystem, energy_code: str
    ) -> EconomizerValidation:
        """Validate economizer requirements for an HVAC system.

        Args:
            hvac_system: The HVAC system to validate.
            energy_code: The energy code to use.

        Returns:
            Economizer validation results.

        Raises:
            ValueError: If the HVAC system description is empty.
        """
        if not hvac_system.description or not hvac_system.description.strip():
            raise ValueError("HVAC system description cannot be empty")

        hvac_data = hvac_system.model_dump(mode="json")
        result = self._service.hvac_system_economizers_validation(hvac_data, energy_code)
        data = result.get("data") or {}
        # The endpoint returns data keyed by description
        for validation_data in data.values():
            return EconomizerValidation.model_validate(validation_data)
        return EconomizerValidation()

    def calculate_plant_efficiency(
        self,
        plants: Union[HVACPlant, List[HVACPlant]],
        energy_code: str,
        plant_name: Optional[str] = None,
    ) -> Dict[str, PlantEfficiency]:
        """Calculate efficiency requirements for HVAC plants.

        Args:
            plants: A single ``HVACPlant`` or a list of them.
            energy_code: The energy code to use.
            plant_name: Optional name to match a plant description.

        Returns:
            A dict keyed by plant description, with efficiency requirements.

        Raises:
            ValueError: If a list contains duplicate descriptions.
        """
        plant_list = [plants] if not isinstance(plants, list) else plants
        if len(plant_list) > 1:
            descriptions = [p.description for p in plant_list]
            if len(descriptions) != len(set(descriptions)):
                raise ValueError("All plant descriptions must be unique")

        if plant_name:
            descriptions = [p.description for p in plant_list]
            if plant_name not in descriptions:
                raise ValueError(
                    f"plant_name '{plant_name}' does not match any plant description"
                )

        plant_data = (
            [p.model_dump(mode="json") for p in plant_list]
            if len(plant_list) > 1
            else plant_list[0].model_dump(mode="json")
        )
        result = self._service.plant_efficiency(plant_data, energy_code, plant_name)
        data = result.get("data") or {}
        return {
            desc: PlantEfficiency.model_validate(eff)
            for desc, eff in data.items()
        }

    def calculate_fan_pressure_drop_credit(
        self, credit: FanSystemPressureDropCredits, energy_code: str
    ) -> float:
        """Calculate pressure drop credit for a fan system.

        Args:
            credit: The pressure drop credit to calculate. The ``type`` field
                must be set and cannot be ``PRESSURE_DROP_CREDIT_TYPE_UNSPECIFIED``.
            energy_code: The energy code to use.

        Returns:
            The calculated pressure drop credit value.

        Raises:
            ValueError: If the credit type is unset or unspecified.
            COMCheckAPIError: If the response has no ``pressureDropCredit``.
        """
        if not credit.type or credit.type == "PRESSURE_DROP_CREDIT_TYPE_UNSPECIFIED":
            raise ValueError(
                "Credit type must be set and cannot be PRESSURE_DROP_CREDIT_TYPE_UNSPECIFIED"
            )

        # Dump the credit without the type field
        credit_dict = credit.model_dump(mode="json")
        credit_type = credit_dict.pop("type", None)

        result = self._service.fan_pressure_drop_credit(credit_dict, energy_code, credit_type)
        data = result.get("data") or {}
        if data.get("pressureDropCredit") is None:
            raise COMCheckAPIError("No pressureDropCredit returned from the API")
        return float(data["pressureDropCredit"])

    def check_fan_system_compliance(
        self, fan_system: FanSystem, energy_code: str
    ) -> FanSystemComplianceResult:
        """Check compliance for a fan system.

        Args:
            fan_system: The fan system to check.
            energy_code: The energy code to use.

        Returns:
            Fan system compliance results.
        """
        fan_system_data = fan_system.model_dump(mode="json")
        result = self._service.fan_system_compliance(fan_system_data, energy_code)
        data = result.get("data") or {}
        return FanSystemComplianceResult.model_validate(data)

    def calculate_fan_maximum_allowable_hp(
        self, fan: Fan, energy_code: str
    ) -> float:
        """Calculate maximum allowable horsepower for a fan.

        Args:
            fan: The fan to calculate for.
            energy_code: The energy code to use.

        Returns:
            The maximum nameplate horsepower.

        Raises:
            COMCheckAPIError: If the response has no ``maxNameplateHp``.
        """
        fan_data = fan.model_dump(mode="json")
        result = self._service.fan_maximum_allowable_hp(fan_data, energy_code)
        data = result.get("data") or {}
        if data.get("maxNameplateHp") is None:
            raise COMCheckAPIError("No maxNameplateHp returned from the API")
        return float(data["maxNameplateHp"])

    def update_fan_system_compliance(
        self, project: ComBuilding, fan_system_description: str
    ) -> ComBuilding:
        """Calculate fan system compliance and update the project in place.

        Sends the fan system to the compliance endpoint and writes the returned
        values back onto the matching fan system in ``project.hvac.fanSystem``
        (matched by ``description``).

        Args:
            project: The project whose fan system should be updated.
            fan_system_description: The description of the fan system to update.

        Returns:
            The same ``project`` instance, with compliance fields updated.

        Raises:
            ValueError: If hvac is missing or the fan system is not found.
        """
        from comcheck_api.types.core_types import MISSING

        if project.hvac is MISSING or not project.hvac:
            raise ValueError("Project has no hvac data")

        fan_system = None
        for fs in project.hvac.fanSystem or []:
            if fs.description == fan_system_description:
                fan_system = fs
                break

        if fan_system is None:
            raise ValueError(
                f"Fan system '{fan_system_description}' not found in project"
            )

        energy_code = str(project.control.code)
        compliance = self.check_fan_system_compliance(fan_system, energy_code)

        results = {
            field: getattr(compliance, field)
            for field in (
                "complies",
                "complianceMessage",
                "complyMethod",
                "hasPressureDropCredits",
            )
            if getattr(compliance, field) is not None
        }
        # Revalidate the merged fan system — plain setattr skips Pydantic
        # validation, so e.g. a boolean hasPressureDropCredits would not be
        # converted to the HasPressureDropCredits enum.
        updated_fan_system = FanSystem.model_validate(
            {**fan_system.model_dump(mode="python"), **results}
        )
        fan_systems = project.hvac.fanSystem
        fan_systems[fan_systems.index(fan_system)] = updated_fan_system

        return project

    def update_fan_pressure_drop_credits(
        self, project: ComBuilding, fan_system_description: str
    ) -> ComBuilding:
        """Calculate pressure drop credits and update the project in place.

        For each credit in the fan system's ``pressureDropCredits`` list,
        calculates the credit value and writes it back to
        ``pressureDropCredit`` on that credit.

        Args:
            project: The project whose fan system should be updated.
            fan_system_description: The description of the fan system to update.

        Returns:
            The same ``project`` instance, with pressure drop credit values updated.

        Raises:
            ValueError: If hvac is missing or the fan system is not found.
        """
        from comcheck_api.types.core_types import MISSING

        if project.hvac is MISSING or not project.hvac:
            raise ValueError("Project has no hvac data")

        fan_system = None
        for fs in project.hvac.fanSystem or []:
            if fs.description == fan_system_description:
                fan_system = fs
                break

        if fan_system is None:
            raise ValueError(
                f"Fan system '{fan_system_description}' not found in project"
            )

        energy_code = str(project.control.code)

        for credit in fan_system.pressureDropCredits or []:
            if credit.type and credit.type != "PRESSURE_DROP_CREDIT_TYPE_UNSPECIFIED":
                credit_value = self.calculate_fan_pressure_drop_credit(credit, energy_code)
                credit.pressureDropCredit = credit_value

        return project

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
