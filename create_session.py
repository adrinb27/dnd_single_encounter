import os
import asyncio
import json 
import requests
from dotenv import load_dotenv
# Add OpenAI import
from openai import AsyncAzureOpenAI
import random

printFullResponse = False
load_dotenv()

class AzureOpenAIClient():

    def __init__(self):
        self.azure_oai_endpoint = os.getenv("AZURE_OAI_ENDPOINT")
        self.azure_oai_key = os.getenv("AZURE_OAI_KEY")
        self.azure_oai_deployment = os.getenv("AZURE_OAI_DEPLOYMENT")
        self.azure_dalle_deployment= os.getenv("AZURE_DALLE_DEPLOYMENT")
        self.client = AsyncAzureOpenAI(
            azure_endpoint = self.azure_oai_endpoint, 
            api_key=self.azure_oai_key,  
            api_version="2024-02-15-preview"
            )
    async def call_openai_model(self,system_message, user_message, model):
        # Format and send the request to the model
        
        messages =[
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
        ]

        print("\nSending request to Azure OpenAI model...\n")

        # Call the Azure OpenAI model
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=800
        )

        # print("Response:\n" + response.choices[0].message.content + "\n")
        # print(response)
        return response.choices[0].message.content
    
    async def call_dalee(self,model,prompt,file_name):
        dalle_response = await self.client.images.generate(
                        model=model,
                        prompt=prompt,
                        n=1,
                        size="1024x1792"
                    )
            
        json_response = json.loads(dalle_response.model_dump_json())

        # Extract the URL of the generated image
        image_url = json_response["data"][0]["url"]
        image_response = requests.get(image_url)
        directory = "images"

        # Check if the directory already exists
        if not os.path.exists(directory):
            # Create the directory
            os.makedirs(directory)
            print("Directory created successfully!")
        else:
            print("Directory already exists!")
        
        #saves image locally    
        if image_response.status_code == 200:
            with open(f'{directory}\{file_name}.png', 'wb') as f:
                f.write(image_response.content)
            print("Image downloaded and saved as 'generated_image.png'")
        else:
            print("Failed to download the image")
#TODO save only world chosen
class Session():
    def __init__(self):
        self.session_id= 0
        self.world={}
        self.locations={}
        self.user_location_choice=""
        self.encounter={}
    
    async def world_creation(self,client,system_prompt,prompt):
        
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

        
    async def location_creation(self,client,system_prompt,prompt):
        
        locations = await client.call_openai_model(system_message = system_prompt, 
                                    user_message = prompt, 
                                    model=client.azure_oai_deployment
                                    )
        # clean output
        locations= locations.replace('```', '')
        locations= locations.replace('json', '')
        
        #store in session
        location_json = json.loads(locations)
        # location_json = location_json[list(location_json.keys())[0]]
        if isinstance(location_json[list(location_json.keys())[0]],list):
            self.locations = transform(location_json[list(location_json.keys())[0]])
        elif isinstance(location_json[list(location_json.keys())[0]],dict):
            self.locations = location_json

    async def encounter_creation(self,client,system_prompt,prompt):
        encounter = await client.call_openai_model(system_message = system_prompt, 
                                    user_message = prompt, 
                                    model=client.azure_oai_deployment
                                    )
        # clean output
        encounter= encounter.replace('```', '')
        encounter= encounter.replace('json', '')
        # print(encounter)
        #store in session
        encounter_json= json.loads(encounter)
        print(encounter_json)
        if isinstance(encounter_json[list(encounter_json.keys())[0]],list):
            self.encounter = transform(encounter_json[list(encounter_json.keys())[0]])
            print("it is a list",self.encounter)
        elif isinstance(encounter_json[list(encounter_json.keys())[0]],dict):
            self.encounter = encounter_json
            print("it is a dictionary",self.encounter)
        elif isinstance(encounter_json,dict):
            self.encounter = encounter_json
        # self.encounter = transform(encounter_json["encounter"])

        # self.encounter = json.loads(encounter)
        print(self.encounter)



async def main():
    try:
        # import system prompts
        with open("prompt.json") as prompt_file:
            prompt_json=json.load(prompt_file)
        
        #Create session and open ai client
        azure_client = AzureOpenAIClient()
        session = Session()
        session.session_id = ''.join(random.choice('0123456789') for i in range(8))
        
        # Create enviroments and store name on a list
        user_text = "Create 4 worlds"

        # Create environment
        await session.world_creation(
            client=azure_client,
            system_prompt=prompt_json['environment_json'][0],
            prompt=user_text
        )
        
        # worlds_string = create_string_from_dict_attributes(session.worlds)
        
        # #user choice
        # session.user_enviroment_choice = input(f"Choose from the following: {worlds_string}")
        # environment_description = session.worlds[session.user_enviroment_choice]["description"] 
        
        # #Create locations
        # user_text = f"Create 4 Locations using this description: {environment_description}"
        # # Create location
        # await session.location_creation(
        #     client = azure_client,
        #     system_prompt = prompt_json['environment_json'][0],
        #     prompt = user_text
        #     )
        
        # locations_string = create_string_from_dict_attributes(session.locations)
        
        # #user choice
        # session.user_location_choice = input(f"Choose from the following: {locations_string}")
        # location_description = session.locations[session.user_location_choice]["description"]
        
        
        # user_text = f"Create an encounter using this description: {location_description}"
        # # print(user_text)
        # await session.encounter_creation(
        #     client=azure_client,
        #     system_prompt=prompt_json['encounter_json'][0],
        #     prompt=user_text
        # )

        
    except Exception as error:
        print(error) 

def create_string_from_dict_attributes(dict):
  """Creates a string out of the attributes of a dictionary.

  Args:
    dict: The dictionary to convert to a string.

  Returns:
    A string containing the attributes of the dictionary.
  """

  string = ""
  last = list(dict.keys())[-1]
  for key in list(dict.keys()):
    if key == last:
      string += f"and {key}. "
    else:
        string += f"{key}, "
  return string

def transform(array):
    new_dict = {}
    for item in array:
        name = item['name']
        new_dict[name] = item
    return new_dict




if __name__ == '__main__': 
    asyncio.run(main())