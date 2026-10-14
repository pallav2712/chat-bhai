import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq

load_dotenv()

model = ChatGroq(model="openai/gpt-oss-120b")

chat_history: list[BaseMessage] = [
    SystemMessage("You are an AI assistant. “Do not use LaTeX, reply in plain text.”")
]

while True:
    
    user_input = input("You: ")

    if user_input.strip().lower() == "exit":
        break

    chat_history.append(HumanMessage(content=user_input))
    result = model.invoke(chat_history)
    chat_history.append(AIMessage(content=result.content))
    print("AI: ", result.text)

# print(chat_history)
