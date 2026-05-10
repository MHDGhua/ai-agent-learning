#!/usr/bin/env python3
"""
文档处理器
用于处理多种格式的文档文件（.docx, .pdf, .doc, .txt等）
"""

import os
import re
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
from datetime import datetime

# 尝试导入文档处理库
try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    logging.warning("python-docx 库未安装，无法处理 .docx 文件")

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logging.warning("PyPDF2 库未安装，无法处理 .pdf 文件")

try:
    import pandas as pd
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False
    logging.warning("pandas 库未安装，无法处理 .xlsx 文件")

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """文档处理器"""
    
    def __init__(self, data_cleaner=None):
        """初始化文档处理器"""
        self.data_cleaner = data_cleaner
        self.supported_formats = {
            '.docx': self._process_docx,
            '.pdf': self._process_pdf,
            '.doc': self._process_doc,
            '.txt': self._process_txt,
            '.json': self._process_json,
            '.csv': self._process_csv,
            '.xlsx': self._process_excel,
        }
        
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """
        处理单个文档文件
        
        Args:
            file_path: 文档文件路径
            
        Returns:
            处理后的文档数据
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                logger.error(f"文件不存在: {file_path}")
                return {"error": "文件不存在", "file_path": str(file_path)}
            
            # 获取文件扩展名
            ext = file_path.suffix.lower()
            
            # 检查是否支持该格式
            if ext not in self.supported_formats:
                logger.warning(f"不支持的文件格式: {ext}")
                return {"error": f"不支持的文件格式: {ext}", "file_path": str(file_path)}
            
            # 检查必要的库是否可用
            if ext == '.docx' and not DOCX_AVAILABLE:
                return {"error": "python-docx 库未安装", "file_path": str(file_path)}
            elif ext == '.pdf' and not PDF_AVAILABLE:
                return {"error": "PyPDF2 库未安装", "file_path": str(file_path)}
            elif ext == '.xlsx' and not EXCEL_AVAILABLE:
                return {"error": "pandas 库未安装", "file_path": str(file_path)}
            
            # 调用对应的处理函数
            processor_func = self.supported_formats[ext]
            result = processor_func(file_path)
            
            # 添加元数据
            result["metadata"] = {
                "file_name": file_path.name,
                "file_path": str(file_path),
                "file_size": file_path.stat().st_size,
                "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                "file_extension": ext,
                "processing_date": datetime.now().isoformat()
            }
            
            # 如果提供了数据清洗器，则清洗数据
            if self.data_cleaner and "content" in result:
                result["content"] = self.data_cleaner.clean_document_text(result["content"])
            
            return result
            
        except Exception as e:
            logger.error(f"处理文档失败 {file_path}: {str(e)}")
            return {"error": f"处理失败: {str(e)}", "file_path": str(file_path)}
    
    def process_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """
        批量处理目录中的所有文档
        
        Args:
            directory_path: 目录路径
            
        Returns:
            处理后的文档列表
        """
        directory_path = Path(directory_path)
        if not directory_path.exists() or not directory_path.is_dir():
            logger.error(f"目录不存在: {directory_path}")
            return []
        
        processed_docs = []
        for file_path in directory_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                doc_result = self.process_document(str(file_path))
                processed_docs.append(doc_result)
        
        return processed_docs
    
    def categorize_document(self, document: Dict[str, Any]) -> str:
        """
        根据文档内容对文档进行分类
        
        Args:
            document: 文档数据
            
        Returns:
            文档分类
        """
        content = document.get("content", "")
        name = document.get("name", "").lower()
        
        # 基于关键词进行分类
        if any(keyword in content.lower() or keyword in name for keyword in ["条例", "规定", "办法", "实施细则"]):
            return "法律法规"
        elif any(keyword in content.lower() or keyword in name for keyword in ["案例", "判决", "裁定", "裁决"]):
            return "判例"
        elif any(keyword in content.lower() or keyword in name for keyword in ["指导意见", "通知", "函"]):
            return "指导性文件"
        elif any(keyword in content.lower() or keyword in name for keyword in ["合同", "协议", "劳动合同"]):
            return "合同模板"
        else:
            return "其他"
    
    def _process_docx(self, file_path: Path) -> Dict[str, Any]:
        """处理DOCX文档"""
        try:
            doc = docx.Document(str(file_path))
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            content = '\n'.join(paragraphs)
            return {
                "content": content,
                "format": "docx",
                "title": doc.core_properties.title or file_path.stem
            }
        except Exception as e:
            logger.error(f"处理DOCX文件失败: {str(e)}")
            return {"error": f"DOCX处理失败: {str(e)}", "format": "docx"}
    
    def _process_pdf(self, file_path: Path) -> Dict[str, Any]:
        """处理PDF文档"""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                content = ""
                for page in reader.pages:
                    content += page.extract_text()
                return {
                    "content": content,
                    "format": "pdf",
                    "title": file_path.stem
                }
        except Exception as e:
            logger.error(f"处理PDF文件失败: {str(e)}")
            return {"error": f"PDF处理失败: {str(e)}", "format": "pdf"}
    
    def _process_doc(self, file_path: Path) -> Dict[str, Any]:
        """处理DOC文档（简化实现）"""
        try:
            # 这里可以使用python-docx处理DOC文件，但需要额外的库
            # 为了简化，我们只读取文件内容
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
            return {
                "content": content,
                "format": "doc",
                "title": file_path.stem
            }
        except Exception as e:
            logger.error(f"处理DOC文件失败: {str(e)}")
            return {"error": f"DOC处理失败: {str(e)}", "format": "doc"}
    
    def _process_txt(self, file_path: Path) -> Dict[str, Any]:
        """处理TXT文档"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
            return {
                "content": content,
                "format": "txt",
                "title": file_path.stem
            }
        except Exception as e:
            logger.error(f"处理TXT文件失败: {str(e)}")
            return {"error": f"TXT处理失败: {str(e)}", "format": "txt"}
    
    def _process_json(self, file_path: Path) -> Dict[str, Any]:
        """处理JSON文档"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            return {
                "content": json.dumps(data, ensure_ascii=False, indent=2),
                "format": "json",
                "title": file_path.stem,
                "raw_data": data
            }
        except Exception as e:
            logger.error(f"处理JSON文件失败: {str(e)}")
            return {"error": f"JSON处理失败: {str(e)}", "format": "json"}
    
    def _process_csv(self, file_path: Path) -> Dict[str, Any]:
        """处理CSV文档"""
        try:
            df = pd.read_csv(file_path)
            content = df.to_string(index=False)
            return {
                "content": content,
                "format": "csv",
                "title": file_path.stem,
                "columns": list(df.columns)
            }
        except Exception as e:
            logger.error(f"处理CSV文件失败: {str(e)}")
            return {"error": f"CSV处理失败: {str(e)}", "format": "csv"}
    
    def _process_excel(self, file_path: Path) -> Dict[str, Any]:
        """处理Excel文档"""
        try:
            df = pd.read_excel(file_path)
            content = df.to_string(index=False)
            return {
                "content": content,
                "format": "xlsx",
                "title": file_path.stem,
                "columns": list(df.columns)
            }
        except Exception as e:
            logger.error(f"处理Excel文件失败: {str(e)}")
            return {"error": f"Excel处理失败: {str(e)}", "format": "xlsx"}
