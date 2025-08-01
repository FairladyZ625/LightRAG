# LightRAG Core 使用指南 2025

> 基于2025年最新官方文档整理，专为 ygagentlanggraph 需求管理AI微服务设计

## 📋 快速开始清单

### 1. 安装（选择其一）

```bash
# ✅ 推荐：PyPI安装（轻量级，嵌入式使用）
pip install -U lightrag-hku

# ✅ 带API服务器（如需要Web界面）
pip install -U "lightrag-hku[api]"

# 🔧 开发模式（仅当需要源码调试）
git clone https://github.com/HKUDS/LightRAG.git
cd LightRAG && pip install -e .
```

### 2. 最小可运行示例

```python
# lightrag_demo.py
import os
import asyncio
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.utils import EmbeddingFunc, setup_logger

# 配置日志
setup_logger("lightrag", "INFO")

# 确保API密钥
os.environ.setdefault("OPENAI_API_KEY", "sk-your-key-here")

WORKING_DIR = "./rag_storage"

async def main():
    # 初始化LightRAG（嵌入式模式）
    rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=openai_complete_if_cache,
        embedding_func=EmbeddingFunc(
            embedding_dim=1536,
            func=openai_embed
        ),
        # 轻量级存储配置
        vector_storage="NanoVectorDBStorage",
        graph_storage="NetworkXStorage",
        kv_storage="JsonKVStorage"
    )
    
    # 插入示例需求
    requirements = [
        "用户需要登录功能，支持手机号+验证码登录",
        "系统需要权限管理，区分管理员和普通用户",
        "需要支持订单管理，包括创建、查询、取消"
    ]
    
    await rag.ainsert(requirements)
    
    # 查询
    result = await rag.aquery(
        "系统支持哪些用户认证方式？",
        QueryParam(mode="hybrid")
    )
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

## 🎯 四种查询模式详解

| 模式 | 适用场景 | 特点 |
|------|----------|------|
| `local` | 实体级精准问答 | 聚焦具体实体，回答精确 |
| `global` | 关系级总结 | 全局视角，适合总结 |
| `hybrid` | 80%场景首选 | 实体+关系融合，平衡精确与全面 |
| `naive` | 基础向量检索 | 快速简单，无图结构 |

```python
# 示例用法
await rag.aquery("登录功能的具体要求是什么？", QueryParam(mode="local"))
await rag.aquery("总结系统的用户管理功能", QueryParam(mode="global"))
```

## 🔧 配置参数表

| 参数 | 说明 | 推荐值（需求管理场景） |
|---|---|---|
| `working_dir` | 存储目录 | `./rag_storage` |
| `chunk_token_size` | 分块大小 | `800-1200`（需求文档适中） |
| `chunk_overlap_token_size` | 重叠大小 | `50-100` |
| `max_async` | 并发数 | `2-4`（控制成本） |
| `llm_model_max_async` | LLM并发 | `2` |

## 📊 批量需求处理

```python
# 批量插入需求文档
requirements = [
    {"content": "用户需要忘记密码功能", "id": "req-001"},
    {"content": "管理员可以查看所有用户订单", "id": "req-002"},
    {"content": "系统需要发送邮件通知", "id": "req-003"}
]

await rag.ainsert(
    [r["content"] for r in requirements],
    ids=[r["id"] for r in requirements]
)
```

## 🔄 与MCP集成模式

```python
# 在ygagentlanggraph中的集成示例
from src.mcp_client import YGMCPClient
from lightrag import LightRAG

class RequirementAnalyzer:
    def __init__(self):
        self.rag = LightRAG(
            working_dir="./requirement_kg",
            vector_storage="NanoVectorDBStorage",
            graph_storage="NetworkXStorage"
        )
        self.mcp_client = YGMCPClient("http://localhost:8890")
    
    async def analyze_requirements(self):
        # 1. 从yg4AI获取需求
        requirements = await self.mcp_client.fetch_requirements()
        
        # 2. 构建知识图谱
        await self.rag.ainsert(requirements)
        
        # 3. 分析并返回结果
        analysis = await self.rag.aquery(
            "分析需求之间的依赖关系和潜在冲突",
            QueryParam(mode="hybrid")
        )
        return analysis
```

## 🚨 常见问题解决

### 安装问题
```bash
# 版本检查
python -c "import lightrag; print(lightrag.__version__)"

# 依赖冲突解决
pip install --force-reinstall lightrag-hku
```

### 存储配置
```python
# 内存模式（测试用）
rag = LightRAG(
    working_dir="/tmp/lightrag",
    vector_storage="NanoVectorDBStorage",
    graph_storage="NetworkXStorage"
)
```

### 性能调优
```python
# 轻量级配置
rag = LightRAG(
    working_dir="./lightrag_data",
    chunk_token_size=600,        # 小文档块
    embedding_batch_num=8,       # 适中批处理
    max_async=2,                 # 控制并发
    enable_llm_cache=True        # 启用缓存
)
```

## 🔍 验证安装

```bash
# 快速验证
python -c "
import asyncio, tempfile
from lightrag import LightRAG

async def test():
    rag = LightRAG(working_dir=tempfile.mkdtemp())
    await rag.ainsert('LightRAG安装测试')
    print('LightRAG Core安装成功！')

asyncio.run(test())
"
```

## 📚 下一步：集成到ygagentlanggraph

### 项目结构建议
```
src/
├── embedded_lightrag/
│   ├── __init__.py
│   ├── lightrag_manager.py      # LightRAG封装
│   └── config.py               # 配置管理
├── mcp_client/
│   └── yg_client.py            # MCP客户端
└── workflows/
    ├── requirement_analysis.py
    └── knowledge_graph.py
```

### 使用流程
1. 安装：`pip install -r requirements.txt`（包含lightrag-hku）
2. 配置：设置OPENAI_API_KEY环境变量
3. 运行：`python src/main.py --short_req "需求分析"`

---

**文档更新时间：2025-07-31**  
**适用版本：lightrag-hku ≥ 1.2.0**