import os
from jira import JIRA

class JiraIntegrator:
    def __init__(self):
        # Set environment variables
        os.environ['JIRA_SERVER'] = 'https://srakella19.atlassian.net/'
        os.environ['JIRA_USERNAME'] = 'srakella19@gmail.com'
        os.environ['JIRA_API_TOKEN'] = 'ATATT3xFfGF0oDcax8Fzkc8_06AE0Pzf54S3m_7g0q0ntNdYHRWiJ6tY8yeLAca_OFNdl9_B2TcroFEnT-9aw9MhmCKxwftqh7uLGYM4vV0vbkd4C2AYRcpg79bS1Jsa5LwXcARMGMtKVDltpcYdDzuf3bu16sehMhq-WEpHxtUvfBg5F--dYR0=BD7D5C1E'

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


    # Add more methods for other Jira actions (update_task, get_task, etc.)

# Example usage:
try:
    jira_integrator = JiraIntegrator()  # Create an instance of the class

    project_key = "MARS"  # Replace with your project key
    task_summary = "Implement new feature"
    assignee = "sravan15462"  # Jira username of the assignee
    #due_date = "2024-03-15"
    description = "Detailed description of the new feature..."

    new_task_key = jira_integrator.create_task(task_summary, project_key, assignee, description)

    if new_task_key:
        print(f"New Jira task created: {new_task_key}")

        # Example of assigning an existing task
        if jira_integrator.assign_task(new_task_key, assignee):  # Assign to a different user
            print(f"Task {new_task_key} assigned successfully.")
        else:
            print(f"Failed to assign task {new_task_key}.")

except ValueError as e:
    print(f"Configuration Error: {e}")
except Exception as e:
    print(f"A general error occurred: {e}")