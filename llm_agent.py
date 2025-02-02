from jira_integration import JiraIntegrator
import openai
import json

class ProjectAssignmentAgent:
    def __init__(self, openai_api_key, project_context=None):
        openai.api_key = openai_api_key
        self.project_context = project_context or {}
        self.jira_integrator = JiraIntegrator()  # Initialize JiraIntegrator

    def process_prompt(self, user_prompt):
        prompt = f"""
        You are a project assignment agent.  Your task is to help manage project tasks.
        Consider the following project context:

        ```json
        {json.dumps(self.project_context, indent=2)}  # Format context as JSON
        ```

        User request: {user_prompt}

        Respond with a JSON object containing the following keys:

        *   `agent_response` (string): A human-readable response to the user.  This could be a suggested action, a request for more information, or a confirmation.
        *   `action_required` (boolean):  `true` if an action needs to be taken (e.g., creating a Jira task), `false` otherwise.
        *   `action_details` (dictionary, optional): Details about the action to be performed. This should only be present if `action_required` is `true`.  Include keys like `task_summary`, `assignee`, `due_date`, and `description` as needed.

        Example:

        ```json
        {{
          "agent_response": "Assign task 'Implement login functionality' to Alice, due on Friday.  The description is: 'Implement user authentication using OAuth 2.0'.",
          "action_required": true,
          "action_details": {{
            "task_summary": "Implement login functionality",
            "assignee": "Alice",
            "due_date": "2024-03-15",  # YYYY-MM-DD format
            "description": "Implement user authentication using OAuth 2.0"
          }}
        }}
        ```

        If no action is required, the `action_details` key should be omitted.  For example:

        ```json
        {{
          "agent_response": "I need more information.  What is the priority of this task?",
          "action_required": false
        }}
        ```
        """  # End of the prompt string
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Or gpt-4
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2048,  # Adjust as needed
                temperature=1.00,  # Adjust as needed
            )
            agent_response_json = json.loads(response.choices.message.content)
            if agent_response_json.get("action_required", False): # Check if action_required is True
                action_details = agent_response_json.get("action_details", {}) # Access action_details safely

                if "task_summary" in action_details:
                    try:
                        new_task_key = self.jira_integrator.create_task(
                            action_details["task_summary"],
                            "MARS",  # Replace with your Project Key
                            action_details.get("assignee"),  # Use.get() to handle optional fields
                            action_details.get("description")
                        )
                        if new_task_key:
                            agent_response_json["jira_task_key"] = new_task_key # Add task key to the response
                            agent_response_json["agent_response"] += f"\nJira task created: {new_task_key}"  # Update agent's response
                        else:
                            agent_response_json["agent_response"] += "\nFailed to create Jira task."

                    except Exception as e:
                        agent_response_json["agent_response"] += f"\nError creating Jira task: {e}"

            return agent_response_json  # Return the (possibly updated) JSON response

        except json.JSONDecodeError:
            return {
                "agent_response": "Error: Could not parse LLM response.",
                "action_required": False,
            }
