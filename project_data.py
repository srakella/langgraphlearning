project_context = {
    "team_members": {
        "sravan15462": {"skills": ["Python", "Jira"], "availability": "full", "name": "Alice Smith"},
        "sravan akella": {"skills": ["Testing", "QA"], "availability": "part-time", "name": "Bob Johnson"},
    },
    "project_goals": "Release version 1.0 of the application by the end of the quarter.",
    "available_resources": ["Developer time", "Testing resources", "AWS credits"],
    "project_timeline": {
        "start_date": "2024-01-15",
        "milestone_1": "2024-02-28",
        "end_date": "2024-03-31"
    },
    "existing_tasks": [
        {"summary": "Implement user authentication", "assignee": "Alice Smith", "status": "In Progress"},
        {"summary": "Create unit tests", "assignee": "Bob Johnson", "status": "To Do"}
    ]
}


# You can also add a function to modify the project context if needed:
def update_project_context(new_data):
    project_context.update(new_data)