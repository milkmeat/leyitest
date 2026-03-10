
## 目标
完成可用的客户端，可以连接到测试服务器后台查询uid信息

## 任务
leyitest/python_auto_ui/ 是一个历史遗留项目供参考
参考 ../python_auto_ui/get_uid_pos.py 完成本项目下客户端代码的开发
不要修改python_auto_ui项目，只在autogame项目下做开发

## 要求
- 可以连接 python_auto_ui 中的测试环境（服务器ip、端口），要使用配置文件管理，不要硬编码
- 使用最精简的代码，简洁易扩展
- 提供一个命令行工具： python src/main.py get_player_pos <uid>
  - 能打印出 (x,y) 形式的坐标，看一下参考代码就知道 city_pos 是怎么组装的
- 先分解成适当的工作项，更新本文件
- 每个工作项进度完成后，更新本文件
- 反复开发调试直到验收通过



## 工作项

- [x] 1. 创建 `config/env_config.yaml` — 测试服务器 URL + 默认请求头
- [x] 2. 实现 `src/client.py` — 连接真实测试服务器的同步 HTTP 客户端（GET + URL JSON 协议）
- [x] 3. 改造 `src/main.py` — 支持 `python src/main.py get_player_pos <uid>` CLI 命令
- [x] 4. 联调测试验收 — 运行命令验证输出

## 验收标准

> python src/main.py get_player_pos 20001946
> (170,178)