"""Example of using COMcheck API client compliance, requirements, and report functions."""

import os
from dotenv import load_dotenv
from comcheck_api.client import COMcheckClient
from comcheck_api.constants.common_constants import PROJECT_TEMPLATE
from comcheck_api.types.core_types import EnergyCodeOptions

# Initialize client
load_dotenv()
client = COMcheckClient()
api_key = os.getenv("COM_API_KEY") or "your-api-key-here"
client.set_api_key(api_key)

# Build a project to evaluate
project = PROJECT_TEMPLATE.model_copy(deep=True)
project.control.code = EnergyCodeOptions.CEZ_90_1_2022

# Example 1: Check code compliance for the project
compliance = client.check_UA_compliance(project)
print(f"Compliance: {compliance}")

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
