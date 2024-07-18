import json
import asyncio
import os
from dotenv import load_dotenv



# Class import
from clients import AzureOpenAIClient, AzureCosmosDBClient
from session import Session , World
load_dotenv()


async def main():
    with open("prompt.json") as prompt_file:
                prompt_json=json.load(prompt_file)
            
            #Create session and open ai client
    azure_open_ai_client = AzureOpenAIClient()
    azure_cosmos_client = AzureCosmosDBClient()

    
    user_text = "Create 4 worlds"
    session = Session()
    world = World(session)
    
    await world.create_world(client=azure_open_ai_client,
                system_prompt=prompt_json['environment_json'][0],
                prompt=user_text)
    # print(world.world)
    
    database = azure_cosmos_client.client.get_database_client(azure_cosmos_client.database)
    container = azure_cosmos_client.client.get_container_client(azure_cosmos_client.container)
    item = {"session_id":session.session_id,"type":"world","world":world.world}
    container.upsert_item(
                item
    )

if __name__ == '__main__': 
    asyncio.run(main())