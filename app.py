import streamlit as st
import os
from dotenv import load_dotenv
import time

import pickle
from streamlit_extras.add_vertical_space import add_vertical_space

from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback
from langchain.chains import ConversationChain

from langchain.prompts.chat import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)



from gptcache import cache
from gptcache.adapter import openai


cache.init()
cache.set_openai_key()

from langchain import PromptTemplate
load_dotenv()


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
local_css("style.css")


def get_chat_prompt():

    template= """

    Do not generate user responses on your own and avoid repeating questions.

    Yor are a helpful financial advisor chatbot designed to assist/help user with their financial needs. 
    Identify user as borrower or broker.
    You can provide personalized advice on managing finances, loan repayment strategies, investment options, retirement planning, and other financial queries. 
    You are here to help user make informed decisions and achieve their financial goals. 
    Your goal is to sell some sort of financial product of the bank (loan, insurance, health plan, etc) to the user.
    Get the consumer to agree they want to start the deal and then push them to have a conversation with a human representative to finalize the start of the deal.
    Settle for meeting lesser goals (consumer just asking to speak to a human),
    Find a 'turn' in the conversation and use sentiment analysis to detect changes in the user's interest or urgency,
    Guide users through preliminary stages of the deal,
    Provide specific details to the user without overloading them with information,
    Adhere to all relevant financial regulations and ethical standards,
    Use language engaging and easy to understand,
    Avoid overly aggressive or sales-oriented chatbot behavior,
    Enhance user experience with user-centric interactions,
    Maintain a conversational tone rather than a hard-sell approach,
    Emphasize guiding consumers through their decision-making process,
    Focus on providing helpful information and answering queries


        
    In whichever language user ask question reply in same language.
    For example if user language is hinglish. reply in hinglish.

    """

    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    human_template="{input}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    messagee_place_holder = MessagesPlaceholder(variable_name="chat_history")
    return ChatPromptTemplate.from_messages([system_message_prompt,messagee_place_holder, human_message_prompt])



def main():

    st.header("Financial Advisor Chatbot 💰🤖")


    message_placeholder = st.container()
    message_placeholder.markdown('Bot 🤖:   ' + "Hi. . . I am a finacial advisor chatbot. How can I help you!!")

    # Initialize Streamlit chat UI
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []


    def user(query):
        message_placeholder.markdown('Human 🧑:   ' + query)
    
    def bot(response):
        message_placeholder.markdown('Bot 🤖:   ' + response)

    




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
        llm = ChatOpenAI(model="gpt-3.5-turbo",temperature=0.7)
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        chat_prompt = get_chat_prompt()
        chain = ConversationChain(llm=llm, prompt=chat_prompt, memory = memory)
        
        for chat in st.session_state.chat_history:
            memory.save_context({"input": chat["input"]}, {"output": chat["output"]})
        # memory.save_context({"input": "hi"}, {"output": "whats up"})

        user(query)
    
        
        with get_openai_callback() as cb:
            start_time = time.time()
            #response = chain({"input_documents": docs, "human_input": query}, return_only_outputs=True)
            response = chain.run(query)
            print("Time consuming: {:.2f}s".format(time.time() - start_time))
            print(cb)

        bot(response)

        st.session_state.messages.append({"role": "ai", "content": response})
        st.session_state.chat_history.append({"input": query, "output": response})
        # memory.save_context({"input": "hi"}, {"output": "whats up"})




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
         

if __name__ == '__main__':
    main()
