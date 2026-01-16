"""Example of using COMcheck API client user functions."""

import os
from dotenv import load_dotenv
from comcheck_api.client import COMcheckClient
from comcheck_api.utilities.get_project_default import get_default_project_template

# Initialize client
load_dotenv()
client = COMcheckClient()
client.set_api_key(os.getenv("COM_API_KEY"))

# Example 1: List all projects
projects = client.list_projects()
print("Projects:", projects)

# Example 2: Get a specific project as JSON
if projects:
    project_id = projects[0].get("_id")
    project_json = client.get_project(project_id, mode="json")
    print(f"\nProject {project_id} (JSON):", project_json)

# Example 3: Get a specific project as Python object
if projects:
    project_id = projects[0].get("_id")
    project = client.get_project(project_id)
    print(f"\nProject {project_id} details:")
    print(f"Name: {getattr(project, 'projectName', 'N/A')}")
    print(f"Type: {getattr(project, 'projectType', 'N/A')}")

# Example 4: Update a project with default template
if projects:
    project_id = projects[0].get("_id")
    default_project = get_default_project_template()
    updated_project = client.update_project(project_id, default_project)
    print(f"\nUpdated project {project_id} with default template")
