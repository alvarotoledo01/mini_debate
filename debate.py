import asyncio
import os 
from dotenv import load_dotenv

# Importamos el cliente para interactuar con openai
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Importamos el modelo de mensajes de usuario, nos permitira crear mensajes para enviar al llm
from autogen_core.models import UserMessage

# No necesitamos interactuar directamente con el llm, para ello usaremos el agente
from autogen_agentchat.agents import AssistantAgent

from autogen_agentchat.teams import RoundRobinGroupChat

from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import TextMentionTermination

load_dotenv()

async def teamConfig(topic):
    model = OpenAIChatCompletionClient(
      model="gpt-4o-mini",
      api_key=os.getenv("api_key_open_ai")
    ) 
    # res = await model.create(messages=[UserMessage(content="Hi, how are you?", source="user")])
   
    # print(res)
# definimos el metodo create del modelo, que recibe una lista de mensajes
# y devuelve una respuesta del modelo
    # topic = "Shall US government ban tik tok?"
    
    host = AssistantAgent(
        name="Rocio",
        model_client=model,
        system_message=(
            'You are Rocio, the host of a debate between Ian the supporter agent'
    ' and Milena the critic agent. Your job is moderate the debate '
    f'the topic of the debate is "{topic}". '
    'At the beginning of each round, announce the round number and the topic of the debate.'
    'At the beginning of third round, declare that it will be the last round.'
    'After the last round, thank the audience and exactly say "TERMINATE".'
    'Do not write any content for Ian or Milena. '
    'End every host message with <EOM>.'
        )
    )
    
    supporter = AssistantAgent(
        name="Ian",
        system_message=(
            f'You are Ian, a supporter agent in a debate for the topic "{topic}". '
            'TURN RULES: Speak EXACTLY ONCE per turn, in YOUR voice only. '
            'NEVER write any line for Milena and NEVER prefix with "Milena:". '
            '2–3 sentences, no stage directions, do not close the debate. '
            'End with <EOM>.'
        ),
        model_client=model
    )
    critic = AssistantAgent(
        name="Milena",
        system_message=(
            f'You are Milena, a critic agent in a debate for the topic "{topic}". '
            'TURN RULES: Speak EXACTLY ONCE per turn, in YOUR voice only. '
            'NEVER write any line for Ian and NEVER prefix with "Ian:". '
            '2–3 sentences, no stage directions, do not close the debate. '
            'End with <EOM>.'
        ),
        model_client=model
    )

# Definimos el equipo de debate, que sera un RoundRobinGroupChat
# porque queremos que los agentes hablen por turnos y terminen despues de 4 turnos
    team = RoundRobinGroupChat(
        [host, supporter, critic],
        max_turns=20,
        termination_condition=TextMentionTermination(text="TERMINATE"),
    )
    return team

async def debate(team):
    async for message in team.run_stream(task="Start the debate!"):
        if isinstance(message, TaskResult):
            yield f'Stopping reason: {message.stop_reason}'
            break
        else:
            content = message.content.split("<EOM>")[0]
            yield f'{message.source}: {content}'

    # Imprime el debate de una sola vez, queremos verlo secuencialmente
    # res = await team.run( task="Start the debate!")
    
    # for message in res.messages:
    #     print('-'*20)
    #     print(f'{message.source}: {message.content}')

async def main():
    topic = "Shall US government ban tik tok?"
    team = await teamConfig(topic)
    async for message in debate(team):
        print('-'*20)
        print(message)

if __name__ == "__main__":
    topic = "Shall US government ban tik tok?"
    asyncio.run(main())