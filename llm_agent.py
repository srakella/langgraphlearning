from jira_integration import JiraIntegrator
import openai
import json

class ProjectAssignmentAgent:
    def __init__(self, openai_api_key, project_context=None):
        openai.api_key = openai_api_key
        self.project_context = project_context or {}
        self.jira_integrator = JiraIntegrator()  # Initialize JiraIntegrator

    def process_prompt(self, user_prompt):
        #... (Your existing prompt construction and LLM interaction code)...

        try:
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
