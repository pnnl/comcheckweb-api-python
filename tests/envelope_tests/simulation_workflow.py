# Load environment variables
import os

from comcheck_api import COMcheckClient

os.environ["COM_API_KEY"] = "g85IQHH0ds1qWmK68zGfOaBV0jyRcX4bP462DqTb"
api_key = os.getenv("COM_API_KEY")
#if not api_key:
#    pytest.fail("COM_API_KEY is not set in environment variables.")
client = COMcheckClient()
client.set_api_key(api_key)

status = client.get_simulation_status("e53ef86b-7aa7-4618-9ba3-4f357b965208")
print(status)