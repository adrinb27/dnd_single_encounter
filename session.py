import random
import json
import numpy
from utils import create_string_from_dict_attributes, transform

with open("prompt.json") as prompt_file:
                prompt_json=json.load(prompt_file)
class Session():
    def __init__(self):
        self.session_id= ''.join(random.choice('0123456789') for i in range(8))
        self.type="session"
    def get_leger(self,cosmos_client):
        database = cosmos_client.client.get_database_client(cosmos_client.database)
        container = database.get_container_client(cosmos_client.container)
        
        query = f'SELECT * FROM mycontainer c WHERE c.id="{self.session_id}" and c.sessionid_type="{self.session_id}_{self.type}"'
        
        items = container.query_items(query=query,enable_cross_partition_query=True)
        content = {}
        for item in items:
            content = item
        return content

class World(Session):
    
    def __init__(self,session):
        super().__init__()
        self.session_id= session.session_id
        self.type = "world"
        # self.world = {}
        self.item = {}
        self.content = {}

    async def create_world(self,azure_open_ai_client,azure_cosmos_client):
        user_text = "Create a world"
        await self.create_content(
                oai_client=azure_open_ai_client,
                system_prompt=prompt_json['world_json'][0],
                prompt=user_text
                )
        # insert world item to cosmos container
        item = { 
                "id":self.session_id,
                "sessionid_type":f"{self.session_id}_{self.type}",
                "session_id":self.session_id,
                "type":self.type,
                self.type:self.content
                }  
        azure_cosmos_client.insert_items(item)
        self.item = item

        # Update leger
        operations = [{ 'op': 'replace', 'path': '/update_reason', 'value': self.type },
                { 'op': 'add', 'path': f'/{self.type}_name', 'value': self.content["name"]}
                        ]

        azure_cosmos_client.patching_items(self.session_id,f"{self.session_id}_session",operations)
    
    async def get_content(self,cosmos_client):
        database = cosmos_client.client.get_database_client(cosmos_client.database)
        container = database.get_container_client(cosmos_client.container)
        
        query = f'SELECT c.{self.type} FROM mycontainer c WHERE c.id="{self.session_id}" and c.sessionid_type="{self.session_id}_{self.type}"'
        
        items = container.query_items(query=query,enable_cross_partition_query=True)
        content = {}
        for item in items:
            content = item[f"{self.type}"]
        return content
    async def create_content(self,oai_client,system_prompt,prompt):
        content = await oai_client.call_openai_model(system_message = system_prompt, 
                                    user_message = prompt, 
                                    model=oai_client.azure_oai_deployment
                                    )
        # clean output
        content= content.replace('```', '')
        content= content.replace('json', '')
        # print(content)
        #store in session
        try:
            content = json.loads(content)
            self.content = content
        except:
            content = content
            self.content = content


class Location(World):
    def __init__(self,session):
        super().__init__(session)
        self.session_id= session.session_id
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
            self.location["name"] = location_choice          
            self.location["description"] = locations[location_choice]
            # print(self.location)
class Characters(World):
    def __init__(self, session):
        super().__init__(session)
        self.session_id= session.session_id
        self.type = "characters"
        self.world = {}
        self.item = {}
        self.trait =""
        self.player_number = 0
    async def create_characters(self,azure_open_ai_client,azure_cosmos_client):
        character_traits = [  
        "Ambitious",  
        "Compassionate",  
        "Cunning",  
        "Diligent",  
        "Eccentric",  
        "Fearless",  
        "Generous",  
        "Honest",  
        "Impulsive",  
        "Joyful",  
        "Kind-hearted",  
        "Loyal",  
        "Melancholic",  
        "Naïve",  
        "Optimistic",  
        "Pessimistic",  
        "Quirky",  
        "Resourceful",  
        "Stubborn",  
        "Tenacious",  
        "Unpredictable",  
        "Vain",  
        "Wise",  
        "Xenial",  
        "Yearning",  
        "Zealous",  
        "Aloof",  
        "Brave",  
        "Charismatic",  
        "Devout"  
        ] 
        character_traits= numpy.array(character_traits)
        res = random.sample(range(1, 30), 1)

        user_text = f"Create 1 unique characters that are {character_traits[res[0]]} respectively"
        
        await self.create_content(
                oai_client=azure_open_ai_client,
                    system_prompt=prompt_json['character_json'][0],
                    prompt=user_text
                    )
        # print(character.content["Feature & Traits"])
        if self.player_number == 1:
            item = {
                "id":self.session_id,
                "sessionid_type":f"{self.session_id}_{self.type}",
                "session_id":self.session_id,
                "type":self.type,
                "player_number":self.player_number,
                f"charachter_definition_{self.player_number}":self.content["Definition"],
                f"character_stats_{self.player_number}":self.content["Stats"],
                f"character_saving_throws_{self.player_number}":self.content["Saving Throws"],
                f"character_skills_{self.player_number}":self.content["Skills"],
                f"character_health_{self.player_number}":self.content["Health"],
                f"character_attacks_n_spellcasting_{self.player_number}":self.content["Attacks and SpellCasting"],
                f"character_personality_{self.player_number}":self.content["Personality"],
                f"character_feature_n_traits_{self.player_number}":self.content["Feature & Traits"]
                }
        else:
            operations = [
                { 'op': 'add', 'path': f'/charachter_definition_{self.player_number}', 'value': self.content["Definition"]},
                { 'op': 'add', 'path': f'/charachter_definition_{self.player_number}', 'value': self.content["Stats"]},
                { 'op': 'add', 'path': f'/charachter_definition_{self.player_number}', 'value': self.content["Saving Throws"]},
                { 'op': 'add', 'path': f'/charachter_definition_{self.player_number}', 'value': self.content["Skills"]},
                { 'op': 'add', 'path': f'/charachter_definition_{self.player_number}', 'value': self.content["Health"]},
                { 'op': 'add', 'path': f'/charachter_definition_{self.player_number}', 'value': self.content["Attacks and SpellCasting"]},
                { 'op': 'add', 'path': f'/charachter_definition_{self.player_number}', 'value': self.content["Personality"]},
                { 'op': 'add', 'path': f'/charachter_definition_{self.player_number}', 'value': self.content["Feature & Traits"]}
                
                  ]
        
        azure_cosmos_client.insert_items(item)
        operations = [{ 'op': 'replace', 'path': '/update_reason', 'value': self.type },
                { 'op': 'add', 'path': f'/{self.type}_{self.player_number}_name', 'value': self.content["Definition"]["Character Name"]},
                { 'op': 'replace', 'path': '/player_count', 'value': self.player_number}
                    ]
        
        azure_cosmos_client.patching_items(self.session_id,f"{self.session_id}_session",operations)   
            # world_choice = input(f"Choose from the following: {characters_string}")
        
class Encounter(Location):
    def __init__(self,session):
        super().__init__(session)
        self.session_id= session.session_id
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
        # print(encounter)
        try:
            encounter_json= json.loads(encounter)
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
        except Exception as error:
            print(error)
        # self.encounter = json.loads(encounter)
        # print(self.encounter)
class Creatures(Encounter):
    def __init__(self, session):
        super().__init__(session)