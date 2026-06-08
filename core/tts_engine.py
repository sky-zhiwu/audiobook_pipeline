import os

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
# 让Hugging Face 以后把模型下载到 D 盘的指定目录
os.environ["HF_HOME"] = "D:\\AI_Models\\HuggingFace"

import os
import logging
from voxcpm import VoxCPM
import soundfile as sf

logger = logging.getLogger(__name__)


class TTSEngine:
    def __init__(self, use_mock: bool = False, device: str = "cuda"):
        """
        :param use_mock: 设为 False 即可开启真实的 AI 推理
        :param device: 显式指定使用 CUDA
        """
        self.use_mock = use_mock
        self.device = device
        self.model = None

        if not self.use_mock:
            # 首次运行时，这里会自动从 HuggingFace 下载几个 GB 的模型权重
            logger.info(f"🔥 正在加载 VoxCPM 模型到 {self.device} (首次启动需下载权重，请耐心等待)...")
            self._load_model()
        else:
            logger.warning("⚠️ 当前为 Mock 模式。")

    def _load_model(self):
        try:
            # 根据官方指南加载最新的 VoxCPM2 模型
            self.model = VoxCPM.from_pretrained(
                "openbmb/VoxCPM2",
                load_denoiser=True,  # 如果你不需要音色克隆高级增强，False 能省显存
                device=self.device
            )
            logger.info("✅ 真实大模型加载成功！")
        except Exception as e:
            logger.error(f"模型加载致命失败: {e}")
            raise

    # 增加 prompt_audio_path，并设置默认值为 None
    def generate_audio(self, text: str, output_path: str, prompt_audio_path: str = None) -> bool:
        logger.info(f"收到合成请求，文本长度: {len(text)} 字")

        if self.use_mock:
            with open(output_path, 'wb') as f:
                f.write(b"Mock file")
            return True

        try:
            logger.info("🧠 GPU 正在全速推理中...")

            # 构建基础的生成参数
            generate_kwargs = {
                "text": text,
                "cfg_value": 2.0,
                "inference_timesteps": 10,
            }

            # 修改：如果传入了参考音频，就把它加进大模型的提示词参数里
            if prompt_audio_path and os.path.exists(prompt_audio_path):
                logger.info(f"🎤 启用音色克隆，参考音频路径: {prompt_audio_path}")
                generate_kwargs["reference_wav_path"] = prompt_audio_path

            # 使用解包的方式传入参数
            wav = self.model.generate(**generate_kwargs)

            import soundfile as sf
            sf.write(output_path, wav, self.model.tts_model.sample_rate)

            logger.info(f"✅ 真实音频生成成功，已保存至: {output_path}")
            return True

        except Exception as e:
            logger.error(f"❌ 显存溢出或生成报错: {e}")
            return False

# 关键：将 use_mock 设为 False 即可激活真实模型！
tts_engine = TTSEngine(use_mock=False, device="cuda")