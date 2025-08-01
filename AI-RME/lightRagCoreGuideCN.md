# LightRAG 核心组件集成指南

本指南将详细说明如何将 LightRAG 的核心检索功能直接集成到您自己的软件项目中（如 LangGraph 应用程序），无需部署独立的 Docker 服务。

## 目录

1. [LightRAG 核心架构概述](#1-lightrag-核心架构概述)
2. [核心组件详解](#2-核心组件详解)
3. [依赖项安装](#3-依赖项安装)
4. [基础集成步骤](#4-基础集成步骤)
5. [完整代码示例](#5-完整代码示例)
6. [存储后端配置](#6-存储后端配置)
7. [LLM 和嵌入模型集成](#7-llm-和嵌入模型集成)
8. [高级配置选项](#8-高级配置选项)
9. [常见集成模式](#9-常见集成模式)
10. [错误处理和最佳实践](#10-错误处理和最佳实践)
11. [性能优化建议](#11-性能优化建议)
12. [故障排除](#12-故障排除)

## 1. LightRAG 核心架构概述

### 1.1 核心设计理念

LightRAG 采用模块化设计，核心组件包括：

- **LightRAG 主引擎** (`lightrag/lightrag.py`)：RAG 编排引擎
- **存储层** (`lightrag/kg/`)：支持多种存储后端
- **LLM 集成层** (`lightrag/llm/`)：支持多种大语言模型
- **查询处理层** (`lightrag/operate.py`)：实体提取和知识图谱构建
- **基础抽象层** (`lightrag/base.py`)：定义接口和数据结构

### 1.2 数据流架构

```
文档输入 → 文本分块 → 实体提取 → 知识图谱构建 → 向量化存储 → 查询检索 → 响应生成
```

## 2. 核心组件详解

### 2.1 主要文件和模块

| 文件/目录 | 功能描述 | 是否必需 |
|-----------|----------|----------|
| `lightrag/lightrag.py` | 主 RAG 引擎，核心业务逻辑 | 必需 |
| `lightrag/base.py` | 基础抽象类和数据结构 | 必需 |
| `lightrag/operate.py` | 查询处理和实体提取操作 | 必需 |
| `lightrag/utils.py` | 工具函数和辅助功能 | 必需 |
| `lightrag/constants.py` | 常量定义 | 必需 |
| `lightrag/types.py` | 类型定义 | 必需 |
| `lightrag/prompt.py` | 提示词模板 | 必需 |
| `lightrag/kg/` | 存储后端实现 | 必需 |
| `lightrag/llm/` | LLM 集成模块 | 必需 |

### 2.2 存储组件

LightRAG 使用四种存储类型：

- **KV_STORAGE**：键值存储，用于 LLM 响应缓存、文本块、文档信息
- **VECTOR_STORAGE**：向量存储，用于实体向量、关系向量、块向量
- **GRAPH_STORAGE**：图存储，用于实体关系图
- **DOC_STATUS_STORAGE**：文档状态存储，用于跟踪文档处理状态

## 3. 依赖项安装

### 3.1 核心依赖项

```bash
# 安装核心 LightRAG 包
pip install lightrag-hku

# 或从源码安装
pip install -e .
```

### 3.2 核心依赖详解

根据 `pyproject.toml` 分析，核心依赖项包括：

```python
# 必需的核心依赖
dependencies = [
    "aiohttp",           # 异步 HTTP 客户端
    "configparser",      # 配置文件解析
    "python-dotenv",     # 环境变量管理
    "nano-vectordb",     # 默认向量数据库
    "networkx",          # 默认图存储
    "numpy",             # 数值计算
    "pandas>=2.0.0",     # 数据处理
    "pydantic",          # 数据验证
    "tenacity",          # 重试机制
    "tiktoken",          # 分词器
    "xlsxwriter>=3.1.0", # Excel 导出
]
```

### 3.3 可选依赖项

```bash
# 如果需要使用特定的存储后端
pip install psycopg2-binary  # PostgreSQL
pip install redis           # Redis
pip install pymongo         # MongoDB
pip install neo4j           # Neo4j
pip install qdrant-client   # Qdrant
pip install pymilvus        # Milvus

# 如果需要使用特定的 LLM 提供商
pip install openai          # OpenAI
pip install anthropic       # Anthropic
pip install google-generativeai  # Google Gemini
```

## 4. 基础集成步骤

### 4.1 第一步：导入核心模块

```python
import os
import asyncio
from lightrag import LightRAG, QueryParam
from lightrag.kg.shared_storage import initialize_pipeline_status
```

### 4.2 第二步：配置 LLM 和嵌入函数

```python
# 使用 OpenAI 作为示例
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed

# 确保设置了 API 密钥
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
```

### 4.3 第三步：初始化 LightRAG 实例

```python
async def create_rag_instance():
    """创建并初始化 LightRAG 实例"""
    
    # 创建工作目录
    working_dir = "./rag_storage"
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)
    
    # 初始化 LightRAG
    rag = LightRAG(
        working_dir=working_dir,
        embedding_func=openai_embed,
        llm_model_func=gpt_4o_mini_complete,
        # 可选配置
        chunk_token_size=1200,
        top_k=60,
        max_total_tokens=32000,
    )
    
    # 关键步骤：初始化存储
    await rag.initialize_storages()
    await initialize_pipeline_status()
    
    return rag
```

### 4.4 第四步：文档索引和查询

```python
async def use_rag_example():
    """使用 RAG 进行文档索引和查询的示例"""
    
    rag = await create_rag_instance()
    
    try:
        # 插入文档
        document_text = "您的文档内容..."
        await rag.ainsert(document_text)
        
        # 执行查询
        query = "您的问题"
        result = await rag.aquery(
            query, 
            param=QueryParam(mode="hybrid")
        )
        
        print(f"查询结果: {result}")
        
    finally:
        # 清理资源
        await rag.finalize_storages()
```

## 5. 完整代码示例

### 5.1 基础集成示例

```python
import os
import asyncio
import logging
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed
from lightrag.kg.shared_storage import initialize_pipeline_status

class LightRAGIntegration:
    """LightRAG 集成封装类"""
    
    def __init__(self, working_dir: str = "./rag_storage"):
        self.working_dir = working_dir
        self.rag = None
        self._initialized = False
    
    async def initialize(self):
        """异步初始化 LightRAG"""
        if self._initialized:
            return
        
        # 检查必需的环境变量
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("请设置 OPENAI_API_KEY 环境变量")
        
        # 创建工作目录
        os.makedirs(self.working_dir, exist_ok=True)
        
        # 初始化 LightRAG
        self.rag = LightRAG(
            working_dir=self.working_dir,
            embedding_func=openai_embed,
            llm_model_func=gpt_4o_mini_complete,
            chunk_token_size=1200,
            top_k=60,
            max_total_tokens=32000,
            llm_model_max_async=4,
            embedding_batch_num=10,
        )
        
        # 初始化存储系统
        await self.rag.initialize_storages()
        await initialize_pipeline_status()
        
        self._initialized = True
        logging.info("LightRAG 初始化完成")
    
    async def add_document(self, content: str, metadata: dict = None) -> str:
        """添加文档到知识库"""
        if not self._initialized:
            await self.initialize()
        
        try:
            # 插入文档内容
            await self.rag.ainsert(content)
            logging.info(f"文档添加成功，内容长度: {len(content)}")
            return "success"
        except Exception as e:
            logging.error(f"文档添加失败: {str(e)}")
            raise
    
    async def query(self, question: str, mode: str = "hybrid") -> str:
        """查询知识库"""
        if not self._initialized:
            await self.initialize()
        
        try:
            result = await self.rag.aquery(
                question,
                param=QueryParam(mode=mode)
            )
            logging.info(f"查询完成，问题: {question[:50]}...")
            return result
        except Exception as e:
            logging.error(f"查询失败: {str(e)}")
            raise
    
    async def query_stream(self, question: str, mode: str = "hybrid"):
        """流式查询知识库"""
        if not self._initialized:
            await self.initialize()
        
        try:
            async for chunk in self.rag.aquery_stream(
                question,
                param=QueryParam(mode=mode)
            ):
                yield chunk
        except Exception as e:
            logging.error(f"流式查询失败: {str(e)}")
            raise
    
    async def cleanup(self):
        """清理资源"""
        if self.rag and self._initialized:
            await self.rag.finalize_storages()
            logging.info("LightRAG 资源清理完成")

# 使用示例
async def main():
    """主函数示例"""
    
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    # 创建 RAG 集成实例
    rag_integration = LightRAGIntegration()
    
    try:
        await rag_integration.initialize()
        
        # 添加文档
        document = """
        LightRAG 是一个简单快速的检索增强生成框架。
        它支持多种存储后端和 LLM 提供商。
        核心特性包括知识图谱构建、向量检索和混合查询模式。
        """
        
        await rag_integration.add_document(document)
        
        # 执行查询
        questions = [
            "LightRAG 的核心特性是什么？",
            "它支持哪些查询模式？",
        ]
        
        for question in questions:
            print(f"\n问题: {question}")
            answer = await rag_integration.query(question)
            print(f"回答: {answer}")
        
        # 流式查询示例
        print(f"\n流式查询示例:")
        async for chunk in rag_integration.query_stream("LightRAG 如何工作？"):
            print(chunk, end="", flush=True)
        
    except Exception as e:
        print(f"错误: {e}")
    finally:
        await rag_integration.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

### 5.2 与 LangGraph 集成示例

```python
import asyncio
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed
from lightrag.kg.shared_storage import initialize_pipeline_status

class GraphState(TypedDict):
    """LangGraph 状态定义"""
    question: str
    context: str
    answer: str
    rag_results: List[str]

class LangGraphRAGIntegration:
    """LangGraph 与 LightRAG 集成"""
    
    def __init__(self):
        self.rag = None
        self.graph = None
    
    async def initialize_rag(self):
        """初始化 LightRAG"""
        self.rag = LightRAG(
            working_dir="./langgraph_rag",
            embedding_func=openai_embed,
            llm_model_func=gpt_4o_mini_complete,
        )
        await self.rag.initialize_storages()
        await initialize_pipeline_status()
    
    async def retrieve_context(self, state: GraphState) -> GraphState:
        """检索上下文步骤"""
        question = state["question"]
        
        # 使用多种查询模式获取更全面的结果
        modes = ["local", "global", "naive"]
        rag_results = []
        
        for mode in modes:
            try:
                result = await self.rag.aquery(
                    question,
                    param=QueryParam(mode=mode)
                )
                rag_results.append(f"[{mode.upper()}] {result}")
            except Exception as e:
                print(f"查询模式 {mode} 失败: {e}")
        
        # 合并上下文
        context = "\n\n".join(rag_results)
        
        return {
            **state,
            "context": context,
            "rag_results": rag_results
        }
    
    async def generate_answer(self, state: GraphState) -> GraphState:
        """生成最终答案步骤"""
        question = state["question"]
        context = state["context"]
        
        # 使用混合模式生成最终答案
        final_answer = await self.rag.aquery(
            f"基于以下上下文回答问题：\n上下文：{context}\n问题：{question}",
            param=QueryParam(mode="hybrid")
        )
        
        return {
            **state,
            "answer": final_answer
        }
    
    def build_graph(self):
        """构建 LangGraph 工作流"""
        workflow = StateGraph(GraphState)
        
        # 添加节点
        workflow.add_node("retrieve", self.retrieve_context)
        workflow.add_node("generate", self.generate_answer)
        
        # 添加边
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)
        
        self.graph = workflow.compile()
    
    async def process_question(self, question: str) -> dict:
        """处理问题的完整流程"""
        if not self.rag:
            await self.initialize_rag()
        
        if not self.graph:
            self.build_graph()
        
        # 执行图工作流
        result = await self.graph.ainvoke({
            "question": question,
            "context": "",
            "answer": "",
            "rag_results": []
        })
        
        return result

# 使用示例
async def main():
    integration = LangGraphRAGIntegration()
    
    # 首先添加一些文档
    await integration.initialize_rag()
    
    documents = [
        "Python 是一种高级编程语言，具有简洁的语法和强大的功能。",
        "机器学习是人工智能的一个分支，通过算法让计算机从数据中学习。",
        "深度学习使用神经网络来解决复杂的模式识别问题。"
    ]
    
    for doc in documents:
        await integration.rag.ainsert(doc)
    
    # 处理问题
    question = "Python 在机器学习中有什么作用？"
    result = await integration.process_question(question)
    
    print(f"问题: {result['question']}")
    print(f"答案: {result['answer']}")
    print(f"检索结果数量: {len(result['rag_results'])}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 6. 存储后端配置

### 6.1 默认存储配置（推荐用于开发）

```python
# 使用默认的本地文件存储
rag = LightRAG(
    working_dir="./rag_storage",
    kv_storage="JsonKVStorage",           # JSON 文件存储
    vector_storage="NanoVectorDBStorage", # NanoVector 向量数据库
    graph_storage="NetworkXStorage",      # NetworkX 图存储
    doc_status_storage="JsonDocStatusStorage",  # JSON 状态存储
)
```

### 6.2 PostgreSQL 统一存储配置（推荐用于生产）

```python
import os

# 设置 PostgreSQL 连接
os.environ["POSTGRES_URL"] = "postgresql://username:password@localhost:5432/lightrag_db"

rag = LightRAG(
    working_dir="./rag_storage",
    kv_storage="PGKVStorage",
    vector_storage="PGVectorStorage", 
    graph_storage="PGGraphStorage",
    doc_status_storage="PGDocStatusStorage",
)
```

### 6.3 专业化存储配置（推荐用于大规模部署）

```python
# 使用专业的向量数据库和图数据库
rag = LightRAG(
    working_dir="./rag_storage",
    kv_storage="RedisKVStorage",        # Redis 键值存储
    vector_storage="QdrantVectorDBStorage",  # Qdrant 向量存储
    graph_storage="Neo4JStorage",       # Neo4j 图存储
    doc_status_storage="MongoDocStatusStorage",  # MongoDB 状态存储
)

# 相应的环境变量配置
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["QDRANT_URL"] = "http://localhost:6333"
os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["NEO4J_USERNAME"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "password"
os.environ["MONGODB_URL"] = "mongodb://localhost:27017/lightrag"
```

## 7. LLM 和嵌入模型集成

### 7.1 OpenAI 集成

```python
from lightrag.llm.openai import gpt_4o_complete, gpt_4o_mini_complete, openai_embed

# 设置 API 密钥
os.environ["OPENAI_API_KEY"] = "your-api-key"

rag = LightRAG(
    working_dir="./rag_storage",
    embedding_func=openai_embed,
    llm_model_func=gpt_4o_mini_complete,  # 或 gpt_4o_complete
    llm_model_name="gpt-4o-mini",
)
```

### 7.2 Ollama 本地模型集成

```python
from lightrag.llm.ollama import ollama_embed, ollama_model_complete

# 配置 Ollama 服务器
os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"

rag = LightRAG(
    working_dir="./rag_storage",
    embedding_func=ollama_embed,
    llm_model_func=ollama_model_complete,
    llm_model_name="mistral-nemo:latest",
    embedding_func_kwargs={
        "model": "bge-m3:latest",
        "base_url": "http://localhost:11434"
    },
    llm_model_kwargs={
        "model": "mistral-nemo:latest",
        "base_url": "http://localhost:11434"
    }
)
```

### 7.3 Azure OpenAI 集成

```python
from lightrag.llm.azure_openai import azure_openai_complete, azure_openai_embed

# 配置 Azure OpenAI
os.environ["AZURE_OPENAI_API_KEY"] = "your-azure-api-key"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://your-resource.openai.azure.com"
os.environ["AZURE_OPENAI_API_VERSION"] = "2024-08-01-preview"

rag = LightRAG(
    working_dir="./rag_storage",
    embedding_func=azure_openai_embed,
    llm_model_func=azure_openai_complete,
    llm_model_name="your-deployment-name",
)
```

### 7.4 自定义 LLM 和嵌入函数

```python
import numpy as np
from typing import List

async def custom_embedding_func(texts: List[str]) -> np.ndarray:
    """自定义嵌入函数示例"""
    # 这里实现您的嵌入逻辑
    # 返回形状为 (len(texts), embedding_dim) 的 numpy 数组
    embedding_dim = 1536
    embeddings = np.random.rand(len(texts), embedding_dim)
    return embeddings

async def custom_llm_func(
    prompt: str,
    system_prompt: str = None,
    **kwargs
) -> str:
    """自定义 LLM 函数示例"""
    # 这里实现您的 LLM 调用逻辑
    # 返回生成的文本
    response = f"针对提示 '{prompt[:50]}...' 的自定义响应"
    return response

# 使用自定义函数
rag = LightRAG(
    working_dir="./rag_storage",
    embedding_func=custom_embedding_func,
    llm_model_func=custom_llm_func,
)
```

## 8. 高级配置选项

### 8.1 性能调优配置

```python
rag = LightRAG(
    working_dir="./rag_storage",
    embedding_func=openai_embed,
    llm_model_func=gpt_4o_mini_complete,
    
    # 查询参数
    top_k=60,                    # 检索的实体/关系数量
    chunk_top_k=30,             # 最大上下文块数量
    max_entity_tokens=8000,     # 实体最大 token 数
    max_relation_tokens=8000,   # 关系最大 token 数
    max_total_tokens=32000,     # 总最大 token 数
    
    # 文本分块
    chunk_token_size=1200,      # 每个块的最大 token 数
    chunk_overlap_token_size=100,  # 块之间的重叠 token 数
    
    # 并发控制
    llm_model_max_async=4,      # LLM 最大并发数
    embedding_func_max_async=8, # 嵌入最大并发数
    embedding_batch_num=10,     # 嵌入批处理大小
    
    # 实体提取
    entity_extract_max_gleaning=1,  # 实体提取最大尝试次数
)
```

### 8.2 缓存配置

```python
rag = LightRAG(
    working_dir="./rag_storage",
    embedding_func=openai_embed,
    llm_model_func=gpt_4o_mini_complete,
    
    # 嵌入缓存配置
    embedding_cache_config={
        "enabled": True,             # 启用嵌入缓存
        "similarity_threshold": 0.95, # 相似度阈值
        "use_llm_check": False,      # 是否使用 LLM 验证缓存
    }
)
```

### 8.3 工作空间隔离配置

```python
# 通过环境变量设置工作空间
os.environ["WORKSPACE"] = "project_a"

rag = LightRAG(
    working_dir="./rag_storage",
    workspace="project_a",  # 或者直接设置
    embedding_func=openai_embed,
    llm_model_func=gpt_4o_mini_complete,
)
```

## 9. 常见集成模式

### 9.1 单例模式集成

```python
class RAGSingleton:
    """RAG 单例模式"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def initialize(self):
        if self._initialized:
            return
        
        self.rag = LightRAG(
            working_dir="./rag_storage",
            embedding_func=openai_embed,
            llm_model_func=gpt_4o_mini_complete,
        )
        
        await self.rag.initialize_storages()
        await initialize_pipeline_status()
        self._initialized = True
    
    async def query(self, question: str, mode: str = "hybrid"):
        if not self._initialized:
            await self.initialize()
        return await self.rag.aquery(question, param=QueryParam(mode=mode))

# 全局 RAG 实例
rag_instance = RAGSingleton()

async def get_rag():
    """获取全局 RAG 实例"""
    await rag_instance.initialize()
    return rag_instance
```

### 9.2 工厂模式集成

```python
class RAGFactory:
    """RAG 工厂模式"""
    
    @staticmethod
    async def create_rag(config_type: str = "default") -> LightRAG:
        """根据配置类型创建 RAG 实例"""
        
        configs = {
            "default": {
                "working_dir": "./rag_storage",
                "kv_storage": "JsonKVStorage",
                "vector_storage": "NanoVectorDBStorage",
                "graph_storage": "NetworkXStorage",
            },
            "production": {
                "working_dir": "./rag_storage_prod",
                "kv_storage": "PGKVStorage",
                "vector_storage": "PGVectorStorage",
                "graph_storage": "PGGraphStorage",
            },
            "high_performance": {
                "working_dir": "./rag_storage_hp",
                "kv_storage": "RedisKVStorage",
                "vector_storage": "QdrantVectorDBStorage",
                "graph_storage": "Neo4JStorage",
            }
        }
        
        config = configs.get(config_type, configs["default"])
        
        rag = LightRAG(
            embedding_func=openai_embed,
            llm_model_func=gpt_4o_mini_complete,
            **config
        )
        
        await rag.initialize_storages()
        await initialize_pipeline_status()
        
        return rag

# 使用示例
async def main():
    # 创建不同配置的 RAG 实例
    dev_rag = await RAGFactory.create_rag("default")
    prod_rag = await RAGFactory.create_rag("production")
```

### 9.3 上下文管理器集成

```python
from contextlib import asynccontextmanager

class RAGContext:
    """RAG 上下文管理器"""
    
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.rag = None
    
    async def __aenter__(self):
        self.rag = LightRAG(**self.kwargs)
        await self.rag.initialize_storages()
        await initialize_pipeline_status()
        return self.rag
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.rag:
            await self.rag.finalize_storages()

# 使用示例
async def example_with_context():
    async with RAGContext(
        working_dir="./temp_rag",
        embedding_func=openai_embed,
        llm_model_func=gpt_4o_mini_complete,
    ) as rag:
        await rag.ainsert("测试文档内容")
        result = await rag.aquery("测试问题")
        print(result)
```

## 10. 错误处理和最佳实践

### 10.1 完善的错误处理

```python
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

class RAGErrorHandler:
    """RAG 错误处理封装"""
    
    def __init__(self, rag: LightRAG):
        self.rag = rag
        self.logger = logging.getLogger(__name__)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def safe_insert(self, content: str) -> bool:
        """安全的文档插入"""
        try:
            await self.rag.ainsert(content)
            self.logger.info(f"文档插入成功，长度: {len(content)}")
            return True
        except Exception as e:
            self.logger.error(f"文档插入失败: {str(e)}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def safe_query(self, question: str, mode: str = "hybrid") -> str:
        """安全的查询执行"""
        try:
            result = await self.rag.aquery(
                question,
                param=QueryParam(mode=mode)
            )
            self.logger.info(f"查询成功: {question[:50]}...")
            return result
        except Exception as e:
            self.logger.error(f"查询失败: {str(e)}")
            # 降级处理：使用更简单的查询模式
            if mode != "naive":
                self.logger.info("尝试使用简单查询模式")
                return await self.safe_query(question, "naive")
            raise

# 使用示例
async def robust_rag_example():
    rag = LightRAG(
        working_dir="./rag_storage",
        embedding_func=openai_embed,
        llm_model_func=gpt_4o_mini_complete,
    )
    
    await rag.initialize_storages()
    await initialize_pipeline_status()
    
    handler = RAGErrorHandler(rag)
    
    try:
        # 安全插入文档
        success = await handler.safe_insert("测试文档内容")
        if success:
            # 安全查询
            result = await handler.safe_query("测试问题")
            print(result)
    finally:
        await rag.finalize_storages()
```

### 10.2 资源管理最佳实践

```python
import signal
import atexit
from typing import List

class RAGResourceManager:
    """RAG 资源管理器"""
    
    def __init__(self):
        self.active_rags: List[LightRAG] = []
        self.setup_cleanup_handlers()
    
    def setup_cleanup_handlers(self):
        """设置清理处理器"""
        atexit.register(self.cleanup_all)
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        asyncio.create_task(self.cleanup_all())
    
    async def create_rag(self, **kwargs) -> LightRAG:
        """创建并注册 RAG 实例"""
        rag = LightRAG(**kwargs)
        await rag.initialize_storages()
        await initialize_pipeline_status()
        
        self.active_rags.append(rag)
        return rag
    
    async def cleanup_all(self):
        """清理所有 RAG 实例"""
        for rag in self.active_rags:
            try:
                await rag.finalize_storages()
            except Exception as e:
                print(f"清理 RAG 实例时出错: {e}")
        
        self.active_rags.clear()

# 全局资源管理器
resource_manager = RAGResourceManager()

async def managed_rag_example():
    """使用资源管理器的示例"""
    rag = await resource_manager.create_rag(
        working_dir="./managed_rag",
        embedding_func=openai_embed,
        llm_model_func=gpt_4o_mini_complete,
    )
    
    # 使用 RAG
    await rag.ainsert("管理的文档内容")
    result = await rag.aquery("管理的查询")
    print(result)
    
    # 资源会在程序退出时自动清理
```

## 11. 性能优化建议

### 11.1 批量处理优化

```python
class BatchRAGProcessor:
    """批量 RAG 处理器"""
    
    def __init__(self, rag: LightRAG, batch_size: int = 10):
        self.rag = rag
        self.batch_size = batch_size
    
    async def batch_insert(self, documents: List[str]) -> List[bool]:
        """批量插入文档"""
        results = []
        
        for i in range(0, len(documents), self.batch_size):
            batch = documents[i:i + self.batch_size]
            batch_tasks = []
            
            for doc in batch:
                task = asyncio.create_task(self.rag.ainsert(doc))
                batch_tasks.append(task)
            
            # 并发执行批次
            batch_results = await asyncio.gather(
                *batch_tasks, 
                return_exceptions=True
            )
            
            # 处理结果
            for result in batch_results:
                if isinstance(result, Exception):
                    results.append(False)
                    print(f"批量插入错误: {result}")
                else:
                    results.append(True)
        
        return results
    
    async def batch_query(self, questions: List[str], mode: str = "hybrid") -> List[str]:
        """批量查询"""
        query_tasks = []
        
        for question in questions:
            task = asyncio.create_task(
                self.rag.aquery(question, param=QueryParam(mode=mode))
            )
            query_tasks.append(task)
        
        results = await asyncio.gather(*query_tasks, return_exceptions=True)
        
        # 处理异常
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(f"查询失败: {result}")
                print(f"批量查询错误 ({questions[i]}): {result}")
            else:
                processed_results.append(result)
        
        return processed_results
```

### 11.2 缓存策略优化

```python
from functools import lru_cache
import hashlib
import json

class CachedRAG:
    """带缓存的 RAG 封装"""
    
    def __init__(self, rag: LightRAG, cache_size: int = 1000):
        self.rag = rag
        self.query_cache = {}
        self.cache_size = cache_size
    
    def _hash_query(self, question: str, mode: str) -> str:
        """生成查询哈希"""
        query_data = {"question": question, "mode": mode}
        query_str = json.dumps(query_data, sort_keys=True)
        return hashlib.md5(query_str.encode()).hexdigest()
    
    async def cached_query(self, question: str, mode: str = "hybrid") -> str:
        """带缓存的查询"""
        cache_key = self._hash_query(question, mode)
        
        # 检查缓存
        if cache_key in self.query_cache:
            print(f"缓存命中: {question[:50]}...")
            return self.query_cache[cache_key]
        
        # 执行查询
        result = await self.rag.aquery(question, param=QueryParam(mode=mode))
        
        # 更新缓存
        if len(self.query_cache) >= self.cache_size:
            # 简单的 LRU 策略：删除第一个项目
            oldest_key = next(iter(self.query_cache))
            del self.query_cache[oldest_key]
        
        self.query_cache[cache_key] = result
        return result
    
    def clear_cache(self):
        """清空缓存"""
        self.query_cache.clear()
```

## 12. 故障排除

### 12.1 常见问题和解决方案

#### 问题 1：初始化失败

```python
# 错误示例
rag = LightRAG(...)
# 直接使用 rag 而没有初始化 - 会失败

# 正确示例
rag = LightRAG(...)
await rag.initialize_storages()          # 必需！
await initialize_pipeline_status()      # 必需！
```

#### 问题 2：环境变量未设置

```python
def check_environment():
    """检查必需的环境变量"""
    required_vars = {
        "OPENAI_API_KEY": "OpenAI API 密钥",
        # 根据存储后端添加其他必需变量
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"{var} ({description})")
    
    if missing_vars:
        raise ValueError(f"缺少必需的环境变量: {', '.join(missing_vars)}")

# 在初始化前检查
check_environment()
```

#### 问题 3：存储连接失败

```python
async def test_storage_connection(rag: LightRAG):
    """测试存储连接"""
    try:
        # 测试 KV 存储
        await rag.kv_storage.aset("test_key", "test_value")
        value = await rag.kv_storage.aget("test_key")
        assert value == "test_value"
        
        # 测试向量存储
        test_embedding = np.random.rand(1536)
        await rag.vector_storage.aindex("test_node", test_embedding)
        
        print("所有存储连接正常")
        
    except Exception as e:
        print(f"存储连接测试失败: {e}")
        raise
```

### 12.2 调试工具

```python
import time
from contextlib import asynccontextmanager

@asynccontextmanager
async def debug_timer(operation_name: str):
    """调试计时器"""
    start_time = time.time()
    try:
        yield
    finally:
        end_time = time.time()
        print(f"{operation_name} 耗时: {end_time - start_time:.2f} 秒")

class RAGDebugger:
    """RAG 调试工具"""
    
    def __init__(self, rag: LightRAG):
        self.rag = rag
    
    async def debug_query(self, question: str, mode: str = "hybrid"):
        """调试查询过程"""
        print(f"开始调试查询: {question}")
        print(f"查询模式: {mode}")
        
        async with debug_timer("总查询时间"):
            # 执行查询
            result = await self.rag.aquery(
                question,
                param=QueryParam(mode=mode)
            )
        
        print(f"查询结果长度: {len(result)}")
        print(f"前100个字符: {result[:100]}...")
        
        return result
    
    async def debug_storage_status(self):
        """调试存储状态"""
        print("=== 存储状态调试 ===")
        
        # 检查 KV 存储
        try:
            test_key = "debug_test"
            await self.rag.kv_storage.aset(test_key, "test")
            value = await self.rag.kv_storage.aget(test_key)
            print(f"✓ KV 存储正常: {value}")
        except Exception as e:
            print(f"✗ KV 存储异常: {e}")
        
        # 检查向量存储（如果可能）
        try:
            # 这里可以添加向量存储的测试
            print("✓ 向量存储状态检查完成")
        except Exception as e:
            print(f"✗ 向量存储异常: {e}")

# 使用调试工具
async def debug_example():
    rag = LightRAG(
        working_dir="./debug_rag",
        embedding_func=openai_embed,
        llm_model_func=gpt_4o_mini_complete,
    )
    
    await rag.initialize_storages()
    await initialize_pipeline_status()
    
    debugger = RAGDebugger(rag)
    
    # 调试存储状态
    await debugger.debug_storage_status()
    
    # 调试查询
    await rag.ainsert("调试测试文档")
    result = await debugger.debug_query("测试问题")
    
    await rag.finalize_storages()
```

### 12.3 日志配置

```python
import logging.config

def setup_comprehensive_logging():
    """设置全面的日志配置"""
    
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            },
        },
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
                'stream': 'ext://sys.stdout',
            },
            'file': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'detailed',
                'filename': 'lightrag_integration.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
            },
        },
        'loggers': {
            'lightrag': {
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
                'propagate': False,
            },
            '__main__': {
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
                'propagate': False,
            },
        }
    }
    
    logging.config.dictConfig(config)

# 在应用启动时调用
setup_comprehensive_logging()
```

## 总结

本指南提供了将 LightRAG 核心功能集成到现有项目中的全面指导。主要要点包括：

1. **核心依赖**：确保安装正确的依赖项
2. **初始化模式**：始终调用 `initialize_storages()` 和 `initialize_pipeline_status()`
3. **存储选择**：根据需求选择合适的存储后端
4. **错误处理**：实现完善的异常处理和重试机制
5. **资源管理**：确保正确清理资源
6. **性能优化**：使用批量处理和缓存策略

通过遵循本指南，您可以成功地将 LightRAG 的强大检索功能集成到您的应用程序中，无需依赖外部服务部署。