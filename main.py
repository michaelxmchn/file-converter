#!/usr/bin/env python3
"""
File Converter - Web 服务主程序
支持 PDF 转 Word 等文件格式转换
"""

import os
import uuid
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import aiofiles
import asyncio

# 导入转换模块
from scripts.pdf_handler import pdf_to_word
from scripts.pdf_to_ppt import pdf_to_ppt

# 配置路径
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
STATIC_DIR = BASE_DIR / "static"
DATA_DIR = BASE_DIR / "data"

# 确保目录存在
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

REQUESTS_FILE = DATA_DIR / "requests.json"

# 数据模型
class FeatureRequest(BaseModel):
    title: str
    description: str
    contact: Optional[str] = None
    priority: str = "normal"

# 创建 FastAPI 应用
app = FastAPI(
    title="文件转换器",
    description="PDF 转 Word 等文件格式转换工具",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建 HTML 页面
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>文件转换器 - 功能需求提交</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 600px;
            width: 100%;
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        .tabs {
            display: flex;
            margin-bottom: 30px;
            border-bottom: 2px solid #eee;
        }
        .tab {
            flex: 1;
            padding: 15px;
            text-align: center;
            cursor: pointer;
            color: #666;
            transition: all 0.3s;
            border-bottom: 2px solid transparent;
            margin-bottom: -2px;
        }
        .tab.active {
            color: #667eea;
            border-bottom-color: #667eea;
            font-weight: bold;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }
        .form-group input,
        .form-group textarea,
        .form-group select {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        .form-group input:focus,
        .form-group textarea:focus,
        .form-group select:focus {
            outline: none;
            border-color: #667eea;
        }
        .form-group textarea {
            resize: vertical;
            min-height: 100px;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 30px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s;
            display: inline-block;
            width: 100%;
            margin: 5px 0;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }
        .btn-secondary {
            background: #f0f4ff;
            color: #667eea;
        }
        .message {
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: none;
        }
        .message.success {
            background: #d4edda;
            color: #155724;
            display: block;
        }
        .message.error {
            background: #f8d7da;
            color: #721c24;
            display: block;
        }
        .features {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }
        .features h3 {
            color: #333;
            margin-bottom: 15px;
        }
        .features ul {
            list-style: none;
            color: #666;
        }
        .features li {
            padding: 5px 0;
        }
        .features li::before {
            content: "✓";
            color: #667eea;
            margin-right: 10px;
        }
        .upload-area {
            border: 3px dashed #667eea;
            border-radius: 15px;
            padding: 40px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            margin-bottom: 20px;
        }
        .upload-area:hover {
            background: #f0f4ff;
            border-color: #764ba2;
        }
        .upload-area.dragover {
            background: #e8edff;
            border-color: #764ba2;
        }
        .upload-icon {
            font-size: 60px;
            margin-bottom: 15px;
        }
        .upload-text {
            color: #666;
            margin-bottom: 10px;
        }
        #fileInput {
            display: none;
        }
        .file-info {
            background: #f8f9ff;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            display: none;
        }
        .file-name {
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }
        .progress {
            width: 100%;
            height: 10px;
            background: #e0e0e0;
            border-radius: 5px;
            overflow: hidden;
            margin: 15px 0;
        }
        .progress-bar {
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            width: 0%;
            transition: width 0.3s;
        }
        .status {
            text-align: center;
            color: #666;
            margin-top: 10px;
        }
        .download-link {
            display: none;
            text-align: center;
            margin-top: 20px;
        }
        .download-link a {
            color: #667eea;
            text-decoration: none;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📄 文件转换器</h1>
        <p class="subtitle">PDF 转 Word | 功能需求提交</p>
        
        <div class="tabs">
            <div class="tab active" onclick="switchTab('convert')">🔄 文件转换</div>
            <div class="tab" onclick="switchTab('request')">💡 提交需求</div>
        </div>
        
        <!-- 转换页面 -->
        <div class="tab-content active" id="convertTab">
            <div class="upload-area" id="uploadArea">
                <div class="upload-icon">📁</div>
                <p class="upload-text">将 PDF 文件拖放到这里，或点击选择文件</p>
                <input type="file" id="fileInput" accept=".pdf">
            </div>
            
            <div class="form-group">
                <label>转换类型</label>
                <select id="convertType" onchange="updateConvertBtn()">
                    <option value="ppt">📄 PDF 转 PPT (演示文稿)</option>
                    <option value="word">📝 PDF 转 Word (文档)</option>
                </select>
            </div>
            
            <div class="file-info" id="fileInfo">
                <div class="file-name" id="fileName"></div>
                <div class="progress">
                    <div class="progress-bar" id="progressBar"></div>
                </div>
                <div class="status" id="status">准备转换...</div>
            </div>
            
            <div style="text-align: center;">
                <button class="btn" id="convertBtn" disabled onclick="convertFile()">开始转换</button>
                <button class="btn btn-secondary" onclick="clearAll()">清除</button>
            </div>
            
            <div class="download-link" id="downloadLink">
                <p>✅ 转换完成！</p>
                <a id="downloadBtn" class="btn" href="#" download>📥 下载文件</a>
            </div>
            
            <div class="features">
                <h3>✨ 支持的功能</h3>
                <ul>
                    <li>PDF 转 PPT (.pptx)</li>
                    <li>PDF 转 Word (.docx)</li>
                    <li>保留原始格式和布局</li>
                    <li>本地处理，保护隐私</li>
                </ul>
            </div>
        </div>
        
        <!-- 需求提交页面 -->
        <div class="tab-content" id="requestTab">
            <div id="message" class="message"></div>
            
            <form id="requestForm" onsubmit="submitRequest(event)">
                <div class="form-group">
                    <label>需求标题 *</label>
                    <input type="text" id="title" placeholder="例如：支持 Excel 转 PDF" required>
                </div>
                
                <div class="form-group">
                    <label>详细描述 *</label>
                    <textarea id="description" placeholder="请详细描述你需要的功能..." required></textarea>
                </div>
                
                <div class="form-group">
                    <label>联系方式（可选）</label>
                    <input type="text" id="contact" placeholder="微信/QQ/邮箱，方便我们联系你">
                </div>
                
                <div class="form-group">
                    <label>优先级</label>
                    <select id="priority">
                        <option value="normal">一般需求</option>
                        <option value="high">急需</option>
                        <option value="low">有空再做</option>
                    </select>
                </div>
                
                <button type="submit" class="btn">📨 提交需求</button>
            </form>
            
            <div class="features">
                <h3>📋 已实现的功能</h3>
                <ul id="implementedList">
                    <li>✅ PDF 转 PPT (.pptx) - 新功能！</li>
                    <li>✅ PDF 转 Word (.docx)</li>
                </ul>
            </div>
        </div>
    </div>
    
    <script>
        // Tab 切换
        function switchTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById(tab + 'Tab').classList.add('active');
        }
        
        // 提交需求
        async function submitRequest(event) {
            event.preventDefault();
            
            const title = document.getElementById('title').value;
            const description = document.getElementById('description').value;
            const contact = document.getElementById('contact').value;
            const priority = document.getElementById('priority').value;
            
            try {
                const response = await fetch('/api/request', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        title,
                        description,
                        contact,
                        priority
                    })
                });
                
                const result = await response.json();
                
                const msg = document.getElementById('message');
                if (response.ok) {
                    msg.textContent = '✅ ' + result.message;
                    msg.className = 'message success';
                    document.getElementById('requestForm').reset();
                } else {
                    msg.textContent = '❌ ' + result.detail;
                    msg.className = 'message error';
                }
            } catch (error) {
                const msg = document.getElementById('message');
                msg.textContent = '❌ 提交失败，请重试';
                msg.className = 'message error';
            }
        }
        
        let selectedFile = null;
        
        // 文件选择
        document.getElementById('fileInput').addEventListener('change', function(e) {
            if (this.files.length > 0) {
                handleFile(this.files[0]);
            }
        });
        
        // 拖拽上传
        const uploadArea = document.getElementById('uploadArea');
        
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', function() {
            this.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
            if (e.dataTransfer.files.length > 0) {
                handleFile(e.dataTransfer.files[0]);
            }
        });
        
        uploadArea.addEventListener('click', function() {
            document.getElementById('fileInput').click();
        });
        
        function handleFile(file) {
            if (file.type !== 'application/pdf' && !file.name.endsWith('.pdf')) {
                alert('请选择 PDF 文件');
                return;
            }
            
            selectedFile = file;
            document.getElementById('fileName').textContent = '📄 ' + file.name;
            document.getElementById('fileInfo').style.display = 'block';
            document.getElementById('convertBtn').disabled = false;
            document.getElementById('downloadLink').style.display = 'none';
            updateProgress(0);
            updateStatus('准备就绪，点击"开始转换"');
        }
        
        function updateProgress(percent) {
            document.getElementById('progressBar').style.width = percent + '%';
        }
        
        function updateStatus(text) {
            document.getElementById('status').textContent = text;
        }
        
        function updateConvertBtn() {
            const type = document.getElementById('convertType').value;
            const btn = document.getElementById('convertBtn');
            if (type === 'ppt') {
                btn.innerHTML = '📊 转换为 PPT';
            } else {
                btn.innerHTML = '📝 转换为 Word';
            }
        }
        
        function clearAll() {
            selectedFile = null;
            document.getElementById('fileInput').value = '';
            document.getElementById('fileInfo').style.display = 'none';
            document.getElementById('downloadLink').style.display = 'none';
            document.getElementById('convertBtn').disabled = true;
        }
        
        async function convertFile() {
            if (!selectedFile) return;
            
            const btn = document.getElementById('convertBtn');
            const convertType = document.getElementById('convertType').value;
            btn.disabled = true;
            updateStatus('正在上传文件...');
            
            try {
                const formData = new FormData();
                formData.append('file', selectedFile);
                formData.append('type', convertType);
                
                updateProgress(20);
                updateStatus('正在转换中，请稍候...');
                
                const response = await fetch('/convert/' + convertType, {
                    method: 'POST',
                    body: formData
                });
                
                updateProgress(80);
                
                if (!response.ok) {
                    throw new Error('转换失败');
                }
                
                const result = await response.json();
                
                updateProgress(100);
                updateStatus('转换完成！');
                
                document.getElementById('downloadBtn').href = '/download/' + result.filename;
                document.getElementById('downloadBtn').innerHTML = convertType === 'ppt' ? '📥 下载 PPT 文件' : '📥 下载 Word 文件';
                document.getElementById('downloadLink').style.display = 'block';
                
            } catch (error) {
                updateStatus('错误: ' + error.message);
                alert('转换失败: ' + error.message);
            } finally {
                btn.disabled = false;
            }
        }
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """返回主页面"""
    return HTML_TEMPLATE


@app.post("/convert")
async def convert_pdf(file: UploadFile = File(...)):
    """处理 PDF 转 Word 请求（默认转为 Word）"""
    return await convert_file(file, "word")


@app.post("/convert/ppt")
async def convert_pdf_to_ppt(file: UploadFile = File(...)):
    """处理 PDF 转 PPT 请求"""
    return await convert_file(file, "ppt")


@app.post("/convert/word")
async def convert_pdf_to_word(file: UploadFile = File(...)):
    """处理 PDF 转 Word 请求"""
    return await convert_file(file, "word")


async def convert_file(file: UploadFile = File(...), convert_type: str = "word"):
    """通用文件转换处理函数"""
    
    # 验证文件类型
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="只支持 PDF 文件")
    
    # 生成唯一文件名
    file_id = str(uuid.uuid4())
    input_filename = f"{file_id}_{file.filename}"
    
    if convert_type == "ppt":
        output_filename = f"{file_id}_{file.filename.replace('.pdf', '.pptx')}"
        output_media_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    else:
        output_filename = f"{file_id}_{file.filename.replace('.pdf', '.docx')}"
        output_media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    
    input_path = UPLOAD_DIR / input_filename
    output_path = OUTPUT_DIR / output_filename
    
    try:
        # 保存上传的文件
        async with aiofiles.open(input_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # 执行转换
        loop = asyncio.get_event_loop()
        
        if convert_type == "ppt":
            result = await loop.run_in_executor(
                None,
                lambda: pdf_to_ppt(str(input_path), str(output_path))
            )
        else:
            result = await loop.run_in_executor(
                None,
                lambda: pdf_to_word(str(input_path), str(output_path))
            )
        
        if result["success"]:
            return {
                "success": True,
                "filename": output_filename,
                "pages": result["pages"],
                "message": result["message"]
            }
        else:
            raise HTTPException(status_code=500, detail=result["message"])
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # 清理上传的临时文件
        if input_path.exists():
            input_path.unlink()


@app.get("/download/{filename}")
async def download_file(filename: str):
    """下载转换后的文件"""
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 根据文件扩展名确定媒体类型
    if filename.endswith('.pptx'):
        media_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    else:
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type=media_type
    )


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "message": "服务运行正常"}


@app.post("/api/request")
async def submit_request(request: FeatureRequest):
    """提交功能需求"""
    try:
        # 读取现有需求
        requests_data = []
        if REQUESTS_FILE.exists():
            with open(REQUESTS_FILE, 'r', encoding='utf-8') as f:
                requests_data = json.load(f)
        
        # 添加新需求
        new_request = {
            "id": str(uuid.uuid4())[:8],
            "title": request.title,
            "description": request.description,
            "contact": request.contact,
            "priority": request.priority,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        requests_data.append(new_request)
        
        # 保存到文件
        with open(REQUESTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(requests_data, f, ensure_ascii=False, indent=2)
        
        # 打印到控制台
        priority_text = {"high": "🔥 急需", "normal": "📋 一般需求", "low": "🕐 有空再做"}
        print("\n" + "="*50)
        print(f"📨 **新功能需求已提交**")
        print("="*50)
        print(f"标题: {request.title}")
        print(f"优先级: {priority_text.get(request.priority, '📋 一般需求')}")
        print(f"联系方式: {request.contact or '未填写'}")
        print(f"时间: {new_request['created_at']}")
        print(f"\n描述:\n{request.description}")
        print("="*50 + "\n")
        
        # 发送 Discord 通知给管理员
        try:
            from tools import message
            notify_msg = f"""📨 **新功能需求提交**

**标题:** {request.title}
**优先级:** {priority_text.get(request.priority, '📋 一般需求')}
**联系方式:** {request.contact or '未填写'}
**时间:** {new_request['created_at']}

**需求描述:**
{request.description}
"""
            message(action="send", message=notify_msg)
            print("✅ Discord 通知已发送\n")
        except Exception as msg_err:
            print(f"⚠️  Discord 通知发送失败: {msg_err}\n")
        
        return {"success": True, "message": "需求已提交！管理员已收到通知。"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提交失败: {str(e)}")


@app.get("/api/requests")
async def get_requests():
    """获取所有需求（管理员用）"""
    if not REQUESTS_FILE.exists():
        return {"requests": [], "total": 0}
    
    with open(REQUESTS_FILE, 'r', encoding='utf-8') as f:
        requests_data = json.load(f)
    
    # 按优先级和时间排序
    priority_order = {"high": 0, "normal": 1, "low": 2}
    requests_data.sort(key=lambda x: (priority_order.get(x["priority"], 1), x["created_at"]))
    
    return {"requests": requests_data, "total": len(requests_data)}


@app.post("/api/requests/{request_id}/implement")
async def implement_request(request_id: str, body: dict = None):
    """标记需求为已实现"""
    try:
        if not REQUESTS_FILE.exists():
            raise HTTPException(status_code=404, detail="需求不存在")
        
        with open(REQUESTS_FILE, 'r', encoding='utf-8') as f:
            requests_data = json.load(f)
        
        for req in requests_data:
            if req["id"] == request_id:
                req["status"] = "implemented"
                req["implemented_at"] = datetime.now().isoformat()
                if body and body.get("notes"):
                    req["notes"] = body["notes"]
                
                with open(REQUESTS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(requests_data, f, ensure_ascii=False, indent=2)
                
                return {"success": True, "message": "已标记为已实现"}
        
        raise HTTPException(status_code=404, detail="需求不存在")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_local_ip():
    """获取本机 IP 地址"""
    import socket
    try:
        # 连接到一个外部 IP，获取本机出口 IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def main():
    """启动服务"""
    host = "0.0.0.0"
    port = 8000
    
    # 获取本机 IP
    local_ip = get_local_ip()
    
    print("\n" + "=" * 60)
    print("  File Converter Started")
    print("=" * 60)
    print(f"\nLocal Access: http://localhost:{port}")
    print(f"LAN Access: http://{local_ip}:{port}")
    print("\nSupported: PDF -> Word (.docx)")
    print("\nPress Ctrl+C to stop\n")
    
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
