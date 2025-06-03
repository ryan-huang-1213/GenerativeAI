#!/usr/bin/env python3
# unified_server.py

import os
import re
import shutil
import subprocess
import tempfile
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import gradio as gr
from mcp.server.fastmcp import FastMCP
from groq import Groq

# ─── 讀取環境變數 ──────────────────────────────────────────────────────
load_dotenv()
LLM_KEY = os.getenv("GROQ_API_KEY")
if not LLM_KEY:
    raise RuntimeError("請先在 .env 或環境變數設定 GROQ_API_KEY")

MANIM_CLI = os.getenv("MANIM_EXECUTABLE", "manim")
# 所有輸出檔案集中存放在 media/
BASE_DIR = os.path.join(os.path.dirname(__file__), "media")
os.makedirs(BASE_DIR, exist_ok=True)

# ─── 建立 FastAPI + MCP────────────────────────────────────────────────
app = FastAPI(title="Geometry → Manim Service")
mcp = FastMCP(app=app)
llm_client = Groq(api_key=LLM_KEY)

# ─── 定義 ToolCall 型別 & 健康檢查 ─────────────────────────────────────
class ToolCall(BaseModel):
    name: str
    arguments: dict

@app.get("/health_check")
async def health_check():
    try:
        p = subprocess.run(
            [MANIM_CLI, "--version"],
            capture_output=True, text=True, timeout=5
        )
        return {"status": "healthy", "manim_version": p.stdout.strip()}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.post("/call")
async def call_tool(tc: ToolCall):
    if tc.name == "extract_constraints":
        return await extract_constraints(tc.arguments["text"])
    if tc.name == "supplement_parameters":
        return await supplement_parameters(tc.arguments["constraints_json"])
    if tc.name == "generate_manim_code":
        return await generate_manim_code(tc.arguments["params_json"])
    if tc.name == "execute_manim_code":
        return execute_manim_code(tc.arguments["manim_code"])
    if tc.name == "cleanup_manim_temp_dir":
        return cleanup_manim_temp_dir(tc.arguments["directory"])
    raise HTTPException(status_code=404, detail=f"Tool {tc.name} not found")

# ─── MCP 工具：提取 constraints ────────────────────────────────────────
@mcp.tool()
async def extract_constraints(text: str) -> dict:
    system = (
        "你是一個會從題目中抓取重要關鍵字的專業幾何題目標註助理。並會將他們整理成 JSON 格式"
        "你會看到一個題目或是題組，你需要將題目以及子題所需要的幾何圖形完整描述，目標是可以通過這些描述畫出一個完整的圖形"
        "你需要找出題目中所有的圖形以及其包含的點 ( 比如 三角形ABC ) 、線段以及其包含的點 ( 比如 線段AB )"
        "、角度以及其包含的點 ( 比如 角A、角ACB 等等 )、以及點 ( 比如 A、B、C 等等 )，"
        "並且備註每個圖形、線段、角度、頂點的特殊條件 ( 也有可能沒有特殊條件 ) "
        "如 [{\"type\":\"constraint\",\"expr\":\"...\"}, ...]，不要額外文字。"
    )
    resp = llm_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": text}
        ]
    )
    return {"constraints_json": resp.choices[0].message.content}

# ─── MCP 工具：補全參數 ───────────────────────────────────────────────
@mcp.tool()
async def supplement_parameters(constraints_json: str) -> dict:
    system = (
        "你是一個專業的幾何參數生成器，根據 constraints JSON，產生具體的點座標和線段定義，"
        "具體要產生的座標，你需要撙手以下幾點：1. 座標要符合題目以及 json 的相關幾何限制 2. 產生出的座標應該要不失一般性 3. 一定要完善所有座標連線等等"
        "回傳純 JSON，如 {points:{{}}, lines:[], polygons:[], circles:[] }，不要額外文字。"
    )
    resp = llm_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": constraints_json}
        ]
    )
    return {"params_json": resp.choices[0].message.content}

# ─── MCP 工具：產生 Manim 程式碼 ──────────────────────────────────────
@mcp.tool()
async def generate_manim_code(params_json: str) -> dict:
    system = (
        "你是一個資深 Python 程式設計師，會寫出完成全正確的程式，參考內容"
        "從頭編寫一個 manim 腳本，運用提供的 JSON 參數，但不要直接死板的使用 JSON 參數。"
        "你應該要理解 JSON 參數的內容後，直接將參數寫進 manim 的函式中，撰寫一個可以繪製該圖形的程式"
        "只需輸出腳本內容，不要額外文字。"
        "請注意，這是一個完整的 Python 腳本，包含必要的 import 語句。"
        "請確保程式碼可以直接執行。"
    )
    resp = llm_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": params_json}
        ]
    )
    return {"manim_code": resp.choices[0].message.content}

# ─── MCP 工具：執行 Manim、回傳檔案路徑 ───────────────────────────────
def execute_manim_code(manim_code: str) -> dict:
    # 1) 去除 Markdown fence
    lines = manim_code.splitlines()
    if lines and re.match(r"^```(?:python)?\s*$", lines[0]):
        lines = lines[1:]
    if lines and re.match(r"^```\s*$", lines[-1]):
        lines = lines[:-1]
    clean_code = "\n".join(lines)

    # 2) 補三維：Dot([x, y]) → Dot([x, y, 0])
    pattern = re.compile(
        r"(Dot\(\s*(?:point\s*=\s*)?\[\s*([^,\]]+)\s*,\s*([^,\]]+)\s*\])"
    )
    def pad_dot(m):
        orig, x, y = m.group(1), m.group(2).strip(), m.group(3).strip()
        return orig.replace(f"[{x}, {y}]", f"[{x}, {y}, 0]")
    code = pattern.sub(pad_dot, clean_code)

    # 3) 建立唯一 tmpdir（避免覆寫）:contentReference[oaicite:2]{index=2}
    tmpdir = tempfile.mkdtemp(dir=BASE_DIR, prefix="manim_")
    scene_py = os.path.join(tmpdir, "scene.py")
    with open(scene_py, "w", encoding="utf-8") as f:
        f.write(code)

    # 4) 呼叫 Manim CLI
    try:
        proc = subprocess.run(
            [MANIM_CLI, "-p", scene_py],
            cwd=tmpdir, capture_output=True, text=True, timeout=300
        )
    except subprocess.TimeoutExpired:
        return {"error": "Execution timed out after 5 minutes"}

    if proc.returncode != 0:
        return {"error": proc.stderr}

    # 5) 掃描 .mp4 / .png，並回傳第一個找到的路徑 :contentReference[oaicite:3]{index=3}
    for root, _, files in os.walk(tmpdir):
        for fn in files:
            if fn.endswith((".mp4", ".png")):
                return {"path": os.path.join(root, fn)}
    return {"error": "No output file found"}

# ─── MCP 工具：清理臨時目錄 ───────────────────────────────────────────
def cleanup_manim_temp_dir(directory: str) -> dict:
    if os.path.exists(directory):
        shutil.rmtree(directory)
        return {"message": f"Cleaned up {directory}"}
    return {"message": f"Directory not found: {directory}"}

# ─── Gradio 前端介面 ──────────────────────────────────────────────────
def create_gradio_app():
    with gr.Blocks() as demo:
        gr.Markdown("## 幾何題目 → Manim 圖形／影片 生成器")
        prompt      = gr.Textbox(label="題目敘述", lines=4, placeholder="輸入幾何題目")
        show_detail = gr.Checkbox(label="顯示詳細 JSON 與程式碼", value=False)
        btn         = gr.Button("生成")
        output_file = gr.File(label="生成結果（可預覽並下載）")
        detail_md   = gr.Markdown()

        async def run_all(text, detail_flag):
            cons   = await extract_constraints(text)
            params = await supplement_parameters(cons["constraints_json"])
            code   = await generate_manim_code(params["params_json"])
            exec_r = execute_manim_code(code["manim_code"])
            if "error" in exec_r:
                raise gr.Error(exec_r["error"])

            details = ""
            if detail_flag:
                details = (
                    "#### Constraints JSON\n```json\n"
                    f"{cons['constraints_json']}\n```\n\n"
                    "#### Parameters JSON\n```json\n"
                    f"{params['params_json']}\n```\n\n"
                    "#### Manim 程式碼\n```python\n"
                    f"{code['manim_code']}\n```"
                )
            return exec_r["path"], details

        btn.click(fn=run_all,
                  inputs=[prompt, show_detail],
                  outputs=[output_file, detail_md])
    return demo

# ─── 掛載並啟動服務 ───────────────────────────────────────────────────
gr_app = create_gradio_app()
app = gr.mount_gradio_app(app, gr_app, path="/")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
