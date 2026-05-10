#!/usr/bin/env python3
"""
LaborLawNavigator数据集处理脚本
用于处理下载的劳动法数据集，清洗并集成到知识库中
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
import time

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.data_processing.data_cleaner import DataCleaner
from app.services.data_processing.document_processor import DocumentProcessor
from app.services.data_import.data_importer import DataImporter

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LaborLawDatasetProcessor:
    """LaborLawNavigator数据集处理器"""
    
    def __init__(self, dataset_path: str):
        """初始化处理器"""
        self.dataset_path = Path(dataset_path)
        self.data_cleaner = DataCleaner()
        self.document_processor = DocumentProcessor(self.data_cleaner)
        self.data_importer = DataImporter()
        
        # 输出目录
        self.output_dir = project_root / "data" / "processed_laborlaw"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 统计信息
        self.stats = {
            "total_files": 0,
            "processed_files": 0,
            "failed_files": 0,
            "by_format": {},
            "by_category": {},
            "total_size_mb": 0
        }
    
    def process_dataset(self) -> Dict[str, Any]:
        """
        处理整个数据集
        
        Returns:
            处理统计信息
        """
        logger.info(f"开始处理数据集: {self.dataset_path}")
        
        if not self.dataset_path.exists():
            logger.error(f"数据集路径不存在: {self.dataset_path}")
            return self.stats
        
        # 处理所有文档
        processed_docs = self.document_processor.process_directory(str(self.dataset_path))
        
        # 更新统计信息
        self.stats["total_files"] = len(processed_docs)
        self.stats["processed_files"] = len([d for d in processed_docs if "error" not in d])
        self.stats["failed_files"] = len([d for d in processed_docs if "error" in d])
        
        # 按格式统计
        for doc in processed_docs:
            format_type = doc.get("format", "unknown")
            self.stats["by_format"][format_type] = self.stats["by_format"].get(format_type, 0) + 1
            
            # 按分类统计
            if "error" not in doc:
                category = self.document_processor.categorize_document(doc)
                self.stats["by_category"][category] = self.stats["by_category"].get(category, 0) + 1
        
        # 计算总大小
        total_size = 0
        for file_path in self.dataset_path.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        self.stats["total_size_mb"] = total_size / (1024 * 1024)
        
        logger.info(f"数据集处理完成: {self.stats}")
        
        # 保存处理后的文档
        self._save_processed_documents(processed_docs)
        
        # 导入到知识库
        self._import_to_knowledge_base(processed_docs)
        
        return self.stats
    
    def _save_processed_documents(self, processed_docs: List[Dict[str, Any]]) -> None:
        """保存处理后的文档"""
        # 按分类保存
        for category in ["regulation", "case", "template", "guideline", "analysis", "other"]:
            category_docs = []
            for doc in processed_docs:
                if "error" not in doc:
                    doc_category = self.document_processor.categorize_document(doc)
                    if doc_category == category:
                        category_docs.append(doc)
            
            if category_docs:
                # 保存为JSON
                output_file = self.output_dir / f"{category}_documents.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(category_docs, f, ensure_ascii=False, indent=2)
                logger.info(f"保存 {len(category_docs)} 个 {category} 文档到 {output_file}")
        
        # 保存所有文档的摘要
        summary = {
            "processing_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "dataset_path": str(self.dataset_path),
            "stats": self.stats,
            "document_count": len(processed_docs),
            "categories": {}
        }
        
        for doc in processed_docs:
            if "error" not in doc:
                category = self.document_processor.categorize_document(doc)
                file_name = doc.get("metadata", {}).get("file_name", "unknown")
                if category not in summary["categories"]:
                    summary["categories"][category] = []
                summary["categories"][category].append(file_name)
        
        summary_file = self.output_dir / "processing_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        logger.info(f"保存处理摘要到 {summary_file}")
    
    def _import_to_knowledge_base(self, processed_docs: List[Dict[str, Any]]) -> None:
        """将处理后的文档导入到知识库"""
        logger.info("开始导入文档到知识库...")
        
        imported_count = 0
        failed_count = 0
        
        for doc in processed_docs:
            if "error" in doc:
                failed_count += 1
                continue
            
            try:
                # 提取关键信息
                key_info = self.document_processor.extract_key_info(doc)
                
                # 构造导入数据
                import_data = {
                    "content": doc.get("cleaned_content", doc.get("content", "")),
                    "metadata": {
                        "type": "external_dataset",
                        "category": self.document_processor.categorize_document(doc),
                        "source": doc.get("metadata", {}).get("file_name", "unknown"),
                        "file_path": doc.get("metadata", {}).get("file_path", ""),
                        "format": doc.get("format", "unknown"),
                        "processing_date": doc.get("metadata", {}).get("processing_date", ""),
                        "key_info": key_info
                    }
                }
                
                # 保存为临时JSON文件供导入器使用
                temp_file = self.output_dir / "temp_import.json"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump([import_data], f, ensure_ascii=False)
                
                # 导入到知识库
                success = self.data_importer.import_labor_regulations(str(temp_file))
                
                if success:
                    imported_count += 1
                else:
                    failed_count += 1
                
                # 删除临时文件
                if temp_file.exists():
                    temp_file.unlink()
                    
            except Exception as e:
                logger.error(f"导入文档失败: {str(e)}")
                failed_count += 1
        
        logger.info(f"导入完成: {imported_count} 成功, {failed_count} 失败")
    
    def generate_dataset_report(self) -> Dict[str, Any]:
        """生成数据集报告"""
        report = {
            "dataset_info": {
                "name": "LaborLawNavigator",
                "path": str(self.dataset_path),
                "processing_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_size_mb": self.stats["total_size_mb"]
            },
            "processing_stats": self.stats,
            "file_formats": self.stats["by_format"],
            "document_categories": self.stats["by_category"],
            "output_location": str(self.output_dir),
            "integration_status": {
                "imported_to_knowledge_base": self.stats["processed_files"] - self.stats["failed_files"],
                "knowledge_base_collection": "chongqing_labor_knowledge",
                "vector_database": "ChromaDB"
            },
            "recommendations": self._generate_recommendations()
        }
        
        # 保存报告
        report_file = self.output_dir / "dataset_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"生成数据集报告: {report_file}")
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """生成建议"""
        recommendations = []
        
        # 基于统计信息的建议
        if self.stats["failed_files"] > 0:
            recommendations.append(f"有 {self.stats['failed_files']} 个文件处理失败，建议检查这些文件的格式或内容")
        
        if "pdf" in self.stats["by_format"] and self.stats["by_format"]["pdf"] > 0:
            recommendations.append("数据集包含PDF文件，建议安装OCR工具以提高文本提取质量")
        
        if "doc" in self.stats["by_format"] and self.stats["by_format"]["doc"] > 0:
            recommendations.append("数据集包含旧版.doc文件，建议转换为.docx格式以获得更好的处理效果")
        
        if self.stats["by_category"].get("regulation", 0) > 0:
            recommendations.append("数据集包含法规文件，建议在系统中建立法规引用索引")
        
        if self.stats["by_category"].get("case", 0) > 0:
            recommendations.append("数据集包含案例文件，建议建立案例相似度匹配功能")
        
        return recommendations

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="处理LaborLawNavigator数据集")
    parser.add_argument("--dataset-path", type=str, default="LaborLawNavigator",
                       help="数据集路径 (默认: LaborLawNavigator)")
    parser.add_argument("--skip-import", action="store_true",
                       help="跳过导入到知识库的步骤")
    parser.add_argument("--generate-report", action="store_true",
                       help="生成数据集报告")
    
    args = parser.parse_args()
    
    # 检查数据集路径
    dataset_path = Path(args.dataset_path)
    if not dataset_path.exists():
        logger.error(f"数据集路径不存在: {dataset_path}")
        print(f"请先下载数据集: git clone https://www.modelscope.cn/datasets/M12sin30o/LaborLawNavigator.git")
        return
    
    # 创建处理器
    processor = LaborLawDatasetProcessor(args.dataset_path)
    
    # 处理数据集
    print("=" * 60)
    print("开始处理LaborLawNavigator数据集")
    print("=" * 60)
    
    stats = processor.process_dataset()
    
    print("\n" + "=" * 60)
    print("处理统计信息:")
    print("=" * 60)
    print(f"总文件数: {stats['total_files']}")
    print(f"成功处理: {stats['processed_files']}")
    print(f"处理失败: {stats['failed_files']}")
    print(f"数据集大小: {stats['total_size_mb']:.2f} MB")
    
    print("\n按格式统计:")
    for format_type, count in stats['by_format'].items():
        print(f"  {format_type}: {count}")
    
    print("\n按分类统计:")
    for category, count in stats['by_category'].items():
        print(f"  {category}: {count}")
    
    # 生成报告
    if args.generate_report:
        print("\n" + "=" * 60)
        print("生成数据集报告...")
        print("=" * 60)
        report = processor.generate_dataset_report()
        print(f"报告已保存到: {processor.output_dir / 'dataset_report.json'}")
    
    print("\n" + "=" * 60)
    print("处理完成!")
    print("=" * 60)
    print(f"处理后的文档保存在: {processor.output_dir}")
    print(f"文档已集成到知识库: chongqing_labor_knowledge")
    print("=" * 60)

if __name__ == "__main__":
    main()