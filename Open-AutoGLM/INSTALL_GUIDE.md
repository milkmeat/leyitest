# Open-AutoGLM 安装指南

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/xxx/Open-AutoGLM.git
cd Open-AutoGLM
```

### 2. 创建虚拟环境

**Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows:**
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 安装 ADB 工具

**macOS:**
```bash
brew install android-platform-tools
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install adb
```

**Windows:**
1. 下载 [platform-tools](https://developer.android.com/tools/releases/platform-tools)
2. 解压并添加到 PATH

### 4. 连接设备

连接 Android 模拟器（如 BlueStacks、MuMu）或真机：

```bash
adb connect localhost:5555   # 模拟器
adb devices                  # 验证连接
```

### 5. 获取 API Key

1. 访问 [智谱 BigModel](https://bigmodel.cn) 注册账号
2. 在控制台获取 API Key
3. 设置环境变量：

```bash
export AUTOGLM_API_KEY="your-api-key"
```

---

## Claude Code 集成

### 配置 MCP Server

运行配置脚本自动生成 `.mcp.json`：

```bash
python setup_mcp.py
```

脚本会自动检测虚拟环境并生成正确的配置。

然后重启 Claude Code，使用命令：

```
/phone 打开微信给张三发消息
```

---

## 独立使用

无需 Claude Code，直接运行：

**单次任务：**
```bash
python main.py --apikey "$AUTOGLM_API_KEY" "打开设置"
```

**交互模式：**
```bash
python main.py --apikey "$AUTOGLM_API_KEY"
```

---

## 故障排除

### ADB 连接失败

1. 确保模拟器已启动并开启 ADB 调试
2. 尝试不同端口：
   ```bash
   adb connect localhost:5555
   adb connect localhost:5037
   adb connect 127.0.0.1:5555
   ```

### MCP Server 无法启动

1. 确保虚拟环境已激活
2. 安装 MCP 依赖：`pip install mcp`
3. 测试导入：`python -c "from phone_mcp_server import server"`

### Windows 中文乱码

```powershell
set PYTHONIOENCODING=utf-8
chcp 65001
```

---

## 环境变量

| 变量 | 说明 | 默认值 |
|-----|------|--------|
| `AUTOGLM_API_KEY` | 智谱 API Key | - |
| `PHONE_DEVICE_ID` | 设备 ID | emulator-5554 |
| `AUTOGLM_BASE_URL` | API 地址 | https://open.bigmodel.cn/api/paas/v4 |
| `AUTOGLM_MODEL` | 模型名称 | autoglm-phone |
