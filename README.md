# 📄 File Converter System

[![GitHub](https://img.shields.io/badge/GitHub-michaelxmchn%2Ffile-converter-blue)](https://github.com/michaelxmchn/file-converter)

局域网文件转换服务平台 - 支持功能需求提交和项目管理

## 🎯 功能特性

### 已完成
- ✅ **PDF 转 Word** - 支持 PDF 文件转换为 Word 文档
- ✅ **功能需求提交** - 用户可在网页提交转换功能需求
- ✅ **需求自动保存** - 需求自动保存到本地并显示
- ✅ **项目管理系统** - 里程碑跟踪和讨论记录

### 待开发
- 🔄 **批量文件转换** - 支持批量上传和转换
- 📋 **Excel 转 PDF** - Excel 文件转 PDF
- 📋 **图片格式转换** - PNG/JPG/GIF/WebP 互转

## 🚀 快速开始

### 环境要求
- Python 3.10+
- FastAPI
- uvicorn

### 安装依赖
```bash
pip install -r requirements.txt
```

### 启动服务
```bash
# Windows
start.bat

# 或直接运行
python main.py
```

### 访问地址
- 本机访问：`http://localhost:8000`
- 局域网访问：`http://<你的IP>:8000`

## 📁 项目结构

```
file-converter/
├── main.py              # 主程序入口
├── project_tool.py      # 项目管理命令行工具
├── projects_manager.py  # 项目管理核心模块
├── projects/            # 项目数据目录
│   └── *.json          # 项目文件
├── scripts/            # 转换脚本模块
│   └── pdf_handler.py  # PDF 转换处理器
├── requirements.txt    # Python 依赖
├── start.bat          # Windows 启动脚本
├── README.md          # 本文档
└── .gitignore        # Git 忽略规则
```

## 💻 命令行工具

### 查看所有项目
```bash
python project_tool.py list
```

### 查看项目详情
```bash
python project_tool.py view file-converter-system
```

### 添加里程碑
```bash
python project_tool.py add-milestone <项目名> <标题> [描述]
```

### 查看项目进度
```bash
python project_tool.py progress <项目名>
```

### 查看讨论记录
```bash
python project_tool.py view <项目名>  # 包含讨论记录
```

## 🔄 Git 备份与回滚

### 备份（推送到 GitHub）
```bash
git add .
git commit -m "描述你的更改"
git push origin main
```

### 一键回滚（Windows）
在 E 盘备份目录中双击 `rollback.bat`，会自动：
1. 拉取 GitHub 最新代码
2. 重置本地文件到最新提交
3. 安装依赖

### 一键回滚（命令行）
```bash
git fetch origin
git reset --hard origin/main
pip install -r requirements.txt
```

## 📋 里程碑

### 已完成
1. ✅ 文件转换核心功能 - PDF 转 Word
2. ✅ 需求提交页面 - 用户网页提交需求
3. ✅ 管理员接收需求 - 控制台显示需求

### 进行中
- 待添加

## 🤝 贡献

如有功能需求，请在网页的 **"💡 提交需求"** 标签中填写。

## 📄 许可证

MIT License

## 📞 联系

- 项目管理员：@michaelwaterbear
- 反馈渠道：网页需求提交系统
