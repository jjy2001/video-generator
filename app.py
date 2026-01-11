# 修改 app.py，去掉本地文件存储
import os
import time
import base64  # 添加base64导入
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from volcenginesdkarkruntime import Ark

# 加载环境变量
load_dotenv()

# 初始化方舟客户端
client = Ark(api_key=os.environ.get("ARK_API_KEY"))

# 创建Flask应用
app = Flask(__name__)

# 配置上传文件大小限制
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# 允许的上传文件类型
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """首页路由"""
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate_video():
    """生成视频"""
    try:
        # 获取表单数据
        prompt = request.form.get('prompt')
        
        # 检查是否有文件上传
        if 'image' not in request.files:
            return jsonify({'error': '请上传一张图片'}), 400
        
        file = request.files['image']
        
        # 检查文件是否为空
        if file.filename == '':
            return jsonify({'error': '请选择一张图片上传'}), 400
        
        # 检查文件类型
        if not allowed_file(file.filename):
            return jsonify({'error': '只允许上传PNG、JPG、JPEG、GIF格式的图片'}), 400
        
        # 直接读取文件，不保存到本地
        image_data = file.read()
        base64_image = base64.b64encode(image_data).decode("utf-8")
        
        # 调用视频生成API
        resp = client.content_generation.tasks.create(
            model="ep-20260111161309-2gz8b",  # 用户提供的模型ID
            content=[
                {
                    "text": prompt + " --ratio adaptive --dur 5",
                    "type": "text"
                },
                {
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    },
                    "type": "image_url"
                }
            ]
        )
        
        return jsonify({'task_id': resp.id, 'status': 'success'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/status/<task_id>')
def get_status(task_id):
    """获取任务状态"""
    try:
        resp = client.content_generation.tasks.get(task_id=task_id)
        
        result = {
            'task_id': task_id,
            'status': resp.status
        }
        
        if resp.status == 'succeeded':
            result['video_url'] = resp.content.video_url
        elif resp.status == 'failed':
            result['failed_reason'] = resp.failed_reason
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)