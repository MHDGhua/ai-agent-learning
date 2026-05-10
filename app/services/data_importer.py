#!/usr/bin/env python3
"""
外部劳动法数据集导入器
用于导入和处理劳动法数据集、判决文书典例和指导意见
"""

import os
import json
import csv
from typing import List, Dict, Any
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

class LocalTFIDFEmbeddingFunction:
    """本地TF-IDF嵌入函数"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=512)
        self.fitted = False
        
    def name(self) -> str:
        """返回嵌入函数名称"""
        return "localtfidf"
    
    def fit(self, documents: List[str]) -> None:
        """训练TF-IDF模型"""
        self.vectorizer.fit(documents)
        self.fitted = True
    
    def __call__(self, input: List[str]) -> List[List[float]]:
        """生成嵌入向量"""
        if not self.fitted:
            # 如果没有训练，使用简单词频作为回退
            return [self._simple_embedding(text) for text in input]
        embeddings = self.vectorizer.transform(input).toarray()
        return embeddings.tolist()
    
    def _simple_embedding(self, text: str) -> List[float]:
        """简单词频嵌入作为回退"""
        words = text.split()
        word_count = {}
        for word in words:
            word_count[word] = word_count.get(word, 0) + 1
        embedding = [word_count.get(word, 0) for word in sorted(word_count.keys())]
        # 填充或截断到512维
        if len(embedding) > 512:
            embedding = embedding[:512]
        else:
            embedding += [0] * (512 - len(embedding))
        return embedding
from chromadb.config import Settings
from loguru import logger

# 配置常量
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", os.path.join("data", "chroma_db"))
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "chongqing_labor_knowledge")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "shibing624/text2vec-base-chinese")

class DataImporter:
    """外部数据导入器"""
    
    def __init__(self):
        """初始化数据导入器"""
        # 使用本地TF-IDF嵌入函数
        self.embedding_fn = LocalTFIDFEmbeddingFunction()
        self.client = chromadb.PersistentClient(
            path=os.path.abspath(CHROMA_PERSIST_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name=CHROMA_COLLECTION,
            embedding_function=self.embedding_fn,
        )
        logger.info("数据导入器初始化完成")
    
    def import_labor_regulations(self, file_path: str) -> bool:
        """
        导入劳动法数据集
        
        Args:
            file_path: 劳动法数据文件路径
            
        Returns:
            导入是否成功
        """
        try:
            # 支持多种格式
            if file_path.endswith('.json'):
                return self._import_json_regulations(file_path)
            elif file_path.endswith('.csv'):
                return self._import_csv_regulations(file_path)
            else:
                logger.warning(f"不支持的文件格式: {file_path}")
                return False
        except Exception as e:
            logger.error(f"导入劳动法数据失败: {str(e)}")
            return False
    
    def _import_json_regulations(self, file_path: str) -> bool:
        """导入JSON格式的劳动法数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                regulations_data = json.load(f)
            
            documents = []
            metadatas = []
            ids = []
            
            for i, regulation in enumerate(regulations_data):
                # 构造文档内容
                content = self._format_regulation_content(regulation)
                documents.append(content)
                metadatas.append({
                    "type": "regulation",
                    "source": file_path,
                    "id": regulation.get("id", f"reg_{i}"),
                    "category": regulation.get("category", "general"),
                    "effective_date": regulation.get("effective_date", ""),
                    "jurisdiction": "重庆"
                })
                ids.append(f"reg_{i}_{hash(content) % 1000000}")  # 确保唯一ID
            
            # 批量添加到向量数据库
            if documents:
                # 先训练TF-IDF模型
                self.embedding_fn.fit(documents)
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                logger.info(f"成功导入 {len(documents)} 条劳动法规")
                return True
            else:
                logger.warning("没有找到有效的劳动法规数据")
                return False
                
        except Exception as e:
            logger.error(f"导入JSON劳动法规失败: {str(e)}")
            return False
    
    def _import_csv_regulations(self, file_path: str) -> bool:
        """导入CSV格式的劳动法数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                regulations_data = list(reader)
            
            documents = []
            metadatas = []
            ids = []
            
            for i, regulation in enumerate(regulations_data):
                # 构造文档内容
                content = self._format_regulation_content_from_csv(regulation)
                documents.append(content)
                metadatas.append({
                    "type": "regulation",
                    "source": file_path,
                    "id": regulation.get("id", f"reg_{i}"),
                    "category": regulation.get("category", "general"),
                    "effective_date": regulation.get("effective_date", ""),
                    "jurisdiction": "重庆"
                })
                ids.append(f"reg_{i}_{hash(content) % 1000000}")  # 确保唯一ID
            
            # 批量添加到向量数据库
            if documents:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                logger.info(f"成功导入 {len(documents)} 条劳动法规")
                return True
            else:
                logger.warning("没有找到有效的劳动法规数据")
                return False
                
        except Exception as e:
            logger.error(f"导入CSV劳动法规失败: {str(e)}")
            return False
    
    def import_precedents(self, file_path: str) -> bool:
        """
        导入判决文书典例
        
        Args:
            file_path: 判决文书文件路径
            
        Returns:
            导入是否成功
        """
        try:
            if file_path.endswith('.json'):
                return self._import_json_precedents(file_path)
            elif file_path.endswith('.csv'):
                return self._import_csv_precedents(file_path)
            else:
                logger.warning(f"不支持的文件格式: {file_path}")
                return False
        except Exception as e:
            logger.error(f"导入判决文书失败: {str(e)}")
            return False
    
    def _import_json_precedents(self, file_path: str) -> bool:
        """导入JSON格式的判决文书"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                precedents_data = json.load(f)
            
            documents = []
            metadatas = []
            ids = []
            
            for i, precedent in enumerate(precedents_data):
                # 构造文档内容
                content = self._format_precedent_content(precedent)
                documents.append(content)
                metadatas.append({
                    "type": "precedent",
                    "source": file_path,
                    "id": precedent.get("id", f"prec_{i}"),
                    "case_type": precedent.get("case_type", "unknown"),
                    "court": precedent.get("court", ""),
                    "date": precedent.get("date", ""),
                    "result": precedent.get("result", ""),
                    "jurisdiction": "重庆"
                })
                ids.append(f"prec_{i}_{hash(content) % 1000000}")  # 确保唯一ID
            
            # 批量添加到向量数据库
            if documents:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                logger.info(f"成功导入 {len(documents)} 条判决文书")
                return True
            else:
                logger.warning("没有找到有效的判决文书数据")
                return False
                
        except Exception as e:
            logger.error(f"导入JSON判决文书失败: {str(e)}")
            return False
    
    def _import_csv_precedents(self, file_path: str) -> bool:
        """导入CSV格式的判决文书"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                precedents_data = list(reader)
            
            documents = []
            metadatas = []
            ids = []
            
            for i, precedent in enumerate(precedents_data):
                # 构造文档内容
                content = self._format_precedent_content_from_csv(precedent)
                documents.append(content)
                metadatas.append({
                    "type": "precedent",
                    "source": file_path,
                    "id": precedent.get("id", f"prec_{i}"),
                    "case_type": precedent.get("case_type", "unknown"),
                    "court": precedent.get("court", ""),
                    "date": precedent.get("date", ""),
                    "result": precedent.get("result", ""),
                    "jurisdiction": "重庆"
                })
                ids.append(f"prec_{i}_{hash(content) % 1000000}")  # 确保唯一ID
            
            # 批量添加到向量数据库
            if documents:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                logger.info(f"成功导入 {len(documents)} 条判决文书")
                return True
            else:
                logger.warning("没有找到有效的判决文书数据")
                return False
                
        except Exception as e:
            logger.error(f"导入CSV判决文书失败: {str(e)}")
            return False
    
    def import_guidelines(self, file_path: str) -> bool:
        """
        导入指导意见
        
        Args:
            file_path: 指导意见文件路径
            
        Returns:
            导入是否成功
        """
        try:
            if file_path.endswith('.json'):
                return self._import_json_guidelines(file_path)
            elif file_path.endswith('.csv'):
                return self._import_csv_guidelines(file_path)
            else:
                logger.warning(f"不支持的文件格式: {file_path}")
                return False
        except Exception as e:
            logger.error(f"导入指导意见失败: {str(e)}")
            return False
    
    def _import_json_guidelines(self, file_path: str) -> bool:
        """导入JSON格式的指导意见"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                guidelines_data = json.load(f)
            
            documents = []
            metadatas = []
            ids = []
            
            for i, guideline in enumerate(guidelines_data):
                # 构造文档内容
                content = self._format_guideline_content(guideline)
                documents.append(content)
                metadatas.append({
                    "type": "guideline",
                    "source": file_path,
                    "id": guideline.get("id", f"guide_{i}"),
                    "category": guideline.get("category", "general"),
                    "effective_date": guideline.get("effective_date", ""),
                    "issuing_authority": guideline.get("issuing_authority", ""),
                    "jurisdiction": "重庆"
                })
                ids.append(f"guide_{i}_{hash(content) % 1000000}")  # 确保唯一ID
            
            # 批量添加到向量数据库
            if documents:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                logger.info(f"成功导入 {len(documents)} 条指导意见")
                return True
            else:
                logger.warning("没有找到有效的指导意见数据")
                return False
                
        except Exception as e:
            logger.error(f"导入JSON指导意见失败: {str(e)}")
            return False
    
    def _import_csv_guidelines(self, file_path: str) -> bool:
        """导入CSV格式的指导意见"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                guidelines_data = list(reader)
            
            documents = []
            metadatas = []
            ids = []
            
            for i, guideline in enumerate(guidelines_data):
                # 构造文档内容
                content = self._format_guideline_content_from_csv(guideline)
                documents.append(content)
                metadatas.append({
                    "type": "guideline",
                    "source": file_path,
                    "id": guideline.get("id", f"guide_{i}"),
                    "category": guideline.get("category", "general"),
                    "effective_date": guideline.get("effective_date", ""),
                    "issuing_authority": guideline.get("issuing_authority", ""),
                    "jurisdiction": "重庆"
                })
                ids.append(f"guide_{i}_{hash(content) % 1000000}")  # 确保唯一ID
            
            # 批量添加到向量数据库
            if documents:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                logger.info(f"成功导入 {len(documents)} 条指导意见")
                return True
            else:
                logger.warning("没有找到有效的指导意见数据")
                return False
                
        except Exception as e:
            logger.error(f"导入CSV指导意见失败: {str(e)}")
            return False
    
    def _format_regulation_content(self, regulation: Dict[str, Any]) -> str:
        """格式化劳动法规内容"""
        content_parts = []
        content_parts.append(f"法规名称: {regulation.get('name', '未知')}")
        content_parts.append(f"法规编号: {regulation.get('number', '无')}")
        content_parts.append(f"适用范围: {regulation.get('scope', '无')}")
        content_parts.append(f"主要内容: {regulation.get('content', '无')}")
        content_parts.append(f"生效日期: {regulation.get('effective_date', '无')}")
        content_parts.append(f"修订版本: {regulation.get('revision', '无')}")
        return "\n".join(content_parts)
    
    def _format_regulation_content_from_csv(self, regulation: Dict[str, Any]) -> str:
        """从CSV格式格式化劳动法规内容"""
        content_parts = []
        content_parts.append(f"法规名称: {regulation.get('name', '未知')}")
        content_parts.append(f"法规编号: {regulation.get('number', '无')}")
        content_parts.append(f"适用范围: {regulation.get('scope', '无')}")
        content_parts.append(f"主要内容: {regulation.get('content', '无')}")
        content_parts.append(f"生效日期: {regulation.get('effective_date', '无')}")
        content_parts.append(f"修订版本: {regulation.get('revision', '无')}")
        return "\n".join(content_parts)
    
    def _format_precedent_content(self, precedent: Dict[str, Any]) -> str:
        """格式化判决文书内容"""
        content_parts = []
        content_parts.append(f"案件编号: {precedent.get('id', '无')}")
        content_parts.append(f"案件类型: {precedent.get('case_type', '未知')}")
        content_parts.append(f"审理法院: {precedent.get('court', '无')}")
        content_parts.append(f"判决日期: {precedent.get('date', '无')}")
        content_parts.append(f"案件事实: {precedent.get('facts', '无')}")
        content_parts.append(f"判决结果: {precedent.get('result', '无')}")
        content_parts.append(f"裁判要点: {precedent.get('key_points', '无')}")
        content_parts.append(f"法律依据: {precedent.get('legal_basis', '无')}")
        return "\n".join(content_parts)
    
    def _format_precedent_content_from_csv(self, precedent: Dict[str, Any]) -> str:
        """从CSV格式格式化判决文书内容"""
        content_parts = []
        content_parts.append(f"案件编号: {precedent.get('id', '无')}")
        content_parts.append(f"案件类型: {precedent.get('case_type', '未知')}")
        content_parts.append(f"审理法院: {precedent.get('court', '无')}")
        content_parts.append(f"判决日期: {precedent.get('date', '无')}")
        content_parts.append(f"案件事实: {precedent.get('facts', '无')}")
        content_parts.append(f"判决结果: {precedent.get('result', '无')}")
        content_parts.append(f"裁判要点: {precedent.get('key_points', '无')}")
        content_parts.append(f"法律依据: {precedent.get('legal_basis', '无')}")
        return "\n".join(content_parts)
    
    def _format_guideline_content(self, guideline: Dict[str, Any]) -> str:
        """格式化指导意见内容"""
        content_parts = []
        content_parts.append(f"指导意见标题: {guideline.get('title', '无')}")
        content_parts.append(f"发布机构: {guideline.get('issuing_authority', '无')}")
        content_parts.append(f"发布日期: {guideline.get('effective_date', '无')}")
        content_parts.append(f"指导意见内容: {guideline.get('content', '无')}")
        content_parts.append(f"适用范围: {guideline.get('scope', '无')}")
        content_parts.append(f"政策要点: {guideline.get('policy_points', '无')}")
        return "\n".join(content_parts)
    
    def _format_guideline_content_from_csv(self, guideline: Dict[str, Any]) -> str:
        """从CSV格式格式化指导意见内容"""
        content_parts = []
        content_parts.append(f"指导意见标题: {guideline.get('title', '无')}")
        content_parts.append(f"发布机构: {guideline.get('issuing_authority', '无')}")
        content_parts.append(f"发布日期: {guideline.get('effective_date', '无')}")
        content_parts.append(f"指导意见内容: {guideline.get('content', '无')}")
        content_parts.append(f"适用范围: {guideline.get('scope', '无')}")
        content_parts.append(f"政策要点: {guideline.get('policy_points', '无')}")
        return "\n".join(content_parts)
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": self.collection.name
            }
        except Exception as e:
            logger.error(f"获取知识库统计信息失败: {str(e)}")
            return {"total_documents": 0, "collection_name": self.collection.name}

# 创建全局实例
data_importer = DataImporter()
