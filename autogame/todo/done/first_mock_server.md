## 目标
完成简单的mock server ，可以用现有的客户端连接并发送查询请求

## 任务
- 完成最小化的mock server，启动后监听localhost本地http端口
- mock server的协议与行为完全模仿 test服务器
- mock server利用本地配置文件来管理测试用的uid数据。例如，可以初始化 20001946 的坐标为 123,234
- main.py 支持 --mock 参数，会按默认端口连接localhost上的mock服务器。不提供时，默认连接test服务器


## 要求
- 如有不明确的项目，一开始就向我询问，并更新本文件
- 都明确后，先分解成适当的工作项，更新本文件。开始开发调试
- 每个工作项进度完成后，更新本文件
- 反复开发调试直到验收通过


## 工作项分解

- [x] 创建 `mock_server/mock_data.yaml` — 定义初始 uid 数据（20001946 坐标 123,234）
- [x] 实现 `mock_server/app.py` — FastAPI 应用，兼容 GET 协议，处理 login_get 命令
- [x] 更新 `config/env_config.yaml` — 添加 mock 环境配置（localhost:18888）
- [x] 更新 `src/main.py` — 支持 `--mock` 参数，传递 env 给 GameClient
- [x] 更新 `src/client.py` — `get_player_pos()` 接受 env 参数
- [x] 端到端验收测试通过


## 验收标准

```
# 启动mock server
cd mock_server
python app.py
```

```
# 运行测试客户端
python src/main.py --mock get_player_pos 20001946
(123,234)
```

```
# 原有test server仍然能够跑通
python src/main.py get_player_pos 20001946
(170,178)
```

## 验收结果: ✅ 全部通过
