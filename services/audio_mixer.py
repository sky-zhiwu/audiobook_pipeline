# 封装 pydub 音频拼接逻辑
import os
import logging
from pydub import AudioSegment

logger = logging.getLogger(__name__)

class AudioMixer:
    def __init__(self, silence_duration_ms: int = 400):
        """
        音频混音服务
        :param silence_duration_ms: 句子与句子之间的静音间隔（毫秒），默认 400ms，让听感更自然。
        """
        self.silence_duration_ms = silence_duration_ms

    def merge_audios(self, input_paths: list[str], output_path: str) -> bool:
        """
        将多个音频片段无缝拼接成一个完整的音频文件。
        """
        if not input_paths:
            logger.error("没有提供任何输入音频路径，合并取消。")
            return False

        try:
            logger.info(f"开始拼接 {len(input_paths)} 个音频片段...")
            # 初始化一个空的音频段
            final_audio = AudioSegment.empty()
            # 生成一段纯静音，作为句与句之间的间隔
            silence = AudioSegment.silent(duration=self.silence_duration_ms)

            for path in input_paths:
                if os.path.exists(path):
                    # 加载临时音频文件
                    segment = AudioSegment.from_file(path)
                    # 拼接到主音频上，并加上静音间隔
                    final_audio += segment + silence
                else:
                    logger.warning(f"⚠️ 找不到临时音频文件，已跳过: {path}")

            # 导出最终的完整音频文件
            final_audio.export(output_path, format="wav")
            logger.info(f"✅ 完整音频合并成功，已导出至: {output_path}")
            return True

        except Exception as e:
            logger.error(f"❌ 音频合并过程中发生异常: {e}")
            return False

# 实例化单例
audio_mixer = AudioMixer()