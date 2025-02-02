

groq_api_key="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"

langsmith_api_key="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"

openai_api_key="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"

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
                    project_agent = ProjectAssignmentAgent(openai_api_key, project_context)
                    #agent_response = user_input
                    agent_response = project_agent.process_prompt(user_input)
                    st.write(f"Assistent: {agent_response}")
            else:    
                with st.spinner("Processing..."):
                    with response_container:
                        for event in graph.stream({'messages':st.session_state.conversation_history}):
                            for(value) in event.values():
                                response=value['messages'].content
                                st.session_state.conversation_history.append({"role":"assistant","content":response})
                                st.write(f"Assistent: {response}")
with col2:
    if st.button("Clear",on_click=clear_prompt):
        pass    
with col3:
    if st.button("Reset",on_click=reset_conversation):
        pass
