import json
import asyncio
import os
from dotenv import load_dotenv



# Class import
from clients import AzureOpenAIClient, AzureCosmosDBClient
from session import Session , World , Location , Encounter
load_dotenv()
app_version = "0.2.0"


async def main():
    
    with open("prompt.json") as prompt_file:
                prompt_json=json.load(prompt_file)
            
            #Create session and open ai client
    azure_open_ai_client = AzureOpenAIClient()
    azure_cosmos_client = AzureCosmosDBClient()

    
    user_text = "Create 3 worlds"
    session = Session()
    world = World()
    location = Location()
    encounter = Encounter()
    
    # TODO create session leger document, add app version 
    item = {
           "id":session.session_id,
           "sessionid_type":f"{session.session_id}_{session.type}",
           "session_id":session.session_id,
           "type":session.type,
           "app_version":app_version,
           "status":"Creating",
           "update_reason":session.type
           }
    azure_cosmos_client.insert_items(item)

    #create world
    await world.create_world(
                client=azure_open_ai_client,
                system_prompt=prompt_json['world_json'][0],
                prompt=user_text
                )
    
    # insert world item to cosmos container
    item = { 
           "id":session.session_id,
           "session_id":session.session_id,
           "type":world.type,"sessionid_type":f"{session.session_id}_{world.type}",
           world.type:world.world
           }  
    azure_cosmos_client.insert_items(item)
    world.item = item

    # Update leger
    operations = [{ 'op': 'replace', 'path': '/update_reason', 'value': world.type },
            { 'op': 'add', 'path': f'/{world.type}_name', 'value': world.world["name"]}
                 ]
    
    azure_cosmos_client.patching_items(session.session_id,f"{session.session_id}_{session.type}",operations)

    
    # create location
    world_description = world.world["description"]
    
    user_text = f"Create 3 Locations using this description: {world_description}"
    
    await location.create_location(
                client=azure_open_ai_client,
                system_prompt=prompt_json['location_json'][0],
                prompt=user_text
    )
    item = {
           "id":session.session_id,
           "sessionid_type":f"{session.session_id}_{location.type}",
           "session_id":session.session_id,
           "type":location.type,
           location.type:location.location
           }  
    azure_cosmos_client.insert_items(item)
    location.item = item

    # Update leger
    operations = [{ 'op': 'replace', 'path': '/update_reason', 'value': location.type },
            { 'op': 'add', 'path': f'/{location.type}_name', 'value': location.location["name"]}
                 ]
    
    azure_cosmos_client.patching_items(session.session_id,f"{session.session_id}_{session.type}",operations)

    # # TODO create charaters
    # # create 4 characters and save it
    # # loop and save the type to create unique characters

    # create encounter
    location_description = location.location["description"]
    
    user_text = f"Create an Encounter using this description: {location_description}"
    
    await encounter.create_encounter(
                client=azure_open_ai_client,
                system_prompt=prompt_json['encounter_json'][0],
                prompt=user_text
    )
    item = {
           "id":session.session_id,
           "sessionid_type":f"{session.session_id}_{encounter.type}",
           "session_id":session.session_id,
           "type":encounter.type,
           encounter.type:encounter.encounter
           }
    # print(item["encounter"])
    azure_cosmos_client.insert_items(item)
    encounter.item = item

    # Update leger
    operations = [{ 'op': 'replace', 'path': '/update_reason', 'value': encounter.type },
            { 'op': 'add', 'path': f'/{encounter.type}_name', 'value': encounter.encounter["name"]}
                 ]
    
    azure_cosmos_client.patching_items(session.session_id,f"{session.session_id}_{session.type}",operations)

    # # TODO create creature

    # # Finish Session:
    # Update leger
    operations = [
           { 'op': 'replace', 'path': '/status', 'value': "Done" }
                 ]
    
    azure_cosmos_client.patching_items(session.session_id,f"{session.session_id}_{session.type}",operations)

    # TODO Creatures on the encounter



if __name__ == '__main__': 
    asyncio.run(main())