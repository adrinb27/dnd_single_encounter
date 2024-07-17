import os
import asyncio
import json 
import requests
from dotenv import load_dotenv
# Add OpenAI import
from openai import AsyncAzureOpenAI

# Add Azure OpenAI package
## List:
# - Session:
#     - Location
#     - Envirioment
#     - Characters
#     - Encounter Goal


# Set to True to print the full response from OpenAI for each call
printFullResponse = False
load_dotenv()

class Session():
    def __init__(self):
        self.session_id= 0
class Encounter():
    def __init__(self):
        self.encounter_id = 0
        self.title = ""
        self.summary = ""
        self.location = ""
        self.image_prompt = {}
        self.vision_prompt = {
            "vision": "",
            "vision_system": "",
            "location": "top",
            "location_padding": 50,
            "font_color": "#FFFFFF",
            "has_text": False
        }
class Location():
    def __init__(self) -> None:
        pass
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

        if printFullResponse:
            print(response)

        print("Response:\n" + response.choices[0].message.content + "\n")

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

async def main(): 
        
    try: 

        # import system prompts
        with open("prompt.json") as prompt_file:
            prompt_json=json.load(prompt_file)
        
        # Configure the Azure OpenAI client
        azure_client = AzureOpenAIClient()

        # Read in system message and prompt for user message
        user_text = input("Enter user message, or 'quit' to exit: ")
        if user_text.lower() == 'quit':
            print('Exiting program...')
            exit()
        
        theme_response = await azure_client.call_openai_model(system_message = prompt_json['theme'][0], 
                                user_message = user_text, 
                                model=azure_client.azure_oai_deployment
                                )
        
        # How many characters?
        # Loop through and create them and choice 
        character_choices = await azure_client.call_openai_model(system_message = prompt_json['character_choices'][0], 
                                user_message = theme_response, 
                                model=azure_client.azure_oai_deployment
                                )
        
        # character_picture = await azure_client.call_openai_model(system_message = prompt_json['character_picture'][0], 
        #                         user_message = character_choices, 
        #                         model=azure_client.azure_oai_deployment
        #                         )
        
        backstory = await azure_client.call_openai_model(system_message = prompt_json['backstory'][0], 
                                user_message = character_choices, 
                                model=azure_client.azure_oai_deployment
                                )
        
        # await azure_client.call_dalee(
        #     model=azure_client.azure_dalle_deployment,
        #     prompt=character_picture,
        #     file_name=picture_name)


    except Exception as ex:
        print(ex)

if __name__ == '__main__': 
    asyncio.run(main())