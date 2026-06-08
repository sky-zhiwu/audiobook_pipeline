# FastAPI 路由逻辑
import os
import re
import traceback
import time
from api.schemas import TTSResponse
# File, Form, UploadFile 用于处理文件上传
from fastapi import APIRouter, HTTPException, File, Form, UploadFile
# 引入我们的三大服务
from core.tts_engine import tts_engine
from services.text_processor import text_processor
from services.audio_mixer import audio_mixer

router = APIRouter()
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# 去掉了 request: TTSRequest，改为直接接收 Form 和 File

@router.post("/generate", response_model=TTSResponse, summary="长文本智能生成语音 (支持音色克隆)")
async def generate_speech(
            text: str = Form(..., description="需要合成的长文本"),
            prompt_audio: UploadFile = File(None, description="可选：参考音色的音频文件 (3-10秒)")):
    '''
    完整的有声书生成流水线：断句 -> 循环生成 -> 拼接混音 -> 垃圾回收
    '''
    timestamp = int(time.time())
    final_output_name = f"audiobook_{timestamp}.wav"
    final_output_path = os.path.join(DATA_DIR, final_output_name)

    temp_audio_paths = []
    prompt_path = None  # 用于记录保存到本地的参考音频路径

    try:
        # 环节 0: 处理用户上传的提示音频
        if prompt_audio:
            # 把前端传来的内存文件写入硬盘临时目录
            prompt_path = os.path.join(DATA_DIR, f"prompt_{timestamp}_{prompt_audio.filename}")
            with open(prompt_path, "wb") as buffer:
                buffer.write(await prompt_audio.read())

        # 提取魔法音色提示词 (兼容中文全角和英文半角括号)
        voice_prompt = ""
        # 匹配文本开头形如 "(...)" 或 "（...）" 的内容
        # match = re.match(r'^[\(（](.*?)[\)）]', text)
        match = re.match(r'^[(（](.*?)[)）]', text)
        if match:
            voice_prompt = match.group(0)  # 获取完整的括号及内容，如 "(年轻男性，声音低沉)"
            # 将魔法提示词从原文中剥离，留下纯净正文给 text_processor 去切分
            text = text[len(voice_prompt):].strip()

        # 环节 1: 智能断句
        chunks = text_processor.split_text(text)
        if not chunks:
            raise ValueError("文本解析为空")

        # 环节 2: 循环调用引擎生成音频碎片
        for index, chunk in enumerate(chunks):
            temp_path = os.path.join(DATA_DIR, f"temp_{timestamp}_{index}.wav")
            chunk = voice_prompt + chunk
            print(f"🎤 正在生成第 {index + 1} 句，实际输入大模型的文本: {chunk}")

            # 把 prompt_path 传给大模型
            success = tts_engine.generate_audio(
                text=chunk,
                output_path=temp_path,
                prompt_audio_path=prompt_path
            )

            if success:
                temp_audio_paths.append(temp_path)
            else:
                print(f"⚠️ 第 {index + 1} 句生成失败，已跳过。文本: {chunk}")

        # 环节 3: 拼接混音
        if not temp_audio_paths:
            raise RuntimeError("所有文本片段均生成失败，无法混音。")

        merge_success = audio_mixer.merge_audios(temp_audio_paths, final_output_path)
        if not merge_success:
            raise RuntimeError("音频拼接环节失败。")

        return TTSResponse(
            success=True,
            message=f"语音合成完毕！共处理了 {len(chunks)} 个句子。",
            audio_url=f"/files/{final_output_name}"
        )

    except Exception as e:
        traceback.print_exc()  # 这行代码会在终端打印出到底哪一行代码崩了
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # 环节 4: 垃圾回收 (清理碎片文件和提示音频)
        for path in temp_audio_paths:
            if os.path.exists(path):
                os.remove(path)

        # 把用户上传的提示音频也删掉，避免占空间
        if prompt_path and os.path.exists(prompt_path):
            os.remove(prompt_path)
