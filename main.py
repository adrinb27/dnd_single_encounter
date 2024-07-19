import json
import asyncio
import os
from dotenv import load_dotenv



# Class import
from clients import AzureOpenAIClient, AzureCosmosDBClient
from session import Session , World , Location , Encounter
load_dotenv()


async def main():
    with open("prompt.json") as prompt_file:
                prompt_json=json.load(prompt_file)
            
            #Create session and open ai client
    azure_open_ai_client = AzureOpenAIClient()
    azure_cosmos_client = AzureCosmosDBClient()

    
    user_text = "Create 4 worlds"
    session = Session()
    world = World()
    location = Location()
    encounter = Encounter()
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
    
    user_text = f"Create 3 Locations using this description: {world_description}"
    
    await location.create_location(
                client=azure_open_ai_client,
                system_prompt=prompt_json['location_json'][0],
                prompt=user_text
    )
    item = {"id":session.session_id,"session_id":session.session_id,"type":location.type,"location":location.location}  
    azure_cosmos_client.insert_items(item)
    location.item = item

    # create charaters
    # create encounter
    location_description = location.location["description"]
    
    user_text = f"Create an Encounter using this description: {location_description}"
    
    await encounter.create_encounter(
                client=azure_open_ai_client,
                system_prompt=prompt_json['encounter_json'][0],
                prompt=user_text
    )
    item = {"id":session.session_id,"session_id":session.session_id,"type":encounter.type,"encounter":encounter.encounter}
    # print(item["encounter"])
    azure_cosmos_client.insert_items(item)
    encounter.item = item


if __name__ == '__main__': 
    asyncio.run(main())