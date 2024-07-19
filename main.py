import json
import asyncio
import os
from dotenv import load_dotenv



# Class import
from clients import AzureOpenAIClient, AzureCosmosDBClient
from session import Session , World , Location
load_dotenv()


async def main():
    with open("prompt.json") as prompt_file:
                prompt_json=json.load(prompt_file)
            
            #Create session and open ai client
    azure_open_ai_client = AzureOpenAIClient()
    azure_cosmos_client = AzureCosmosDBClient()

    
    user_text = "Create 4 worlds"
    session = Session()
    world = World(session=session)
    location = Location(session=session)
    #create world
    await world.create_world(
                client=azure_open_ai_client,
                system_prompt=prompt_json['world_json'][0],
                prompt=user_text
                )
    
    # insert world item to cosmos container
    item = {"id":session.session_id,"session_id":session.session_id,"type":world.type,"world":world.world}  
    azure_cosmos_client.insert_items(item)
    world.item = item
    
    # create location
    world_description = world.world["description"]
    
    user_text = f"Create 4 Locations using this description: {world_description}"
    
    await location.create_location(
                client=azure_open_ai_client,
                system_prompt=prompt_json['location_json'][0],
                prompt=user_text
    )
    item = {"id":session.session_id,"session_id":session.session_id,"type":location.type,"location":location.location}  
    azure_cosmos_client.insert_items(item)
    world.item = item

    # create charaters
    # create encounter





if __name__ == '__main__': 
    asyncio.run(main())