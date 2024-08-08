import json
import asyncio
import os
import random
import numpy
from dotenv import load_dotenv

load_dotenv()

# Class import
from clients import AzureOpenAIClient, AzureCosmosDBClient
from session import Session , World , Location , Encounter, Characters
app_version = "0.3.0"
async def main():
    with open("prompt.json") as prompt_file:
        prompt_json=json.load(prompt_file)
            
    #Create session and open ai client
    azure_open_ai_client = AzureOpenAIClient()
    azure_cosmos_client = AzureCosmosDBClient()


    #create session leger document, add app version
    session = Session() 
    item = {
           "id":session.session_id,
           "sessionid_type":f"{session.session_id}_{session.type}",
           "session_id":session.session_id,
           "type":session.type,
           "app_version":app_version,
           "status":"Creating",
           "update_reason":session.type,
           "player_count":0
           }
    azure_cosmos_client.insert_items(item)
    
    #create world
    world = World(session)
    await world.create_world(azure_open_ai_client,azure_cosmos_client)
    

    # world_content = await world.get_content(azure_cosmos_client)

if __name__ == '__main__': 
    asyncio.run(main())    