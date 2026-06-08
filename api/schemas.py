# Pydantic 模型 (定义输入输出的数据格式)
from pydantic import BaseModel, Field

# 严格定义输入参数，并附带默认值和校验规则
class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=500, description="需要合成的文本内容（目前限制单次最多500字）")
    # 如果后续 VoxCPM 支持传 prompt 音频来克隆音色，可以加在这里，目前我们留空或加个假参数
    voice_preset: str = Field("default", description="音色预设（备用字段）")

# 定义 API 返回的格式
class TTSResponse(BaseModel):
    success: bool = Field(..., description="是否生成成功")
    message: str = Field(..., description="状态信息或错误提示")
    audio_url: str | None = Field(None, description="生成的音频下载或访问路径")