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
    
    def clean_labor_regulation(self, regulation: Dict[str, Any]) -> Dict[str, Any]:
        """
        清洗劳动法规数据
        
        Args:
            regulation: 原始法规数据
            
        Returns:
            清洗后的法规数据
        """
        cleaned = regulation.copy()
        
        # 清洗名称
        if 'name' in cleaned:
            cleaned['name'] = self.clean_document_text(cleaned['name'])
        
        # 清洗内容
        if 'content' in cleaned:
            cleaned['content'] = self.clean_document_text(cleaned['content'])
        
        # 清洗适用范围
        if 'scope' in cleaned:
            cleaned['scope'] = self.clean_document_text(cleaned['scope'])
        
        # 标准化日期格式
        if 'effective_date' in cleaned:
            cleaned['effective_date'] = self._standardize_date(cleaned['effective_date'])
        
        # 生成摘要
        if 'content' in cleaned and 'summary' not in cleaned:
            cleaned['summary'] = self._generate_summary(cleaned['content'])
        
        # 添加清洗标记
        cleaned['cleaned'] = True
        cleaned['cleaned_at'] = datetime.now().isoformat()
        
        return cleaned
    
    def clean_precedent(self, precedent: Dict[str, Any]) -> Dict[str, Any]:
        """
        清洗判决文书数据
        
        Args:
            precedent: 原始判决文书数据
            
        Returns:
            清洗后的判决文书数据
        """
        cleaned = precedent.copy()
        
        # 清洗案件类型
        if 'case_type' in cleaned:
            cleaned['case_type'] = self.clean_document_text(cleaned['case_type'])
        
        # 清洗案件事实
        if 'facts' in cleaned:
            cleaned['facts'] = self.clean_document_text(cleaned['facts'])
        
        # 清洗判决结果
        if 'result' in cleaned:
            cleaned['result'] = self.clean_document_text(cleaned['result'])
        
        # 清洗裁判要点
        if 'key_points' in cleaned:
            if isinstance(cleaned['key_points'], list):
                cleaned['key_points'] = [self.clean_document_text(point) for point in cleaned['key_points']]
            else:
                cleaned['key_points'] = [self.clean_document_text(str(cleaned['key_points']))]
        
        # 清洗法律依据
        if 'legal_basis' in cleaned:
            if isinstance(cleaned['legal_basis'], list):
                cleaned['legal_basis'] = [self.clean_document_text(basis) for basis in cleaned['legal_basis']]
            else:
                cleaned['legal_basis'] = [self.clean_document_text(str(cleaned['legal_basis']))]
        
        # 标准化日期格式
        if 'date' in cleaned:
            cleaned['date'] = self._standardize_date(cleaned['date'])
        
        # 生成案件摘要
        if 'facts' in cleaned and 'summary' not in cleaned:
            cleaned['summary'] = self._generate_case_summary(cleaned)
        
        # 添加清洗标记
        cleaned['cleaned'] = True
        cleaned['cleaned_at'] = datetime.now().isoformat()
        
        return cleaned
    
    def clean_guideline(self, guideline: Dict[str, Any]) -> Dict[str, Any]:
        """
        清洗指导意见数据
        
        Args:
            guideline: 原始指导意见数据
            
        Returns:
            清洗后的指导意见数据
        """
        cleaned = guideline.copy()
        
        # 清洗标题
        if 'title' in cleaned:
            cleaned['title'] = self.clean_document_text(cleaned['title'])
        
        # 清洗内容
        if 'content' in cleaned:
            cleaned['content'] = self.clean_document_text(cleaned['content'])
        
        # 清洗适用范围
        if 'scope' in cleaned:
            cleaned['scope'] = self.clean_document_text(cleaned['scope'])
        
        # 清洗政策要点
        if 'policy_points' in cleaned:
            if isinstance(cleaned['policy_points'], list):
                cleaned['policy_points'] = [self.clean_document_text(point) for point in cleaned['policy_points']]
            else:
                cleaned['policy_points'] = [self.clean_document_text(str(cleaned['policy_points']))]
        
        # 标准化日期格式
        if 'effective_date' in cleaned:
            cleaned['effective_date'] = self._standardize_date(cleaned['effective_date'])
        
        # 生成摘要
        if 'content' in cleaned and 'summary' not in cleaned:
            cleaned['summary'] = self._generate_summary(cleaned['content'])
        
        # 添加清洗标记
        cleaned['cleaned'] = True
        cleaned['cleaned_at'] = datetime.now().isoformat()
        
        return cleaned
    
    def _standardize_date(self, date_str: str) -> str:
        """
        标准化日期格式
        
        Args:
            date_str: 日期字符串
            
        Returns:
            标准化日期字符串
        """
        if not date_str:
            return ""
        
        # 尝试解析常见日期格式
        try:
            # 移除中文日期标记
            date_str = date_str.replace('年', '-').replace('月', '-').replace('日', '')
            
            # 尝试解析日期
            for fmt in ['%Y-%m-%d', '%Y-%m', '%Y', '%Y/%m/%d', '%Y/%m']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
        except Exception:
            pass
        
        return date_str
    
    def _generate_summary(self, text: str, max_length: int = 200) -> str:
        """
        生成文本摘要
        
        Args:
            text: 文本
            max_length: 最大长度
            
        Returns:
            摘要
        """
        if not text:
            return ""
        
        # 简单实现：取前几段
        sentences = text.split('. ')
        summary = '. '.join(sentences[:3])
        
        if len(summary) > max_length:
            summary = summary[:max_length] + '...'
        
        return summary
    
    def _generate_case_summary(self, precedent: Dict[str, Any]) -> str:
        """
        生成案件摘要
        
        Args:
            precedent: 判决文书数据
            
        Returns:
            案件摘要
        """
        parts = []
        
        if 'case_type' in precedent:
            parts.append(f"案件类型: {precedent['case_type']}")
        
        if 'court' in precedent:
            parts.append(f"审理法院: {precedent['court']}")
        
        if 'result' in precedent:
            parts.append(f"判决结果: {precedent['result']}")
        
        return ' | '.join(parts)
    
    def clean_file(self, file_path: str, output_path: Optional[str] = None) -> bool:
        """
        清洗整个文件
        
        Args:
            file_path: 输入文件路径
            output_path: 输出文件路径（可选）
            
        Returns:
            是否成功
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                logger.error(f"文件不存在: {file_path}")
                return False
            
            # 根据文件类型处理
            if file_path.suffix == '.json':
                return self._clean_json_file(file_path, output_path)
            elif file_path.suffix == '.csv':
                return self._clean_csv_file(file_path, output_path)
            elif file_path.suffix in ['.xlsx', '.xls']:
                return self._clean_excel_file(file_path, output_path)
            else:
                logger.error(f"不支持的文件格式: {file_path.suffix}")
                return False
                
        except Exception as e:
            logger.error(f"清洗文件失败: {str(e)}")
            return False
    
    def _clean_json_file(self, file_path: Path, output_path: Optional[str] = None) -> bool:
        """清洗JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 判断数据类型
            if isinstance(data, list):
                cleaned_data = []
                for item in data:
                    cleaned_item = self._clean_item_based_on_type(item)
                    if cleaned_item:
                        cleaned_data.append(cleaned_item)
            else:
                cleaned_data = self._clean_item_based_on_type(data)
            
            # 确定输出路径
            if output_path is None:
                output_path = file_path.parent / f"cleaned_{file_path.name}"
            
            # 保存清洗后的数据
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"JSON文件清洗完成: {file_path} -> {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"清洗JSON文件失败: {str(e)}")
            return False
    
    def _clean_csv_file(self, file_path: Path, output_path: Optional[str] = None) -> bool:
        """清洗CSV文件"""
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            
            # 清洗每一列
            for col in df.columns:
                if df[col].dtype == 'object':  # 文本列
                    df[col] = df[col].apply(lambda x: self.clean_document_text(str(x)) if pd.notnull(x) else x)
            
            # 确定输出路径
            if output_path is None:
                output_path = file_path.parent / f"cleaned_{file_path.name}"
            
            # 保存清洗后的数据
            df.to_csv(output_path, index=False, encoding='utf-8')
            
            logger.info(f"CSV文件清洗完成: {file_path} -> {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"清洗CSV文件失败: {str(e)}")
            return False
    
    def _clean_excel_file(self, file_path: Path, output_path: Optional[str] = None) -> bool:
        """清洗Excel文件"""
        try:
            df = pd.read_excel(file_path)
            
            # 清洗每一列
            for col in df.columns:
                if df[col].dtype == 'object':  # 文本列
                    df[col] = df[col].apply(lambda x: self.clean_document_text(str(x)) if pd.notnull(x) else x)
            
            # 确定输出路径
            if output_path is None:
                output_path = file_path.parent / f"cleaned_{file_path.name}"
            
            # 保存清洗后的数据
            df.to_excel(output_path, index=False)
            
            logger.info(f"Excel文件清洗完成: {file_path} -> {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"清洗Excel文件失败: {str(e)}")
            return False
    
    def _clean_item_based_on_type(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """根据数据类型清洗项目"""
        if not isinstance(item, dict):
            return None
        
        # 根据字段判断数据类型
        if 'case_type' in item or 'court' in item or 'facts' in item:
            return self.clean_precedent(item)
        elif 'name' in item and ('number' in item or 'content' in item):
            return self.clean_labor_regulation(item)
        elif 'title' in item and ('issuing_authority' in item or 'content' in item):
            return self.clean_guideline(item)
        else:
            # 通用清洗
            cleaned = item.copy()
            for key, value in cleaned.items():
                if isinstance(value, str):
                    cleaned[key] = self.clean_document_text(value)
            return cleaned

# 创建全局实例
data_cleaner = DataCleaner()