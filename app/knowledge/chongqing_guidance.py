"""
重庆本地劳动争议典型案例与指导意见。

只保留已经稳定、对办案有直接帮助的归纳结论，用于本地优先参考。
"""

from __future__ import annotations

from typing import Any, Dict, List


LOCAL_GUIDANCE: Dict[str, Dict[str, Any]] = {
    "labor_relation_fact_first": {
        "title": "新就业形态劳动关系认定坚持事实优先",
        "tags": ["劳动关系", "新就业形态", "平台用工", "主播", "网约车", "配送"],
        "summary": (
            "重庆高院和市人社局发布的新就业形态案例强调，不能只看合同名义，"
            "应结合工作规则、报酬结算、管理控制和组织从属性，先查用工事实再定关系。"
        ),
        "source": "重庆市人力资源和社会保障局：新就业形态劳动争议典型案例（三）",
        "url": "https://rlsbj.cq.gov.cn/zwxx_182/tzgg/202410/t20241021_13724147.html",
        "use_when": ["平台用工", "主播", "骑手", "经纪合同", "派单管理", "算法考核"],
    },
    "termination_reasonable_period": {
        "title": "解除劳动合同需在合理期间内行使",
        "tags": ["解除", "违纪", "刑事责任", "合理期间", "单方解除"],
        "summary": (
            "重庆高院案例提示，用人单位主张解除权不能无限期拖延；"
            "若多年后才以旧事由解除，通常难以获得支持。"
        ),
        "source": "重庆市高级人民法院劳动争议典型案例",
        "url": "https://www.thepaper.cn/newsDetail_forward_7198658",
        "use_when": ["违法解除", "事后追责", "多年后解除", "规章制度", "纪律处分"],
    },
    "job_transfer_reasonableness": {
        "title": "重庆市内调岗也要审查正当性和合理性",
        "tags": ["调岗", "工作地点", "旷工", "解除", "违法解除"],
        "summary": (
            "重庆高院典型案例认为，即便劳动合同写明工作地点为重庆市，"
            "用人单位跨区县大幅调整工作地点仍需说明生产经营必要性，"
            "否则以拒绝调岗、旷工解除可能构成违法解除。"
        ),
        "source": "重庆市高级人民法院第六批劳动争议十大典型案例",
        "url": "https://www.thepaper.cn/newsDetail_forward_7198658",
        "use_when": ["调岗", "工作地点", "渝北", "奉节", "旷工", "拒绝调岗"],
    },
    "wage_and_overtime_high_frequency": {
        "title": "工资、加班费、解除终止是重庆高频争议类型",
        "tags": ["工资", "加班费", "解除", "终止", "劳动报酬"],
        "summary": (
            "重庆人社局的公开宣讲和典型案例显示，工资报酬、解除终止和履行变更劳动合同 "
            "是本地高频争议，仲裁意见通常优先核对工资流水、考勤、解除通知和协商记录。"
        ),
        "source": "川渝劳动人事争议典型案例发布相关公开信息",
        "url": "https://m.thepaper.cn/newsDetail_forward_27226039",
        "use_when": ["拖欠工资", "加班费", "被辞退", "解除通知", "工资差额"],
    },
    "mediation_and_online_filing": {
        "title": "重庆支持线上调解与智慧仲裁",
        "tags": ["调解", "线上申请", "易简裁", "一站式"],
        "summary": (
            "重庆已形成线上调解、线上庭审和“易简裁”等便民流程，"
            "对案情清楚、金额明确的案件，先调解再仲裁通常更高效。"
        ),
        "source": "重庆荣昌区人民政府：重庆易简裁办理劳动争议",
        "url": "https://www.rongchang.gov.cn/zwxx/bmjz/202405/t20240522_13227233.html",
        "use_when": ["想先调解", "异地申请", "材料不全", "需要快速立案"],
    },
    "one_stop_mediation": {
        "title": "重庆新就业形态纠纷优先纳入一站式调解",
        "tags": ["新就业形态", "平台用工", "调解", "一站式", "诉调对接", "调裁衔接"],
        "summary": (
            "重庆市人社等部门推进新就业形态劳动纠纷一站式调解，"
            "强调把协商、调解、仲裁和审判衔接起来。平台用工案件除判断劳动关系外，"
            "还应同步评估是否适合先行调解和快速化解。"
        ),
        "source": "重庆市人力资源和社会保障局等：加强新就业形态劳动纠纷一站式调解工作实施方案",
        "url": "https://rlsbj.cq.gov.cn/zwxx_182/tzgg/202408/t20240801_13445840.html",
        "use_when": ["平台", "骑手", "主播", "网约车", "一站式调解", "先调解", "诉调对接"],
    },
    "one_stop_joint_center": {
        "title": "重庆多数仲裁机构已建设一站式联调中心",
        "tags": ["联调中心", "调解优先", "速裁", "仲裁", "立案"],
        "summary": (
            "重庆公开信息显示，多数仲裁机构已建设劳动人事争议一站式联调中心。"
            "对事实清楚、金额明确、证据集中的案件，应优先准备简明申请、金额明细和证据目录，"
            "再衔接调解、速裁或正式仲裁。"
        ),
        "source": "重庆市人民政府网：超80%仲裁机构建起一站式联调中心",
        "url": "https://www.cq.gov.cn/ywdt/zwhd/bmdt/202311/t20231101_12499145.html",
        "use_when": ["立案", "调解", "速裁", "工资", "补偿", "证据清楚", "小额"],
    },
    "scope_and_conditions": {
        "title": "重庆调解受理范围以法定劳动争议为前提",
        "tags": ["受理范围", "调解", "仲裁", "法定范围"],
        "summary": (
            "重庆官方调解服务明确要求属于法定劳动人事争议范围，且双方同意调解；"
            "因此，先确认是否属于劳动争议，再判断能否走重庆调解/仲裁渠道。"
        ),
        "source": "重庆市人民政府：新就业形态劳动纠纷一站式调解工作",
        "url": "https://www.cq.gov.cn/ywdt/zwhd/bmdt/202411/t20241113_13792606_wap.html",
        "use_when": ["是否受理", "是否属于劳动争议", "能否申请调解", "程序选择"],
    },
}


def select_relevant_guidance(query: str, case_type: str = "") -> List[Dict[str, Any]]:
    text = f"{query} {case_type}".lower()
    scored = []
    for item in LOCAL_GUIDANCE.values():
        score = 0
        for tag in item["tags"]:
            if tag.lower() in text:
                score += 2
        for marker in item["use_when"]:
            if marker.lower() in text:
                score += 1
        if score:
            scored.append((score, item))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in scored[:3]]
