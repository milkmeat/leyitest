# Prompt Record

- Date: 2026-03-31 00:00
- Branch: master
- Commit: feat: 提取 error_msg.yaml 错误码表 (doc_err_info + ETshpErrCode)

---

### 1. 提取 doc_err_info 到 YAML

把 docs/p10/document_english.json 文件中， doc_err_info 之下的error code和error message提取出来，保存在单独的 yaml
  文件中 docs/p10/error_msg.yaml

> **Insight**
> - 原始 JSON 中 `doc_err_info` 是以字符串数字为 key 的 dict（如 `"10001": {"info": "..."}`），转换到 YAML 时将 key 转为 int，使其更易于程序化读取
> - 共提取 **1369 条**错误码，范围从 `0` 到 `100048`（编号不连续），按数字升序排列
> - YAML 格式比 JSON 更简洁，`error_code: message` 的扁平结构方便直接用 `yaml.safe_load()` 读取为 Python dict

**Files:** `docs/p10/error_msg.yaml`

### 2. 补充 ETshpErrCode 枚举错误码

读取 docs/p10/service_key.h 下面的 enum ETshpErrCode，将其中的error
  code/message补充到error_msg.yaml中，为每个枚举变量生成简短明确的error message

> **Insight**
> 1. **两个数据源互补**：`doc_err_info`（1369条）是客户端显示文本，`ETshpErrCode`（838条）是服务端枚举。两者有大量重叠（606条共有），最终合并为 **1601 条唯一**错误码
> 2. **`[SVC]` 前缀标识来源**：从 `service_key.h` 补充的 232 条用 `[SVC]` 前缀标注，便于区分——这些是服务端内部错误，在 `doc_err_info` 中没有对应的客户端友好文本
> 3. **错误码段落分区**：枚举按模块分段（10000+ 客户端、20000+ 服务端业务、30000+ 服务器内部、32000-37000+ 各子模块、50000-60000 需重载），理解这个分区有助于快速定位错误类别

**Files:** `docs/p10/error_msg.yaml`
