# FastAPI 启动入口
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from api.routes import router

# 1. 初始化 FastAPI 实例，这里填写的 title 会直接显示在接口文档里
app = FastAPI(
    title="Audiobook Pipeline API",
    description="基于 VoxCPM 的音频生成后端服务",
    version="1.0.0"
)

# 2. 挂载路由（把我们刚才写的 /generate 接口挂上来）
app.include_router(router, prefix="/api/v1")

# 3. 挂载静态文件目录
# 这样前端就可以通过 http://.../files/output_xxx.wav 直接播放音频了
app.mount("/files", StaticFiles(directory="data"), name="static_files")

# 4. 如果你想直接在 Python 里运行（方便 debug）
if __name__ == "__main__":
    uvicorn.run("main_api:app", host="127.0.0.1", port=8000, reload=True)