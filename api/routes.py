# FastAPI 路由逻辑
import os
import time
from fastapi import APIRouter, HTTPException
from api.schemas import TTSRequest, TTSResponse

# 引入我们的三大服务
from core.tts_engine import tts_engine
from services.text_processor import text_processor
from services.audio_mixer import audio_mixer

router = APIRouter()
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)


@router.post("/generate", response_model=TTSResponse, summary="长文本智能生成语音", tags=["TTS Pipeline"])
async def generate_speech(request: TTSRequest):
    """
    完整的有声书生成流水线：断句 -> 循环生成 -> 拼接混音 -> 垃圾回收
    """
    timestamp = int(time.time())
    final_output_name = f"audiobook_{timestamp}.wav"
    final_output_path = os.path.join(DATA_DIR, final_output_name)

    temp_audio_paths = []  # 用于记录生成的临时碎片文件路径

    try:
        # 环节 1: 智能断句
        chunks = text_processor.split_text(request.text)
        if not chunks:
            raise ValueError("文本解析为空")

        # 环节 2: 循环调用引擎生成音频碎片
        for index, chunk in enumerate(chunks):
            temp_path = os.path.join(DATA_DIR, f"temp_{timestamp}_{index}.wav")
            # 调用底层大模型推理
            success = tts_engine.generate_audio(text=chunk, output_path=temp_path)

            if success:
                temp_audio_paths.append(temp_path)
            else:
                # 容错机制。如果某一句失败了，系统不该全盘崩溃，而是跳过该句记录日志。
                print(f"⚠️ 第 {index + 1} 句生成失败，已跳过。文本: {chunk}")

        # 环节 3: 拼接混音
        if not temp_audio_paths:
            raise RuntimeError("所有文本片段均生成失败，无法混音。")

        merge_success = audio_mixer.merge_audios(temp_audio_paths, final_output_path)
        if not merge_success:
            raise RuntimeError("音频拼接环节失败。")

        # 返回最终结果
        return TTSResponse(
            success=True,
            message=f"语音合成完毕！共处理了 {len(chunks)} 个句子。",
            audio_url=f"/files/{final_output_name}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # 环节 4: 垃圾回收
        # finally 块意味着无论上面代码是成功还是崩溃，这里的代码必定执行。
        # 把临时文件删掉，释放磁盘空间
        for path in temp_audio_paths:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except OSError as e:
                    print(f"⚠️ 临时文件删除失败: {path}, 错误: {e}")