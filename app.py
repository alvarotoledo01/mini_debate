import streamlit as st
from debate import teamConfig, debate
import asyncio

st.title("Debate Simulation with Autogen AgentChat")

topic = st.text_input("Enter the topic for the debate:", "Shall the US government ban TikTok?")
clicked = st.button("Start Debate", type="primary")

chat = st.container()

if clicked:
    chat.empty()


    async def main():
        team = await teamConfig(topic)
        with chat:
            async for message in debate(team):
                if message.startswith("Rocio"):
                    with st.chat_message(name="Rocio", avatar="🤖"):
                        st.write(message)
                elif message.startswith("Ian"): 
                    with st.chat_message(name="Ian", avatar="👍"):
                        st.write(message)
                elif message.startswith("Milena"):
                    with st.chat_message(name="Milena", avatar="👎"):
                        st.write(message)
    asyncio.run(main())                
            
