import os
from dotenv import load_dotenv
import asana
from asana.rest import ApiException # Important for error handling in v5
from asana.api.tasks_api import TasksApi # API class for tasks
from langchain_core.tools import tool

# Load environment variables from .env file
load_dotenv()

# --- Asana Configuration from .env ---
ASANA_ACCESS_TOKEN = os.getenv("ASANA_ACCESS_TOKEN")
ASANA_WORKSPACE_GID = os.getenv("ASANA_WORKSPACE_GID")
ASANA_PROJECT_GID = os.getenv("ASANA_PROJECT_GID")

default_assignee_gids_str = os.getenv("DEFAULT_ASSIGNEE_GIDS")
DEFAULT_ASSIGNEE_GIDS = default_assignee_gids_str.split(',') if default_assignee_gids_str else []

# --- Validate essential environment variables ---
if not ASANA_ACCESS_TOKEN:
    raise ValueError("ASANA_ACCESS_TOKEN not found in environment variables. Please set it in your .env file.")
if not ASANA_WORKSPACE_GID:
    raise ValueError("ASANA_WORKSPACE_GID not found in environment variables. Please set it in your .env file.")
if not ASANA_PROJECT_GID:
    raise ValueError("ASANA_PROJECT_GID not found in environment variables. Please set it in your .env file.")
if not DEFAULT_ASSIGNEE_GIDS:
    print("Warning: DEFAULT_ASSIGNEE_GIDS not set or empty in .env. Tasks may be unassigned or fail.") # Log a warning if no default assignees

# --- Asana Client Initialization (v5.x.x method) ---
# Configure Asana API client with Personal Access Token
configuration = asana.Configuration()
configuration.access_token = ASANA_ACCESS_TOKEN

# Create an API client instance
api_client_instance = asana.ApiClient(configuration)

# --- Define Asana Tool ---
@tool
def create_asana_task(task_name: str, task_notes: str, assignees_gids: list[str] = None) -> dict:
    """
    Creates a new task in Asana with the given name, notes, and assigns it to specified users.
    Uses Asana Python Client v5.x.x.
    Assignees_gids is a list of Asana user GIDs. If None, uses DEFAULT_ASSIGNEE_GIDS loaded from environment.
    """
    # Determine which assignees to use
    if assignees_gids is None or not assignees_gids:
        assignees_gids_to_use = DEFAULT_ASSIGNEE_GIDS
    else:
        assignees_gids_to_use = assignees_gids

    if not assignees_gids_to_use:
        return {"status": "error", "message": "No assignees GIDs provided in tool call or set in DEFAULT_ASSIGNEE_GIDS in .env. Cannot assign task."}

    # --- DEBUG: Verify task_name and task_notes before sending ---
    print(f"DEBUG: task_name received: '{task_name}'")
    print(f"DEBUG: task_notes received: '{task_notes}'")
    # -----------------------------------------------------------

    # Correct structure for the 'body' parameter based on GitHub example for v5 client
    # The 'data' key contains the task's fields as a dictionary
    body_for_api_call = {
        "data": {
            "name": task_name,  # Pass the task_name here
            "notes": task_notes,  # Pass the task_notes here
            "projects": [ASANA_PROJECT_GID], # Pass the project GID as a list
            "assignee_gid": assignees_gids_to_use[0], # Use 'assignee_gid' for assignee GID
            "workspace_gid": ASANA_WORKSPACE_GID # Use 'workspace_gid' for the workspace
        }
    }
    
    # Options for the API call, e.g., to request specific fields in the response
    opts = {
        'opt_fields': 'gid,name,notes,projects,assignee,permalink_url' # Request useful fields in the response
    }

    try:
        tasks_api_instance = TasksApi(api_client_instance)

        # Call the create_task method with the 'body_for_api_call' dictionary and 'opts'
        api_response = tasks_api_instance.create_task(body_for_api_call, opts)

        # --- DEBUG: Confirm final API response ---
        print(f"DEBUG: Type of final api_response: {type(api_response)}")
        print(f"DEBUG: Raw final api_response content: {api_response}")
        # ----------------------------------------

        # Access gid and name directly from the dictionary as per your last DEBUG output
        # Your DEBUG output showed: {'gid': '...', 'name': '...', 'notes': '...', ...}
        task_gid = api_response.get('gid')
        task_name_from_response = api_response.get('name')
        task_notes_from_response = api_response.get('notes') # Check notes from response too
        
        if task_gid and task_name_from_response is not None: # Check for None explicitly as name could be empty string
            return {
                "status": "success",
                "task_id": task_gid,
                "task_name": task_name_from_response,
                "task_notes": task_notes_from_response, # Include notes in the response for debugging
                "permalink_url": api_response.get('permalink_url') # Get permalink if available
            }
        else:
            return {"status": "error", "message": f"Task created, but GID/name not found in response: {api_response}"}

    except ApiException as e:
        print(f"Asana API Error (Code {e.status}): {e.body}")
        return {"status": "error", "message": f"Asana API Error: {e.body}"}
    except Exception as e:
        print(f"An unexpected error occurred during Asana task creation: {e}")
        return {"status": "error", "message": f"An unexpected error occurred: {e}"}