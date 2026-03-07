## Nexus: The Multi-modal Vlog Memory Agent 

# 🚀Nexus is an advanced AI agent designed to transform raw, unstructured Vlog media into a searchable, interactive, and intelligent "Second Brain." By leveraging the power of Gemini 2.5 Flash and high-dimensional vector embeddings, Nexus allows users to bridge the gap between recording life and recalling it.

# 🧠 Design Philosophy
The core philosophy behind Nexus is Active Intelligence. Traditional media storage is a "data graveyard"—files are stored but rarely retrieved due to the effort required to search through video content.Nexus solves this by:Deconstructing Reality: Using Visual Language Models (VLM) to perceive video frames like a human.Mathematical Indexing: Projecting human experiences into a 768-dimensional vector space where "similar experiences" are mathematically close.Conversational Retrieval: Moving beyond keyword search to a natural, generative dialogue with your own past.

# ✨ Core FeaturesIntelligent Media Ingestion: 
Automatically scans uploaded MP4/Image files using Gemini 2.5 Flash to identify scenes, objects, and emotional tones.Semantic Memory Search: Instead of filenames, search by context. For example, "When was I checking the map?".Generative RAG Feedback: The agent doesn't just find the file; it summarizes the memory and answers your questions with Match Confidence Scores.Memory Galaxy (3D Visualization): An interactive 3D map of your database. Memories are clustered by "Vibe" (Emotional Tone) using PCA dimensionality reduction.Multi-Model Support: Dynamically switch between Gemini 2.5 Flash, 2.0 Flash, and 3 Pro to optimize for speed or depth.

# 🛠️ Technical ImplementationThe Math Behind the MemoryNexus calculates the Cosine Similarity between your natural language query vector  and stored memory vectors score of 0.89 indicates a high-confidence semantic match.
Tech StackLLM/VLM: Google Gemini 2.5 Flash via Vertex AI.
Backend: FastAPI with WebSockets for real-time log broadcasting.
Vector Engine: Local Numpy-based Vector Database.
Visualization: Plotly.js & Scikit-learn (PCA).

# 🚀 Installation & Usage1. PrerequisitesGoogle Cloud Project with Vertex AI API enabled.Docker installed (for deployment).Python 3.11+.2. Local SetupBash# Clone the repository
# git clone [https://github.com/your-username/nexus-vlog-agent.git](https://github.com/dong-runze/nexus-vlog-agent.git)
cd nexus-vlog-agent
# my cloud deployment: https://nexus-agent-950282885470.us-central1.run.app

# Install dependencies
pip install -r requirements.txt

# Set up your GCP credentials
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your-service-account.json"

# Run the server
uvicorn main:app --reload
3. UsageOpen http://localhost:8000.Click 📎 to upload a Vlog clip.Watch the VLM_SCANNER logs in real-time as it indexes your memory.Type a query (e.g., "A plane") and get a generative summary of the match.Type "show map" to launch the 3D Galaxy View.4. Cloud Deployment (Google Cloud Run)Bash# Ensure gcloud is configured
gcloud config set project [YOUR_PROJECT_ID]

# Execute the deployment script
bash deploy.sh
🏆 Hackathon Submission DetailsCategory: Applied AI / Multi-modal RAG.Core Achievement: Successfully implemented a full-stack, low-latency video-to-knowledge pipeline using Gemini's latest 2026 APIs.
