import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

class VlogVisionEngine:
    def __init__(self):
        # 初始化客户端，使用你刚跑通的配置
        self.client = genai.Client(
            vertexai=True,
            project=os.environ["GCP_PROJECT_ID"],
            location=os.environ["GCP_LOCATION"]
        )
        # 使用验证成功的 2.5 Flash 模型
        self.model_id = "gemini-2.5-flash"

    async def analyze_vlog_segment(self, file_path: str, model_id: str = None):
        """解析媒体文件并输出结构化记忆 JSON"""
        
        # 读取文件
        with open(file_path, "rb") as f:
            media_content = f.read()

        # 精确设计的提示词，确保存入向量数据库的质量
        prompt = """
        As an advanced Vlog Memory Analyst, deeply review this 10-second media segment. Beyond basic descriptions, perform semantic reasoning to extract core memories.
        {
          "scene": "A concise scene name",
          "detailed_actions": ["List of decomposed actions observed"],
          "inferred_location": "Specific location inferred from visual cues (e.g., a specific brand cafe, home office)",
          "emotional_tone": "The emotional atmosphere (e.g., cozy, hectic, nostalgic)",
          "memory_tag": "A short, searchable tag for indexing"
        }
        """

        try:
            target_model = model_id if model_id else self.model_id
            # 执行多模态推理
            response = self.client.models.generate_content(
                model=target_model,
                contents=[
                    types.Part.from_bytes(data=media_content, mime_type="video/mp4"),
                    types.Part.from_text(text=prompt)
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Vision Engine Error: {e}")
            return {"error": "Processing failed"}