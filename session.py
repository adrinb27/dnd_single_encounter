import random
import json
from utils import create_string_from_dict_attributes

class Session():
    def __init__(self):
        self.session_id= ''.join(random.choice('0123456789') for i in range(8))

class World(Session):
    
    def __init__(self,session):
        super().__init__()
        self.session_id= session.session_id
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