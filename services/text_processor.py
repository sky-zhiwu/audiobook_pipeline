# 封装 NLTK 断句、正则清洗逻辑
import re
import logging

# import nltk
# NLTK 的 sent_tokenize 对于纯英文断句非常优秀，但对于中文处理并不原生支持。
# 在中文 TTS 场景下，使用正则表达式匹配中文标点，是工业界更稳健、更轻量的做法。

logger = logging.getLogger(__name__)


class TextProcessor:
    def __init__(self, max_chunk_length: int = 300):
        """
        文本处理服务类
        :param max_chunk_length: 每个文本块的最大字符数。必须小于 VoxCPM 的极限。
        """
        self.max_chunk_length = max_chunk_length

    def clean_text(self, text: str) -> str:
        """
        数据清洗（Data Cleaning）：
        去除网络文本中常见的不可见字符、多余的换行和空格。
        """
        if not text:
            return ""
        # 统一替换换行符，将连续多个空格/换行压缩为一个
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def split_text(self, text: str) -> list[str]:
        """
        核心逻辑：智能断句（Smart Sentence Splitting）
        保证切分后的每句话都不超过 max_chunk_length，且尽量不断在句子中间。
        """
        text = self.clean_text(text)
        if not text:
            return []

        # 1. 粗切分：利用正则“正向后视断言”，在【中文及英文的句号、问号、感叹号、换行符】后进行切割
        # (?<=...) 保证标点符号被保留在上一句的结尾，而不是被吃掉
        raw_sentences = re.split(r'(?<=[。！？!\?\n])', text)

        chunks = []
        current_chunk = ""

        # 2. 贪婪组装（Greedy Assembling）：将短句拼成长度合适的块
        for sentence in raw_sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # 【边界情况防御】：万一有一句话没有标点符号，且直接超过了最大长度？
            if len(sentence) > self.max_chunk_length:
                logger.warning(f"⚠️ 发现超长无标点单句，执行强制暴力截断：{sentence[:20]}...")
                # 暴力按定长切分，避免系统崩溃
                for i in range(0, len(sentence), self.max_chunk_length):
                    chunks.append(sentence[i:i + self.max_chunk_length])
                continue

            # 如果当前块拼接上新句子会“超载”
            if len(current_chunk) + len(sentence) > self.max_chunk_length:
                if current_chunk:
                    chunks.append(current_chunk)  # 把之前的块推入队列
                current_chunk = sentence  # 开启一个新的块
            else:
                # 没超载，继续拼接
                current_chunk += sentence

        # 3. 把循环结束时最后剩下的一点尾巴，推入队列
        if current_chunk:
            chunks.append(current_chunk)

        logger.info(f"文本预处理完成。原文长度: {len(text)}，被切分为 {len(chunks)} 个安全片段。")
        return chunks


# 实例化单例，供路由层调用
text_processor = TextProcessor(max_chunk_length=200)