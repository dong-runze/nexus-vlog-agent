import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

class MemoryEngine:
    def __init__(self):
        self.client = genai.Client(
            vertexai=True,
            project=os.environ["GCP_PROJECT_ID"],
            location=os.environ["GCP_LOCATION"]
        )
        # Vertex AI 的标准嵌入模型
        self.model_id = "text-embedding-004"

    async def generate_embedding(self, text: str):
        """将场景文字转化为高维向量"""
        try:
            result = self.client.models.embed_content(
                model=self.model_id,
                contents=text
            )
            # 返回嵌入向量
            return result.embeddings[0].values
        except Exception as e:
            print(f"Embedding Error: {e}")
            return None