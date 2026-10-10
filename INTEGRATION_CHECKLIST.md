请在这里填入你们现有系统的关键信息，我们才能做出真正匹配的集成版本。

## 你需要提供的信息

### 1. Cloud API Client V2
请给出：
- 完整的 cloud_api_client.py 文件路径和实现
- 或者至少给出关键方法的签名和返回结构

示例：
```python
class CloudAPIClient:
    def fetch_conversations(self, cursor=None, limit=100):
        # 返回什么结构？
        return {"data": [...], "cursor": "...", "has_more": True}
```

### 2. Analysis Pipeline DFA 词库（6大类）
请给出：
- 文件位置
- 词库数据结构
- 6个分类分别是什么

示例：
```json
{
  "complaint": [...],
  "refund": [...],
  "abuse": [...],
  ...
}
```

### 3. Notifier 通知骨架
请给出：
- services/notifier.py 的完整代码
- 或者至少给出主要方法和通知渠道

### 4. LLM 语义质检实现
请给出：
- 调用 LLM 的代码
- API 地址和认证方式
- 返回的 JSON 结构

### 5. 真实接口文档
请给出：
- Cloud API 的完整接口定义
- 请求/响应的真实示例

### 6. .env 配置
请列出你们现成的所有 webhook 和 LLM 配置

---

提供完后，我会直接：
1. 替换掉我们的模拟实现
2. 接入真实的 DFA 词库（6大类）
3. 集成真实的通知系统
4. 用真实的 LLM 语义质检
5. 校准 cloud_api_client 的契约
