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
    
    # insert world item
    item = {"id":session.session_id,"session_id":session.session_id,"type":world.type,"world":world.world}  
    azure_cosmos_client.insert_items(item)
    world.item = item



if __name__ == '__main__': 
    asyncio.run(main())