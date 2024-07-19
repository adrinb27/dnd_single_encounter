import random
import json
from utils import create_string_from_dict_attributes, transform

class Session():
    def __init__(self):
        self.session_id= ''.join(random.choice('0123456789') for i in range(8))

class World(Session):
    
    def __init__(self):
        super().__init__()
        # self.session_id= session.session_id
        self.type = "world"
        self.world = {}
        self.item = {}

    async def create_world(self,client,system_prompt,prompt):
        worlds = await client.call_openai_model(system_message = system_prompt, 
                                        user_message = prompt, 
                                        model=client.azure_oai_deployment
                                        )
            
            # clean output
        worlds= worlds.replace('```', '')
        worlds= worlds.replace('json', '')
        #store in session
        worlds = json.loads(worlds)
        worlds_string = create_string_from_dict_attributes(worlds)
        world_choice = input(f"Choose from the following: {worlds_string}")
        self.world = worlds[world_choice]
        self.world["name"] = world_choice

class Location(World):
    def __init__(self):
        super().__init__()
        # self.session_id= session.session_id
        self.type = "location"
        self.location = {}
        self.item = {}
    async def create_location(self,client,system_prompt,prompt):
        locations = await client.call_openai_model(system_message = system_prompt, 
                                    user_message = prompt, 
                                    model=client.azure_oai_deployment
                                    )
        # clean output
        locations= locations.replace('```', '')
        locations= locations.replace('json', '')
        
        #store in session
        locations = json.loads(locations)
        # print(locations)
        #Create locations
        # location_choice = f"Create 4 Locations using this description: {locations}"
        # Create location
        if isinstance(locations[list(locations.keys())[0]],list):
            locations = locations[list(locations.keys())[0]]
            locations = transform(locations)

            locations_string = create_string_from_dict_attributes(locations)
            location_choice = input(f"Choose from the following: {locations_string}")
            
            self.location = locations[location_choice]
            self.location["name"] = location_choice
        elif isinstance(locations[list(locations.keys())[0]],dict):
            # locations = locations[list(locations.keys())[0]]
            # print(locations)
            locations_string = create_string_from_dict_attributes(locations)
            location_choice = input(f"Choose from the following: {locations_string}")

            
            self.location = locations[location_choice]
            self.location["name"] = location_choice
        elif isinstance(locations,dict):
            # print(locations)
            locations_string = create_string_from_dict_attributes(locations)
            location_choice = input(f"Choose from the following: {locations_string}")
            self.location = locations[location_choice]
            self.location["name"] = location_choice          

class Encounter(Location):
    def __init__(self):
        super().__init__()
        # self.session_id= session.session_id
        self.type = "encounter"
        self.location = {}
        self.item = {}
    async def create_encounter(self,client,system_prompt,prompt):
        encounter = await client.call_openai_model(system_message = system_prompt, 
                                    user_message = prompt, 
                                    model=client.azure_oai_deployment
                                    )
        # clean output
        encounter= encounter.replace('```', '')
        encounter= encounter.replace('json', '')
        #store in session
        print(encounter)
        try:
            encounter_json= json.loads(encounter)
        except Exception as error:
            print(error)

        # print(encounter_json)
        if isinstance(encounter_json[list(encounter_json.keys())[0]],list):
            self.encounter = transform(encounter_json[list(encounter_json.keys())[0]])
            # print("it is a list",self.encounter)
        elif isinstance(encounter_json[list(encounter_json.keys())[0]],dict):
            self.encounter = encounter_json
            # print("it is a dictionary",self.encounter)
        elif isinstance(encounter_json,dict):
            self.encounter = encounter_json
        # self.encounter = transform(encounter_json["encounter"])

        # self.encounter = json.loads(encounter)
        # print(self.encounter)