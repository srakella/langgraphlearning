

groq_api_key="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"

langsmith_api_key="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"


import json
import os
os.environ['GROQ_API_KEY'] = groq_api_key
os.environ['LANGSMITH_API_KEY'] = langsmith_api_key
os.environ['LANGCHAIN_TRACING_V2']="true"
os.environ['LANGCHAIN_PROJECT']="LangsmithLearning"

from langchain_groq import ChatGroq
llm=ChatGroq(groq_api_key=groq_api_key, model_name="deepseek-r1-distill-llama-70b")
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
class State(TypedDict):
    messages: Annotated[list, add_messages]
graph_builder = StateGraph(State) 
def chatbot(state: State):
    return {'messages':llm.invoke(state['messages'])}
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)    
graph=graph_builder.compile()
import re
import streamlit as st  
from llm_agent import ProjectAssignmentAgent
from project_data import project_context
if 'prompt' not in st.session_state:
    st.session_state.prompt=""
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history=[]


def clear_prompt():
    st.session_state.prompt=""
    
def reset_conversation():
    st.session_state.prompt=""
    st.session_state.conversation_history=[]    

def format_agent_response(agent_response_json):
    """Formats a JSON agent response for display in Streamlit."""

    try:
        agent_response = json.loads(agent_response_json)  # Parse the JSON string
    except json.JSONDecodeError:
        return "Invalid JSON response from agent."  # Handle parsing errors

    formatted_output = ""

    if isinstance(agent_response, dict):  # Handle dictionary-based JSON
        for key, value in agent_response.items():
            formatted_output += f"**{key}:** {value}\n\n"  # Bold keys, add newlines
    elif isinstance(agent_response, list):  # Handle list-based JSON
        formatted_output += "<ul>"  # Start an unordered list
        for item in agent_response:
            if isinstance(item, dict):
                formatted_output += "<li>" # Start a list item
                for key, value in item.items():
                    formatted_output += f"<strong>{key}:</strong> {value}<br>"
                formatted_output += "</li>" # Close a list item
            else:
                formatted_output += f"<li>{item}</li>"  # Simple list items
        formatted_output += "</ul>"  # Close the unordered list

    else:
        formatted_output = str(agent_response)  # Default to string conversion

    return formatted_output

st.title("Chatbot")
st.text_area("Enter your prompt:",height=150,key="prompt")
col1,col2,col3=st.columns(3)

response_container=st.container()
with col1:
    if st.button("Submit"):
        if st.session_state.prompt:
            st.session_state.conversation_history.append({"role":"user","content":st.session_state.prompt})
            user_input=st.session_state.prompt
            if re.search(r"(create|new|add)\s+(task|issue|ticket)", user_input, re.IGNORECASE) or re.search(r"assign\s+.*to", user_input, re.IGNORECASE) or re.search(r"jira\s+task", user_input, re.IGNORECASE): # More patterns as needed
                with st.spinner("Processing..."):
                    project_agent = ProjectAssignmentAgent(groq_api_key,project_context)
                    #agent_response = user_input
                    agent_response = project_agent.process_prompt(user_input)
                    formatted_response = format_agent_response(agent_response) # Format the response
                    st.markdown(formatted_response, unsafe_allow_html=True) # Display the formatted response.
                   
                    #st.write(f"Assistant: {agent_response}")
            else:    
                with st.spinner("Processing..."):
                    with response_container:
                        for event in graph.stream({'messages':st.session_state.conversation_history}):
                            for(value) in event.values():
                                response=value['messages'].content
                                st.session_state.conversation_history.append({"role":"assistant","content":response})
                                st.write(f"Assistant: {response}")
with col2:
    if st.button("Clear",on_click=clear_prompt):
        pass    
with col3:
    if st.button("Reset",on_click=reset_conversation):
        pass

