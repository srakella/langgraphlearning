from jira_integration import JiraIntegrator
import json
from groq import Groq
class ProjectAssignmentAgent:
    def __init__(self, groq_api_key,project_context=None):
        self.project_context = project_context or {}
        self.jira_integrator = JiraIntegrator()  # Initialize JiraIntegrator
        self.llm=Groq(api_key=groq_api_key)
        
    def generate_prompt(self, user_prompt):
        return [
                {
                    "role": "user",
                    "content": user_prompt
                },
                {
                    "role": "system",
                    "content": f"""
                    You are a project assignment agent.  Your task is to help manage project tasks.
                    Consider the following project context:

                    ```json
                    {json.dumps(self.project_context, indent=2)}
                    ```

                    User request: {user_prompt}

                    pick the assignee from team members
                    Respond with a JSON object containing the following keys:

                    *   `agent_response` (string): A human-readable response to the user.  This could be a suggested action, a request for more information, or a confirmation.
                    *   `action_required` (boolean):  `true` if an action needs to be taken (e.g., creating a Jira task), `false` otherwise.
                    *   `action_details` (dictionary, optional): Details about the action to be performed. This should only be present if `action_required` is `true`.  Include keys like `task_summary`, `assignee`, and `description` as needed.

                    Example:

                    ```json
                    {{
                    "agent_response": "Assign task 'Implement login functionality' to Alice, due on Friday.  The description is: 'Implement user authentication using OAuth 2.0'.",
                    "action_required": true,
                    "action_details": {{
                        "task_summary": "Implement login functionality",
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
                    """
                }

            ]
    def process_prompt(self, user_prompt):
        try:      
            prompt = self.generate_prompt(user_prompt)  # Generate the prompt for the LLM
            response = self.llm.chat.completions.create(model="deepseek-r1-distill-llama-70b",messages=prompt,response_format={"type": "json_object"},stream=False)
            
            agent_response_json = json.loads(response.choices[0].message.content)
            print(f"agent response: {agent_response_json}")
            if agent_response_json.get("action_required", True): # Check if action_required is True
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
            return agent_response_json

        except json.JSONDecodeError:
            return {
                "agent_response": "Error: Could not parse LLM response.",
                "action_required": False,
            }
    