import os
import time
from dotenv import load_dotenv
from volcenginesdkarkruntime import Ark

# 加载环境变量
load_dotenv()

# 初始化客户端
client = Ark(api_key=os.environ.get("ARK_API_KEY"))


def create_video_task():
    """创建视频生成任务"""
    print("正在创建视频生成任务...")
    try:
        resp = client.content_generation.tasks.create(
            model="ep-20260111161309-2gz8b",  # 用户提供的模型ID
            content=[
                {
                    "text": ("女孩抱着狐狸，女孩睁开眼，温柔地看向镜头，狐狸友善地抱着，镜头缓缓拉出，女孩的头发被风吹动  --ratio adaptive  --dur 5"),
                    "type": "text"
                },
                {
                    "image_url": {
                        "url": ("https://ark-project.tos-cn-beijing.volces.com/doc_image/i2v_foxrgirl.png")
                    },
                    "type": "image_url"
                }
            ]
        )
        print(f"任务创建成功，任务ID: {resp.id}")
        return resp.id
    except Exception as e:
        print(f"创建任务失败: {e}")
        return None


def get_task_status(task_id):
    """轮询获取任务状态"""
    print(f"正在查询任务状态，任务ID: {task_id}...")
    try:
        # 调整API调用方式，使用正确的参数名
        resp = client.content_generation.tasks.get(task_id=task_id)
        print(f"任务状态: {resp.status}")
        return resp
    except Exception as e:
        print(f"查询任务失败: {e}")
        return None


def main():
    """主函数"""
    # 创建视频生成任务
    task_id = create_video_task()
    if not task_id:
        return

    # 轮询任务状态
    max_retries = 60  # 最大重试次数
    retry_interval = 5  # 重试间隔（秒）

    for i in range(max_retries):
        task_resp = get_task_status(task_id)
        if not task_resp:
            time.sleep(retry_interval)
            continue

        if task_resp.status == "succeeded":
            print("\n任务执行成功！")
            print(f"视频URL: {task_resp.content.video_url}")
            break
        elif task_resp.status == "failed":
            print(f"\n任务执行失败: {task_resp.failed_reason}")
            break
        else:
            print(f"任务正在执行中，第 {i+1}/{max_retries} 次查询...")
            time.sleep(retry_interval)
    else:
        print("\n任务超时，已超过最大查询次数")


if __name__ == "__main__":
    main()
