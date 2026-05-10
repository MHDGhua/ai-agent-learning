#!/usr/bin/env python3
"""
劳动法数据清洗工具
用于清洗和格式化外部劳动法数据集
"""

import os
import re
import json
import pandas as pd
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DataCleaner:
    """数据清洗器"""
    
    def __init__(self):
        """初始化数据清洗器"""
        self.chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
        self.number_pattern = re.compile(r'\d+')
        self.date_pattern = re.compile(r'\d{4}[-年]\d{1,2}[-月]\d{1,2}[日]?')
        
    def clean_document_text(self, text: str) -> str:
        """
        清洗文档文本
        
        Args:
            text: 原始文本
            
        Returns:
            清洗后的文本
        """
        if not text:
            return ""
        
        # 1. 移除多余的空格和换行
        text = re.sub(r'\s+', ' ', text)
        
        # 2. 移除特殊字符，但保留中文标点
        text = re.sub(r'[^\u4e00-\u9fff\w\s，。；：！？、（）《》【】「」""''-]', '', text)
        
        # 3. 标准化标点符号
        text = text.replace('，', ', ').replace('。', '. ')
        text = text.replace('；', '; ').replace('：', ': ')
        text = text.replace('！', '! ').replace('？', '? ')
        text = text.replace('、', ', ').replace('（', '(').replace('）', ')')
        text = text.replace('《', '"').replace('》', '"')
        text = text.replace('【', '[').replace('】', ']')
        text = text.replace('「', '"').replace('」', '"')
        
        # 4. 移除重复的标点
        text = re.sub(r'([,.!?;:])\1+', r'\1', text)
        
        # 5. 确保句子以标点结束
        if text and text[-1] not in '.!?;:':
            text += '.'
        
        return text.strip()
    
    def extract_chinese_text(self, text: str) -> str:
        """
        提取中文文本
        
        Args:
            text: 原始文本
            
        Returns:
            中文文本
        """
        if not text:
            return ""
        
        # 提取中文字符
        chinese_chars = self.chinese_pattern.findall(text)
        return ' '.join(chinese_chars)
    
    def extract_dates(self, text: str) -> List[str]:
        """
        提取日期信息
        
        Args:
            text: 文本
            
        Returns:
            日期列表
        """
        dates = self.date_pattern.findall(text)
        return dates
    
    def extract_numbers(self, text: str) -> List[str]:
        """
        提取数字信息
        
        Args:
            text: 文本
            
        Returns:
            数字列表
        """
        numbers = self.number_pattern.findall(text)
        return numbers
    
    def clean_json_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        清洗JSON数据
        
        Args:
            data: 原始JSON数据
            
        Returns:
            清洗后的JSON数据
        """
        cleaned_data = {}
        for key, value in data.items():
            if isinstance(value, str):
                cleaned_data[key] = self.clean_document_text(value)
            elif isinstance(value, dict):
                cleaned_data[key] = self.clean_json_data(value)
            elif isinstance(value, list):
                cleaned_data[key] = [self.clean_json_data(item) if isinstance(item, dict) else item for item in value]
            else:
                cleaned_data[key] = value
        return cleaned_data

    def validate_data_integrity(self, data: Dict[str, Any]) -> bool:
        """
        验证数据完整性
        
        Args:
            data: 待验证的数据
            
        Returns:
            数据是否完整
        """
        required_fields = ['id', 'name', 'content']
        return all(field in data for field in required_fields)