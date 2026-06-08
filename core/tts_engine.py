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
                load_denoiser=False,  # 如果你不需要音色克隆高级增强，False 能省显存
                device=self.device
            )
            logger.info("✅ 真实大模型加载成功！")
        except Exception as e:
            logger.error(f"模型加载致命失败: {e}")
            raise

    def generate_audio(self, text: str, output_path: str) -> bool:
        logger.info(f"收到合成请求，文本长度: {len(text)} 字")

        if self.use_mock:
            with open(output_path, 'wb') as f:
                f.write(b"Mock file")
            return True

        try:
            logger.info("🧠 GPU 正在全速推理中...")

            # 【核心：官方标准推理 API】
            # wav 是一个 numpy 数组，包含了连续的音频波形数据
            wav = self.model.generate(
                text=text,
                cfg_value=2.0,  # 分类器引导强度，控制发音清晰度
                inference_timesteps=10,  # 扩散模型的采样步数 (步数越低速度越快，默认 10)
            )

            # 使用 soundfile 将波形数组保存为真实的 .wav 文件
            sf.write(output_path, wav, self.model.tts_model.sample_rate)

            logger.info(f"✅ 真实音频生成成功，已保存至: {output_path}")
            return True

        except Exception as e:
            logger.error(f"❌ 显存溢出或生成报错: {e}")
            return False


# 关键：将 use_mock 设为 False 即可激活真实模型！
tts_engine = TTSEngine(use_mock=False, device="cuda")