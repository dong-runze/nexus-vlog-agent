import os
from google import genai
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize the Vertex AI client
client = genai.Client(
    vertexai=True, 
    project=os.environ["GCP_PROJECT_ID"], 
    location=os.environ["GCP_LOCATION"]
)

print(f"Current Project ID: {os.environ['GCP_PROJECT_ID']}")
print("Pinging Vertex AI...")

# Execute the Ping
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents="You are the core intelligence of the Nexus Architect. Are your multimodal systems online in Vertex AI?"
)

print("Response:")
print(response.text)
