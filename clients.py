from openai import AsyncAzureOpenAI
import requests
import os
import asyncio
import json
from azure.cosmos import CosmosClient



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

class AzureCosmosDBClient():

    def __init__(self):
        self.URL = os.environ['COSMOS_ACCOUNT_URI']
        self.KEY = os.environ['COSMOS_ACCOUNT_KEY']
        self.database = os.environ['COSMOS_DATABASE_NAME']
        self.container = os.environ['COSMOS_CONTAINER_NAME']
        self.client = CosmosClient(self.URL, credential=self.KEY)
    
    def insert_items(self,item):
        database = self.client.get_database_client(self.database)
        container = database.get_container_client(self.container)
        container.upsert_item(
                    item
        )