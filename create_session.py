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

class Session():
    def __init__(self):
        self.session_id= 0
        self.environments={}
        self.user_enviroment_choice=""
        self.locations={}
        self.user_location_choice=""
        self.encounter={}



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
        user_text = "Create 4 Environments"
        environments = await azure_client.call_openai_model(system_message = prompt_json['environment_json'][0], 
                                    user_message = user_text, 
                                    model=azure_client.azure_oai_deployment
                                    )
        
        # clean output
        environments= environments.replace('```', '')
        environments= environments.replace('json', '')
        #store in session
        session.environments = json.loads(environments)
        environment_keys = list(session.environments.keys())
        
        #user choice
        session.user_enviroment_choice = input(f"Choose from the following: {environment_keys[0]}. ")
        environment_description = session.environments[session.user_enviroment_choice]["description"] 
        
        #Create locations
        user_text = f"Create 4 Locations using this description: {environment_description}"
        
        locations = await azure_client.call_openai_model(system_message = prompt_json['location_json'][0], 
                                    user_message = user_text, 
                                    model=azure_client.azure_oai_deployment
                                    )
        # clean output
        locations= locations.replace('```', '')
        locations= locations.replace('json', '')
        #store in session
        session.locations = json.loads(locations)
        locations_keys = list(session.locations.keys())
        
        #user choice
        session.user_location_choice = input(f"Choose from the following: {locations_keys[0]}. ")
        location_description = session.locations[session.user_location_choice]["description"]
        
        #Create encounter
        user_text = f"Create an encounter using this description: {location_description}"
        encounter = await azure_client.call_openai_model(system_message = prompt_json['encounter_json'][0], 
                                    user_message = user_text, 
                                    model=azure_client.azure_oai_deployment
                                    )
        # clean output
        encounter= encounter.replace('```', '')
        encounter= encounter.replace('json', '')
        #store in session
        session.encounter = json.loads(encounter)
        # encounter_keys = list(session.encounter.keys())
        print(session.encounter)

        
    except Exception as error:
        print(error) 

if __name__ == '__main__': 
    asyncio.run(main())