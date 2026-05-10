#!/usr/bin/env python3
"""
外部数据导入脚本示例
用于演示如何导入劳动法数据集、判决文书典例和指导意见
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.data_importer import data_importer
from loguru import logger

def main():
    """主函数"""
    logger.info("开始导入外部劳动法数据...")
    
    # 创建示例数据目录
    data_dir = Path("data/external_datasets")
    data_dir.mkdir(exist_ok=True)
    
    # 示例：创建劳动法数据文件
    labor_regulations_data = [
        {
            "id": "cq_labor_001",
            "name": "重庆市劳动合同条例",
            "number": "渝人发〔2023〕15号",
            "scope": "适用于重庆市内所有用人单位和劳动者",
            "content": "用人单位应当依法与劳动者签订书面劳动合同，明确双方权利义务。",
            "effective_date": "2023-01-01",
            "revision": "2023版"
        },
        {
            "id": "cq_labor_002",
            "name": "重庆市最低工资规定",
            "number": "渝政发〔2022〕28号",
            "scope": "适用于重庆市行政区域内所有用人单位",
            "content": "重庆市月最低工资标准为2100元，非全日制用工小时最低工资标准为20元。",
            "effective_date": "2022-07-01",
            "revision": "2022版"
        }
    ]
    
    # 示例：创建判决文书数据
    precedents_data = [
        {
            "id": "cq_prec_001",
            "case_type": "加班费纠纷",
            "court": "重庆市江北区人民法院",
            "date": "2023-05-15",
            "facts": "申请人自2022年入职公司，每月加班约20小时，公司未支付加班费。",
            "result": "支持申请人，判决公司支付加班费共计8000元",
            "key_points": ["加班事实清楚", "公司未支付加班费", "适用《劳动法》第44条"],
            "legal_basis": ["《劳动法》第44条", "《劳动合同法》第85条"]
        },
        {
            "id": "cq_prec_002",
            "case_type": "违法解除劳动合同",
            "court": "重庆市渝中区人民法院",
            "date": "2023-08-22",
            "facts": "公司以员工违反规章制度为由解除劳动合同，但未履行民主程序。",
            "result": "支持申请人，判决公司支付违法解除赔偿金",
            "key_points": ["解除程序违法", "未履行民主程序", "适用《劳动合同法》第48条"],
            "legal_basis": ["《劳动合同法》第48条", "《劳动合同法》第87条"]
        }
    ]
    
    # 示例：创建指导意见数据
    guidelines_data = [
        {
            "id": "cq_guide_001",
            "title": "关于加班费计算的指导意见",
            "issuing_authority": "重庆市人力资源和社会保障局",
            "effective_date": "2023-03-01",
            "content": "加班费计算应按照劳动者正常工作时间工资标准的150%支付平日加班费。",
            "scope": "适用于全市各类用人单位",
            "policy_points": ["明确加班费计算标准", "规范用人单位行为"]
        }
    ]
    
    # 导入数据到JSON文件
    regulations_file = data_dir / "labor_regulations.json"
    precedents_file = data_dir / "court_precedents.json"
    guidelines_file = data_dir / "guidelines.json"
    
    import json
    
    with open(regulations_file, 'w', encoding='utf-8') as f:
        json.dump(labor_regulations_data, f, ensure_ascii=False, indent=2)
    
    with open(precedents_file, 'w', encoding='utf-8') as f:
        json.dump(precedents_data, f, ensure_ascii=False, indent=2)
    
    with open(guidelines_file, 'w', encoding='utf-8') as f:
        json.dump(guidelines_data, f, ensure_ascii=False, indent=2)
    
    logger.info("创建示例数据文件完成")
    
    # 导入劳动法数据
    logger.info("正在导入劳动法数据...")
    success = data_importer.import_labor_regulations(str(regulations_file))
    if success:
        logger.info("劳动法数据导入成功")
    else:
        logger.error("劳动法数据导入失败")
    
    # 导入判决文书
    logger.info("正在导入判决文书...")
    success = data_importer.import_precedents(str(precedents_file))
    if success:
        logger.info("判决文书导入成功")
    else:
        logger.error("判决文书导入失败")
    
    # 导入指导意见
    logger.info("正在导入指导意见...")
    success = data_importer.import_guidelines(str(guidelines_file))
    if success:
        logger.info("指导意见导入成功")
    else:
        logger.error("指导意见导入失败")
    
    # 显示统计信息
    stats = data_importer.get_collection_stats()
    logger.info(f"知识库统计信息: {stats}")
    
    logger.info("外部数据导入完成!")

if __name__ == "__main__":
    main()