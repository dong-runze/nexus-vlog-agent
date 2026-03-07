import asyncio
import json
import uuid
import traceback
import os
import shutil
import pandas as pd
import plotly.express as px
from sklearn.decomposition import PCA
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# 🚨 正式解除封印：导入你的核心 AI 模块
from vision_parser import VlogVisionEngine
from memory_engine import MemoryEngine
from vector_memory import LocalNumpyVectorDB, VectorRecord

app = FastAPI(title="Nexus Vlog Memory Broadcasting Engine")
# Ensure upload directory exists
os.makedirs("data/uploads", exist_ok=True)
app.mount("/data/uploads", StaticFiles(directory="data/uploads"), name="uploads")

# ==========================================
# 核心引擎初始化 (全局单例)
# ==========================================
print("初始化 AI 引擎中...")
vision_engine = VlogVisionEngine()
memory_engine = MemoryEngine()
vector_db = LocalNumpyVectorDB()
print("引擎初始化完毕！")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = f"data/uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename}

@app.get("/visualize")
async def visualize_memory():
    records = list(vector_db._storage.values())
    
    if len(records) < 3:
        return HTMLResponse(content="<h1>Not enough memories yet! Upload at least 3 videos to form a galaxy.</h1>", status_code=400)
    
    embeddings = [r.embedding for r in records]
    scenes = [r.metadata.get("scene", "Unknown") if r.metadata else "Unknown" for r in records]
    tones = [r.metadata.get("emotional_tone", "Unknown") if r.metadata else "Unknown" for r in records]
    file_paths = [f"/data/uploads/{r.metadata.get('filename', '')}" if r.metadata and "filename" in r.metadata else "" for r in records]
    
    n_components = 3
    pca = PCA(n_components=n_components)
    reduced_embeddings = pca.fit_transform(embeddings)
    
    df = pd.DataFrame(reduced_embeddings, columns=['x', 'y', 'z'])
    df["Scene"] = scenes
    df["Tone"] = tones
    df["file_path"] = file_paths
    
    fig = px.scatter_3d(df, x='x', y='y', z='z', color='Tone', hover_name='Scene', custom_data=['file_path'], template='plotly_dark', title='Nexus Memory Galaxy')
    fig.update_traces(marker=dict(size=8))
    
    html_content = fig.to_html(full_html=True)
    
    script = """
    <script>
    document.addEventListener("DOMContentLoaded", function() {
        var gd = document.getElementsByClassName('plotly-graph-div')[0];
        
        gd.on('plotly_hover', function(data){
            const filePath = data.points[0].customdata[0];
            const preview = window.parent.document.getElementById('memory-preview-hover');
            const video = window.parent.document.getElementById('preview-vid');
            const img = window.parent.document.getElementById('preview-img');
            
            if (!filePath || filePath === "/data/uploads/" || !preview) return;
            
            preview.style.display = 'block';
            
            // Positioning relative to mouse
            document.addEventListener('mousemove', function movePreview(e) {
                if (preview.style.display !== 'none') {
                    preview.style.left = (e.clientX + 15) + 'px';
                    preview.style.top = (e.clientY + 15) + 'px';
                } else {
                    document.removeEventListener('mousemove', movePreview);
                }
            });
            
            if (filePath.toLowerCase().endsWith('.mp4') || filePath.toLowerCase().endsWith('.webm') || filePath.toLowerCase().endsWith('.mov')) {
                if(img) img.style.display = 'none';
                if(video) {
                    video.src = filePath;
                    video.style.display = 'block';
                }
            } else {
                if(video) video.style.display = 'none';
                if(img) {
                    img.src = filePath;
                    img.style.display = 'block';
                }
            }
        });
        
        gd.on('plotly_unhover', function(data){
            const preview = window.parent.document.getElementById('memory-preview-hover');
            if(preview) preview.style.display = 'none';
        });
    });
    </script>
    """
    
    html_content = html_content.replace('</body>', script + '</body>')
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/")
async def serve_frontend():
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content, status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Error: index.html not found!</h1>", status_code=404)

@app.websocket("/ws/agent")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("🟢 [Backend] WebSocket Connected!") 
    
    try:
        while True:
            raw_data = await websocket.receive_text()
            print(f"📩 [Backend] Received: {raw_data}") 

            try:
                payload = json.loads(raw_data)
                command = payload.get("command")

                if command == "start":
                    # --- 1. 触发视觉解析 (VLM) ---
                    filename = payload.get("filename")
                    model_id = payload.get("model", "gemini-2.5-flash")
                    
                    if not filename:
                        await websocket.send_json({"type": "thought", "content": "ERROR: No filename provided for synthesis."})
                        continue
                        
                    await websocket.send_json({"type": "tool_call", "content": f"{model_id.upper()} scanning {filename}..."})
                    
                    video_path = f"data/uploads/{filename}"
                    parsed_result = await vision_engine.analyze_vlog_segment(video_path, model_id=model_id)
                    
                    # Store filename so /visualize knows exactly where the asset is
                    parsed_result["filename"] = filename
                    
                    scene_name = parsed_result.get("scene", "Unknown Environment")
                    tone = parsed_result.get("emotional_tone", "neutral")
                    await websocket.send_json({"type": "thought", "content": f"Memory Fragment synthesized: {scene_name}"})

                    # --- 2. 触发向量计算 (Embedding) ---
                    await websocket.send_json({"type": "db_search", "content": "Indexing fragment into 768-dim vector space..."})
                    
                    text_to_embed = json.dumps(parsed_result, ensure_ascii=False)
                    embedding_vector = await memory_engine.generate_embedding(text_to_embed)

                    if embedding_vector:
                        # --- 3. 存入本地向量数据库 ---
                        record_id = str(uuid.uuid4())
                        record = VectorRecord(id=record_id, embedding=embedding_vector, metadata=parsed_result)
                        await vector_db.insert(record)
                        
                        await websocket.send_json({"type": "thought", "content": f"Geometry finalized in us-central1 datacenter. [ID: {record_id[:8]}]"})
                        summary_msg = f"I've analyzed your vlog and identified a scene of {scene_name} with a {tone} vibe. Memory indexed!"
                        await websocket.send_json({"type": "message", "content": summary_msg})
                    else:
                        await websocket.send_json({"type": "thought", "content": "ERROR: Vector embedding generation failed."})

                elif command == "search":
                    query = payload.get("query")
                    model_id = payload.get("model", "gemini-2.5-flash")
                    query_lower = query.lower()
                    visual_keywords = ["visualize", "map", "plot", "galaxy", "space"]
                    
                    if any(kw in query_lower for kw in visual_keywords):
                        await websocket.send_json({"type": "message", "content": "Memory Galaxy generated. <a href='/visualize' target='_blank' style='color:#2ea043; text-decoration:underline;'>[Click here to view Vector Space]</a>"})
                        continue
                        
                    await websocket.send_json({"type": "db_search", "content": f"Computing Cosine Similarity for query: '{query}'..."})
                    
                    # Convert the query into a 768-dim vector
                    query_embedding = await memory_engine.generate_embedding(query)
                    
                    if query_embedding:
                        # Perform mathematically similar semantic search (Cosine Similarity)
                        matches = await vector_db.search(query_embedding, top_k=1)
                        
                        if matches:
                            top_match = matches[0]
                            meta = top_match.metadata or {}
                            
                            await websocket.send_json({"type": "thought", "content": f"Memory Extracted. Invoking LLM ({model_id}) for generative analysis..."})
                            
                            # --- Dynamic LLM RAG Response ---
                            rag_prompt = f"You are a helpful, supportive Memory Agent. Based on these retrieved metadata details: {json.dumps(meta, ensure_ascii=False)}, answer the user's question: '{query}' in a natural, supportive tone. Do not use a strict template. Be conversational."
                            
                            try:
                                rag_response = vision_engine.client.models.generate_content(
                                    model=model_id,
                                    contents=rag_prompt
                                )
                                generated_llm_text = rag_response.text
                            except Exception as llm_err:
                                generated_llm_text = f"I found the memory (Scene: {meta.get('scene')}), but couldn't generate a conversational response due to an LLM error."
                                print(f"LLM RAG Error: {llm_err}")
                            
                            # 获取匹配分数 (Cosine Similarity)
                            dot = sum(a*b for a,b in zip(query_embedding, top_match.embedding))
                            norm = (sum(a*a for a in query_embedding)**0.5) * (sum(b*b for b in top_match.embedding)**0.5)
                            top_score = dot / norm if norm > 0 else 0.0
                            
                            confidence_tag = f"[Confidence: {top_score:.2f}] "
                            final_response = confidence_tag + generated_llm_text
                            
                            await websocket.send_json({"type": "message", "content": final_response})
                        else:
                            await websocket.send_json({"type": "message", "content": "Memory Not Found: No matching memory clusters stored."})
                    else:
                        await websocket.send_json({"type": "thought", "content": "ERROR: Failed to computationally embed the query text."})

            except Exception as logic_err:
                print("❌ [Backend] Logic Error:")
                traceback.print_exc() 
                await websocket.send_json({"type": "thought", "content": f"CRITICAL ERROR: {str(logic_err)}"})
                
    except WebSocketDisconnect:
        print("🟡 [Backend] Client disconnected.")
    except Exception as e:
        print(f"🔴 [Backend] WebSocket Error: {str(e)}")