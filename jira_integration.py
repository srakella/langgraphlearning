import os
from jira import JIRA
from hcp_vault_helper import HCPVaultHelper

class JiraIntegrator:
    def __init__(self):
        # Set environment variables
        os.environ['JIRA_SERVER'] = 'https://srakella19.atlassian.net/'
        os.environ['JIRA_USERNAME'] = 'srakella19@gmail.com'
        os.environ['JIRA_API_TOKEN'] = HCPVaultHelper.get_api_token()
        # Get environment variables
        self.JIRA_SERVER = os.getenv('JIRA_SERVER')
        self.JIRA_USERNAME = os.getenv('JIRA_USERNAME')
        self.JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')
        self.jira = None  # Initialize jira to None

        if not all([self.JIRA_SERVER, self.JIRA_USERNAME, self.JIRA_API_TOKEN]):
            raise ValueError("JIRA_SERVER, JIRA_USERNAME, and JIRA_API_TOKEN environment variables must be set.")

        try:
            jira_options = {'server': self.JIRA_SERVER}
            self.jira = JIRA(options=jira_options, basic_auth=(self.JIRA_USERNAME, self.JIRA_API_TOKEN))
            print("Successfully connected to Jira.")  # Optional confirmation message
        except Exception as e:
            print(f"Error connecting to Jira: {e}")
            # Handle the error appropriately (e.g., raise an exception, log the error, etc.)
            raise  # Re-raise the exception so calling code knows connection failed


    def create_task(self, summary, project_key, assignee=None, description=None):    
        try:
            fields = {
                'project': {'key': project_key},
                'summary': summary,
                'issuetype': {'name': 'Task'}  # Default to 'Task' issue type
            }

            if assignee:
                # Jira uses accountId for assignees. You might need to fetch this.
                # Simplified for this example: assumes username is sufficient.
                fields['assignee'] = {'name': assignee} # Or {'accountId': assignee_id} if available

        
            if description:
                fields['description'] = description
            
            new_task = self.jira.create_issue(fields=fields)
            return new_task.key  # Return the key of the created task

        except Exception as e:
            print(f"Error creating Jira task: {e}")
            return None  # Or raise the exception if you prefer

    def assign_task(self, task_key, assignee):  # New method to assign tasks
        try:
            # Similar assignee handling as in create_task
            self.jira.assign_issue(task_key, assignee) # or self.jira.assign_issue(task_key, {'accountId': assignee_id})
            return True
        except Exception as e:
            print(f"Error assigning task: {e}")
            return False
