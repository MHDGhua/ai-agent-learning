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
        
    def name(self):
        """返回嵌入函数名称"""
        return "localtfidf"
    
    def fit(self, documents: List[str]):
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
                data = json.load(f)
            
            # 处理每个数据项
            for item in data:
                # 构建文档内容
                content_parts = [
                    item.get('name', ''),
                    item.get('content', ''),
                    item.get('scope', ''),
                    item.get('legal_basis', '')
                ]
                content = ' '.join(content_parts)
                
                # 构建元数据
                metadata = {
                    'id': item.get('id', ''),
                    'type': 'regulation',
                    'name': item.get('name', ''),
                    'number': item.get('number', ''),
                    'effective_date': item.get('effective_date', ''),
                    'revision': item.get('revision', ''),
                    'source': file_path
                }
                
                # 添加到知识库
                self.collection.add(
                    ids=[item.get('id', '')],
                    documents=[content],
                    metadatas=[metadata]
                )
            
            logger.info(f"成功导入JSON劳动法数据: {len(data)} 条记录")
            return True
        except Exception as e:
            logger.error(f"导入JSON劳动法数据失败: {str(e)}")
            return False
    
    def _import_csv_regulations(self, file_path: str) -> bool:
        """导入CSV格式的劳动法数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = list(reader)
            
            # 处理每个数据项
            for item in data:
                # 构建文档内容
                content_parts = [
                    item.get('name', ''),
                    item.get('content', ''),
                    item.get('scope', ''),
                    item.get('legal_basis', '')
                ]
                content = ' '.join(content_parts)
                
                # 构建元数据
                metadata = {
                    'id': item.get('id', ''),
                    'type': 'regulation',
                    'name': item.get('name', ''),
                    'number': item.get('number', ''),
                    'effective_date': item.get('effective_date', ''),
                    'revision': item.get('revision', ''),
                    'source': file_path
                }
                
                # 添加到知识库
                self.collection.add(
                    ids=[item.get('id', '')],
                    documents=[content],
                    metadatas=[metadata]
                )
            
            logger.info(f"成功导入CSV劳动法数据: {len(data)} 条记录")
            return True
        except Exception as e:
            logger.error(f"导入CSV劳动法数据失败: {str(e)}")
            return False
    
    def import_court_precedents(self, file_path: str) -> bool:
        """
        导入法院判例数据
        
        Args:
            file_path: 判例文件路径
            
        Returns:
            导入是否成功
        """
        try:
            if file_path.endswith('.json'):
                return self._import_json_precedents(file_path)
            else:
                logger.warning(f"不支持的文件格式: {file_path}")
                return False
        except Exception as e:
            logger.error(f"导入判例数据失败: {str(e)}")
            return False
    
    def _import_json_precedents(self, file_path: str) -> bool:
        """导入JSON格式的判例数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 处理每个数据项
            for item in data:
                # 构建文档内容
                content_parts = [
                    item.get('case_type', ''),
                    item.get('facts', ''),
                    item.get('result', ''),
                    item.get('key_points', ''),
                    item.get('legal_basis', '')
                ]
                content = ' '.join(content_parts)
                
                # 构建元数据
                metadata = {
                    'id': item.get('id', ''),
                    'type': 'precedent',
                    'case_type': item.get('case_type', ''),
                    'court': item.get('court', ''),
                    'date': item.get('date', ''),
                    'source': file_path
                }
                
                # 添加到知识库
                self.collection.add(
                    ids=[item.get('id', '')],
                    documents=[content],
                    metadatas=[metadata]
                )
            
            logger.info(f"成功导入JSON判例数据: {len(data)} 条记录")
            return True
        except Exception as e:
            logger.error(f"导入JSON判例数据失败: {str(e)}")
            return False
    
    def import_guidelines(self, file_path: str) -> bool:
        """
        导入指导意见数据
        
        Args:
            file_path: 指导意见文件路径
            
        Returns:
            导入是否成功
        """
        try:
            if file_path.endswith('.json'):
                return self._import_json_guidelines(file_path)
            else:
                logger.warning(f"不支持的文件格式: {file_path}")
                return False
        except Exception as e:
            logger.error(f"导入指导意见数据失败: {str(e)}")
            return False
    
    def _import_json_guidelines(self, file_path: str) -> bool:
        """导入JSON格式的指导意见数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 处理每个数据项
            for item in data:
                # 构建文档内容
                content_parts = [
                    item.get('title', ''),
                    item.get('content', ''),
                    item.get('scope', ''),
                    item.get('policy_points', '')
                ]
                content = ' '.join(content_parts)
                
                # 构建元数据
                metadata = {
                    'id': item.get('id', ''),
                    'type': 'guideline',
                    'title': item.get('title', ''),
                    'issuing_authority': item.get('issuing_authority', ''),
                    'effective_date': item.get('effective_date', ''),
                    'source': file_path
                }
                
                # 添加到知识库
                self.collection.add(
                    ids=[item.get('id', '')],
                    documents=[content],
                    metadatas=[metadata]
                )
            
            logger.info(f"成功导入JSON指导意见数据: {len(data)} 条记录")
            return True
        except Exception as e:
            logger.error(f"导入JSON指导意见数据失败: {str(e)}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        获取知识库统计信息
        
        Returns:
            统计信息
        """
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": CHROMA_COLLECTION
            }
        except Exception as e:
            logger.error(f"获取统计信息失败: {str(e)}")
            return {"error": str(e)}
    
    def search_documents(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        在知识库中搜索文档
        
        Args:
            query: 搜索查询
            limit: 返回结果数量限制
            
        Returns:
            搜索结果列表
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=limit,
                include=['documents', 'metadatas', 'distances']
            )
            
            # 格式化结果
            formatted_results = []
            for i, document in enumerate(results['documents'][0]):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'content': document,
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i]
                })
            
            return formatted_results
        except Exception as e:
            logger.error(f"搜索文档失败: {str(e)}")
            return []