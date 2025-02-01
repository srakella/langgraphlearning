

groq_api_key="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"

langsmith_api_key="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"
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

import streamlit as st  
if 'prompt' not in st.session_state:
    st.session_state.prompt=""
def clear_prompt():
    st.session_state.prompt=""    
st.title("Chatbot")
st.text_area("Enter your prompt:",height=150,key="prompt")
col1,col2=st.columns(2)

response_container=st.container()
with col1:
    if st.button("Submit"):
        if st.session_state.prompt:
            with st.spinner("Processing..."):
                with response_container:
                    for event in graph.stream({'messages':("user",st.session_state.prompt)}):
                        for(value) in event.values():
                            response=value['messages'].content
                            st.write(f"Assistent: {response}")
with col2:
    if st.button("Clear",on_click=clear_prompt):
        pass            