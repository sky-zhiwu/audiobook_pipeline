# 智能有声书生成引擎 (Audiobook Pipeline)

基于前沿端到端语音大模型 **VoxCPM2** 构建的全自动有声书生成平台。本项目采用 B/S 微服务架构设计，通过工程化的流水线调度，原生支持零样本音色克隆与自然语言音色设计。

## ✨ 核心特性 (Core Features)

- **🚀 自动化长文本管线 (Pipeline)：** 针对长篇小说自动进行智能正则断句 -> 碎片化并行推理 -> 无缝音频拼接混音。
- **🛡️ 防御机制：** 内置完整的 `try...finally` 垃圾回收机制与临时资产托管，确保异常崩溃时服务器磁盘不会被临时文件撑爆。
- **🎨 魔法音色设计 (Voice Design)：** 无需参考音频，直接通过自然语言提示词（如 `(年轻男性，低沉磁性)`）凭空创造音色，并支持长文本的全局状态自动注入。
- **🎛️ 零样本声音克隆 (Zero-shot Cloning)：** 支持前端上传 3-10 秒参考音频，实现高质量的目标音色克隆与情感复刻。
- **🔌 前后端解耦架构：** 基于 FastAPI 提供标准 RESTful API 与 Swagger 文档，前端采用 Streamlit 实现轻量级且现代化的可视化交互。

## 🛠️ 技术栈 (Tech Stack)

- **AI 基座：** [VoxCPM2](https://github.com/OpenBMB/VoxCPM) (2B 参数, Tokenizer-Free 架构)
- **后端服务：** FastAPI, Uvicorn, Pydantic, python-multipart
- **前端交互：** Streamlit, Requests
- **音频与数据处理：** pydub, soundfile, re (正则)
- **包与环境管理：** `uv` (极速 Rust 驱动管理器)

## ⚙️ 环境配置指南 (Setup Installation)

本项目对环境依赖有一定要求，请严格按照以下步骤配置：

### 1. 系统级依赖安装

音频拼接与底层处理强依赖于 `ffmpeg`，必须将其安装在操作系统中并配置环境变量。

- **Windows:** `winget install ffmpeg`
- **Mac:** `brew install ffmpeg`
- **Linux:** `sudo apt install ffmpeg`

### 2. Python 虚拟环境初始化

强烈推荐使用 `uv` 来管理依赖，大幅节省大模型的安装时间与磁盘空间。请在项目根目录下打开终端：

Bash

```
# 1. 创建并激活 Python 3.10+ 虚拟环境
uv venv --python 3.10
# Windows 激活命令: .venv\Scripts\activate
# Mac/Linux 激活命令: source .venv/bin/activate

# 2. 安装基础框架与处理库
uv add fastapi uvicorn pydantic streamlit pydub python-multipart soundfile

# 3. 安装 PyTorch (CUDA版本) 及 VoxCPM 模型包
uv add torch torchaudio
uv add voxcpm
```

## 🚀 启动项目 (How to Run)

本项目采用前后端分离架构，需要开启 **两个独立的终端窗口**（请确保两个终端均已激活 `.venv` 虚拟环境）。

### 终端 A：启动 FastAPI 后端核心

Bash

```
uvicorn main_api:app --reload
```

*启动后，初次运行会自动从 HuggingFace 下载模型权重到本地缓存。等待终端打印出 `✅ 真实大模型加载成功！` 后，服务即准备就绪。可以访问 `http://127.0.0.1:8000/docs` 查看 API 接口文档。*

### 终端 B：启动 Streamlit 前端页面

Bash

```
streamlit run main_ui.py
```

*启动后，浏览器会自动打开 `http://localhost:8501` 进入可视化操作页面。*

## 📖 交互使用说明 (Usage Guide)

### 场景一：常规文本转语音

直接在输入框中粘贴长篇小说（如《三体》节选），点击生成。系统会在后台自动切片合成并拼接，最终直接在网页端渲染出可播放下载的完整音频。

### 场景二：魔法音色设计

在要合成的长文本 **最开头**，使用英文或中文括号输入你期望的声音特征。系统会自动将该特征注入到长文本的每一个切片中，防止大模型出现“上下文音色遗忘”。

- 输入示例：

  ```
  (年轻男性，声音低沉磁性) 春江潮水连海平，海上明月共潮生。滟滟随波千万里，何处春江无月明！
  ```

### 场景三：零样本音色克隆

在界面的文件上传区，上传一段 **3 到 10 秒钟、无背景杂音的纯净人声 (.wav / .mp3)**。模型会提取该音频的声纹特征，并用该音色朗读你输入的文本内容。