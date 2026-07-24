"""Example of using COMcheck API client compliance, requirements, and report functions.

UA path vs. ASHRAE 90.1 Compliance Check
----------------------------------------
ASHRAE 90.1-based codes (and state codes derived from it) require TWO checks to
establish full envelope compliance:

  1. UA path (check_UA_compliance) — envelope-only trade-off check.  The
     aggregate UA of proposed assemblies must not exceed the prescriptive
     baseline.  This is fast and synchronous.

  2. Full simulation (start_run_simulation / get_simulation_result) — whole-
     building energy simulation that covers all systems (envelope, lighting,
     mechanical, renewables, etc.).  Required when the UA check passes and a
     complete code compliance determination is needed.

If your project only needs to verify the envelope trade-off path, Example 1 is
sufficient.  If you need an ASHRAE 90.1 Compliance Check determination (e.g. to generate an
official report), run Example 1 first; if it passes, proceed with Example 6.
"""

import os
import time
from dotenv import load_dotenv
from comcheck_api.client import COMcheckClient
from comcheck_api.constants.common_constants import PROJECT_TEMPLATE
from comcheck_api.types.core_types import EnergyCodeOptions
from comcheck_api.types import SimulationStatus

# Initialize client
load_dotenv()
client = COMcheckClient()
api_key = os.getenv("COM_API_KEY") or "your-api-key-here"
client.set_api_key(api_key)

# Build a project to evaluate
project = PROJECT_TEMPLATE.model_copy(deep=True)
project.control.code = EnergyCodeOptions.CEZ_90_1_2022

# Example 1: UA path compliance check (envelope trade-off path only)
compliance = client.check_UA_compliance(project)
print(f"UA compliance: {compliance}")

# Example 2: Check the applicable requirements for the project
requirements = client.check_requirements(project)
print(f"Requirements: {requirements}")

# Example 3: Generate a PDF report (returns metadata: url, expires, fileName)
report = client.generate_report(project)
if report:
    print(f"Report metadata: {report}")

# Example 4: Generate a report and download the PDF to ~/Downloads
report = client.generate_report(
    project,
    envelope=True,
    intlighting=True,
    extlighting=True,
    mechanical=True,
    download=True,
)
if report:
    print(f"Downloaded report: {report['fileName']}")

# Example 5: Download into a specific directory
report = client.generate_report(project, download=True, download_dir="./reports")
if report:
    print(f"Saved report to ./reports/{report['fileName']}")

# Example 6: ASHRAE 90.1 Compliance Check (ASHRAE 90.1-based codes)
# For a complete compliance determination, first verify the UA path passes,
# then run the full simulation.
ua_result = client.check_UA_compliance(project)
if not ua_result or not ua_result.get("mandatoryRequirementsMet"):
    print("UA path failed — skipping full simulation.")
else:
    session_id = client.start_run_simulation(project)
    deadline = time.time() + 300  # 5 min timeout
    while time.time() < deadline:
        status = client.get_simulation_status(session_id)
        if status["status"] == SimulationStatus.SUCCESS:
            result = client.get_simulation_result(session_id)
            print(f"ASHRAE 90.1 Compliance Check result: {result}")
            break
        if status["status"] == SimulationStatus.FAILED:
            print(f"Simulation failed: {status.get('message')}")
            break
        time.sleep(5)
    else:
        print(f"Simulation {session_id} did not complete within 5 minutes.")
