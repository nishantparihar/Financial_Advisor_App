import streamlit as st
import os
from dotenv import load_dotenv
import time

import pickle
from streamlit_extras.add_vertical_space import add_vertical_space

import openai
from langchain.llms import OpenAI
from langchain.agents import initialize_agent
from langchain.agents.agent_toolkits import ZapierToolkit
from langchain.utilities.zapier import ZapierNLAWrapper
from langchain.agents import Tool
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback

from langchain import LLMChain
from langchain.agents import Tool, AgentExecutor
from langchain.prompts.chat import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from langchain import PromptTemplate
load_dotenv()


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
local_css("style.css")


def get_chat_prompt(chat_history):

    template= """

    Do not generate user responses on your own and avoid repeating questions.

    Yor are a helpful financial advisor chatbot designed to assist/help user with their financial needs. You can provide personalized advice on 
    managing finances, loan repayment strategies, investment options, retirement planning, and other financial queries. 
    You are here to help user make informed decisions and achieve their financial goals. 

    In whichever language user ask question reply in same language.
    For example if user language is hinglish. reply in hinglish.
    {chat_history}

    """

    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    human_template="{query}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    return ChatPromptTemplate.from_messages([system_message_prompt,human_message_prompt])


with st.sidebar:
    st.title('🌐 Welcome to Your Financial Ally! 🌐')
    st.markdown('''
                ### Hello there! 
                I am your dedicated financial advisor chatbot,
                meticulously designed to be your go-to guide in the intricate world
                of finance. 
                ### My mission? 
                To assist and empower you on your financial journey,
                making every step towards your goals a well-informed and confident one.
                ''')
    st.markdown('''
            ### About
            This app is an LLM-powered chatbot built using:
            - [Streamlit](https://streamlit.io/)
            - [LangChain](https://python.langchain.com/)
            - [OpenAI](https://platform.openai.com/docs/models) LLM model
            ''')

    st.markdown('''
            ### Developed by [Nishant Singh Parihar](https://nishantparihar.github.io/)
            ''')


def main():

    st.header("Financial Advisor Chatbot 💰🤖")


    message_placeholder = st.container()
    message_placeholder.markdown('Bot 🤖:   ' + "Hi. . . I am a finacial advisor chatbot. How can I help you!!")

    # Initialize Streamlit chat UI
    if "messages" not in st.session_state:
        st.session_state.messages = []


    def user(query):
        message_placeholder.markdown('Human 🧑:   ' + query)
    
    def bot(response):
        message_placeholder.markdown('Bot 🤖:   ' + response)

    
        
    
    llm = ChatOpenAI(model="gpt-3.5-turbo",temperature=0.7)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    chat_prompt = get_chat_prompt(st.session_state.messages)
    chain = LLMChain(llm=llm, prompt=chat_prompt, memory = memory)




    with st.form('chat_input_form'):
        # Create two columns; adjust the ratio to your liking
        # col1, col2 = st.columns([7,1]) 

        # Use the first column for text input
        # with col1:
        query = st.text_input( "Ask your query:", placeholder= "Ask your query:", label_visibility='collapsed')
        # Use the second column for the submit button
        # with col2:
        submit = st.form_submit_button("Submit")


    if st.button("New Chat"):
        st.session_state.clear()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        if message["role"] == "human":
            message_placeholder.markdown('Human 🧑:   ' + message["content"])
        else :
            message_placeholder.markdown('Bot 🤖:   ' + message["content"])     

    if submit:

        st.session_state.messages.append({"role": "human", "content": query})
        

        user(query)
    

        with get_openai_callback() as cb:
            #response = chain({"input_documents": docs, "human_input": query}, return_only_outputs=True)
            response = chain.run(query)
            print(cb)

        bot(response)

        st.session_state.messages.append({"role": "ai", "content": response})



         

if __name__ == '__main__':
    main()
