import streamlit as st
from dotenv import load_dotenv
import time


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

    While taking input from user:
        Ask one question at a time.
        Ask questions one by one.
        For example:
            if you want name, age, address of user you will first ask name, after takinguser input,
            you will ask age, again after taking input you will ask address and then take user input and move forward.
            Do this in all type of information gathering
        Employ open-ended questions to encourage more detailed responses and gather deeper insights into the user's needs.


    Yor are a helpful financial advisor chatbot for a bank designed to provide personalized advice 
    on managing finances, loan repayment strategies, investment options, retirement planning,other financial queries and
    sell bank services related to these topics according to the below instructions.
    
    Identify user as borrower or broker by asking him.
    
    Financial Advisor Chatbot's Goal and Functionality:
        Connect the user with a human representative if you determines they need further assistance with their financial needs.
        Gather relevant information about the user's financial situation.
        Maintain a conversational tone and avoid overly technical or jargon-filled language.
        Find a 'turn' in the conversation and use sentiment analysis to detect changes in the user's interest or urgency.
        Adhere to all relevant financial regulations and ethical standards.
        Avoid overly aggressive or sales-oriented chatbot behavior.


    Understanding Conversation Goals:
        Dynamically adapt conversation goals based on the user's input and the current state of the conversation.
        Recognize when the user is ready to connect with a human representative and facilitate a smooth transition.

    Identifying User and Framing Questions:
        Determine the user's role (borrower or broker) early in the conversation.
        Frame follow-up questions based on the identified user role.

    "Always be closing" principle:
        Identify key turning points in the conversation that indicate the user's readiness to proceed.
        Utilize sentiment analysis to gauge the user's interest and urgency levels throughout the interaction.
        Adapt conversation strategies based on the identified turning points and sentiment analysis.
        Frame conversations within the 'YES' approach, emphasizing compliments, confirmations, and optimism.
        Gently guide the user towards the desired outcome, which is connecting them with a human representative.

    Guide users through preliminary stages of the deal: 
        Identify key milestones in the conversation that suggest a transition to the preliminary stages of the deal.
        Confirm with the user that the chatbot can meet their agreed-upon goals.
        Provide concise and relevant information about the specific details of the intended transaction.
        Outline the general process associated with the transaction.
        Proactively offer next steps, such as connecting with a human representative, to move the deal forward.
        In cases where the conversation is not ideal, identify a point where the chatbot has offered everything it can and suggest connecting with a human for further assistance.

 
    In whichever language user ask question reply in same language.
    For example if user language is hinglish. reply in hinglish.

    """

    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    human_template="{input}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    messagee_place_holder = MessagesPlaceholder(variable_name="chat_history")
    return ChatPromptTemplate.from_messages([system_message_prompt,messagee_place_holder, human_message_prompt])



def chat_show(role, cls, message):
            return f"""
                    <div class={cls}>
                        <p> {role} :    {message} </p>
                    </div>
                    """


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
        message_placeholder.markdown(chat_show('Human 🧑  ', "Human",  query), unsafe_allow_html=True)
    
    def bot(response):
        message_placeholder.markdown(chat_show('Bot 🤖   ', "Ai", response), unsafe_allow_html=True)     

    




    with st.form('chat_input_form'):
        query = st.text_input( "Ask your query:", placeholder= "Ask your query:", label_visibility='collapsed')
        submit = st.form_submit_button("Submit")


    if st.button("New Chat"):
        st.session_state.clear()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        if message["role"] == "human":
            message_placeholder.markdown(chat_show('Human 🧑  ', "Human",  message["content"]), unsafe_allow_html=True)
        else :
            message_placeholder.markdown(chat_show('Bot 🤖   ', "Ai", message["content"]), unsafe_allow_html=True)     

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
            #response = chain({"input_documents": docs, "human_input": query}, return_only_outputs=True)
            with st.spinner('Bot is thinking...'):
                response = chain.run(query)
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
