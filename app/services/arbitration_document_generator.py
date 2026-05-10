#!/usr/bin/env python3
"""
劳动仲裁文书生成器
负责生成各种劳动仲裁文书，包括仲裁申请书、答辩书、证据清单和代理词
"""

from typing import Dict, List, Any
from enum import Enum


class DocumentType(str, Enum):
    """文书类型枚举"""
    ARBITRATION_APPLICATION = "仲裁申请书"
    MEDIATION_APPLICATION = "庭前调解申请书"
    DEFENSE_RESPONSE = "答辩书"
    EVIDENCE_LIST = "证据清单"
    PROXY_LETTER = "代理词"


class ArbitrationDocumentGenerator:
    """
    劳动仲裁文书生成器
    """
    
    def __init__(self):
        pass

    def _applicant_info(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        return case_data.get("applicant_info") or {}

    def _money(self, value: Any) -> str:
        try:
            amount = float(value or 0)
        except (TypeError, ValueError):
            amount = 0
        return f"{amount:,.2f}".replace(",", "") if amount else "______"

    def _build_claim_requests(self, case_data: Dict[str, Any]) -> List[str]:
        text = f"{case_data.get('case_type', '')} {case_data.get('facts', '')}"
        salary = case_data.get("salary") or self._applicant_info(case_data).get("salary")
        amount = case_data.get("amount")
        requests: List[str] = []

        if any(k in text for k in ["工资", "拖欠", "劳动报酬"]):
            requests.append(f"请求裁决被申请人支付拖欠工资人民币{self._money(amount)}元。")
        if "加班" in text:
            requests.append("请求裁决被申请人支付延时、休息日或法定节假日加班工资，具体金额以工资基数、考勤和庭审核算为准。")
        if any(k in text for k in ["辞退", "违法解除", "解除"]):
            requests.append("请求裁决被申请人支付违法解除劳动合同赔偿金或经济补偿金。")
        if "未签" in text or "没签" in text:
            requests.append("请求裁决被申请人支付未签书面劳动合同二倍工资差额。")
        if "工伤" in text or "受伤" in text:
            requests.append("请求裁决被申请人依法承担工伤待遇相关费用。")

        if not requests:
            requests.append("请求依法确认双方劳动关系并支持申请人的劳动争议请求。")
        if salary:
            requests.append(f"请求以月工资人民币{self._money(salary)}元作为相关项目的计算基数。")
        return requests

    def _build_evidence_rows(self, case_data: Dict[str, Any]) -> List[Dict[str, str]]:
        evidence = [str(item).strip() for item in case_data.get("evidence") or [] if str(item).strip()]
        rows = []
        defaults = {
            "劳动合同": "证明双方存在劳动关系、岗位、工资及合同期限。",
            "工资流水": "证明工资标准、支付周期及欠付事实。",
            "聊天记录": "证明工作安排、催款沟通或解除过程。",
            "考勤记录": "证明出勤、加班时长及排班情况。",
            "解除通知": "证明用人单位解除劳动关系的时间和理由。",
        }
        for item in evidence:
            purpose = next((text for key, text in defaults.items() if key in item), "证明与本案争议相关的事实。")
            rows.append({"name": item, "purpose": purpose})
        if not rows:
            rows = [{"name": "待补充证据", "purpose": "请补充劳动合同、工资流水、聊天记录、考勤或解除通知等材料。"}]
        return rows
    
    async def generate_arbitration_document(
        self, 
        document_type: DocumentType, 
        case_data: Dict[str, Any]
    ) -> str:
        """
        生成劳动仲裁文书
        
        Args:
            document_type: 文书类型
            case_data: 案件数据
            
        Returns:
            生成的文书内容
        """
        # 根据文书类型选择不同的生成策略
        if document_type == DocumentType.ARBITRATION_APPLICATION:
            return await self._generate_application(case_data)
        elif document_type == DocumentType.MEDIATION_APPLICATION:
            return await self._generate_mediation_application(case_data)
        elif document_type == DocumentType.DEFENSE_RESPONSE:
            return await self._generate_defense_response(case_data)
        elif document_type == DocumentType.EVIDENCE_LIST:
            return await self._generate_evidence_list(case_data)
        elif document_type == DocumentType.PROXY_LETTER:
            return await self._generate_proxy_letter(case_data)
        else:
            raise ValueError(f"不支持的文书类型：{document_type}")
    
    async def _generate_application(self, case_data: Dict[str, Any]) -> str:
        """
        生成仲裁申请书 - 使用内置模板
        """
        case_type = case_data.get('case_type', '劳动纠纷')
        facts = case_data.get('facts', '未提供')
        applicant_info = self._applicant_info(case_data)
        applicant_name = applicant_info.get('name', '申请人')
        respondent_name = applicant_info.get('employer_name', '被申请人')
        respondent_address = applicant_info.get("employer_address") or applicant_info.get("workplace") or "____________________________________________"
        phone = case_data.get("contact_phone") or applicant_info.get("phone") or "________________________________________"
        requests = "\n".join(f"{idx}. {item}" for idx, item in enumerate(self._build_claim_requests(case_data), 1))
        evidence_names = "、".join(row["name"] for row in self._build_evidence_rows(case_data))
        
        return f"""劳动仲裁申请书

申请人：{applicant_name}
性别：______ 民族：______ 出生日期：______年______月______日
身份证号：________________________________________
住址：____________________________________________
联系电话：{phone}

被申请人：{respondent_name}
法定代表人：______ 职务：______
地址：{respondent_address}
联系电话：________________________________________

【仲裁请求】

{requests}

以上请求金额共计人民币______元。

【事实和理由】

{facts if facts else '请在此处详细描述案件事实经过，包括入职时间、工作岗位、工资标准、争议发生的时间、地点、原因及经过等。'}

现有主要证据包括：{evidence_names}。申请人认为，被申请人的上述行为违反《中华人民共和国劳动法》《中华人民共和国劳动合同法》《中华人民共和国劳动争议调解仲裁法》等相关规定，侵害了申请人的合法权益。为维护申请人的合法权益，特向贵委提出仲裁申请，恳请贵委依法查明事实，支持申请人的仲裁请求。

此致
重庆市______区劳动人事争议仲裁委员会

申请人（签名）：____________
______年______月______日

【附项】

1. 本申请书副本______份；
2. 证据材料清单及副本______份；
3. 申请人身份证复印件______份；
4. 其他证据材料______份。

【相关法律条款】
• 《中华人民共和国劳动法》第七十九条：劳动争议发生后，当事人可以向本单位劳动争议调解委员会申请调解；调解不成，当事人一方要求仲裁的，可以向劳动争议仲裁委员会申请仲裁。
• 《中华人民共和国劳动合同法》第四十六条：有下列情形之一的，用人单位应当向劳动者支付经济补偿……
• 《中华人民共和国劳动合同法》第四十七条：经济补偿按劳动者在本单位工作的年限，每满一年支付一个月工资的标准向劳动者支付。"""

    async def _generate_mediation_application(self, case_data: Dict[str, Any]) -> str:
        """生成庭前调解申请书。"""
        facts = case_data.get("facts", "")
        applicant_info = self._applicant_info(case_data)
        applicant_name = applicant_info.get("name", "申请人")
        respondent_name = applicant_info.get("employer_name", "被申请人")
        phone = case_data.get("contact_phone") or applicant_info.get("phone") or "________________________________________"
        requests = "\n".join(f"{idx}. {item}" for idx, item in enumerate(self._build_claim_requests(case_data), 1))
        evidence_names = "、".join(row["name"] for row in self._build_evidence_rows(case_data))

        return f"""庭前调解申请书

申请人：{applicant_name}
联系电话：{phone}

被申请人：{respondent_name}
地址：{applicant_info.get("employer_address") or applicant_info.get("workplace") or "____________________________________________"}

申请事项：

申请贵委在正式开庭前组织双方进行调解，并围绕以下事项促成双方达成书面调解协议：

{requests}

事实简述：

{facts if facts else "请补充入职时间、岗位、工资标准、争议发生时间、沟通过程和目前诉求。"}

现有材料：

{evidence_names}

调解方案建议：

1. 请求被申请人在明确期限内一次性或分期履行给付义务；
2. 如双方就金额或部分请求存在争议，可先确认无争议部分并约定支付时间；
3. 调解协议应写明支付金额、支付期限、支付方式、违约后果及双方后续权利义务。

申请理由：

为节约双方时间和维权成本，避免争议扩大，申请人愿在事实清楚、权利义务明确的基础上先行调解。若调解不成，申请人仍保留依法继续申请仲裁审理的权利。

此致
重庆市______区劳动人事争议仲裁委员会

申请人（签名）：____________
______年______月______日

【相关法律条款】
• 《中华人民共和国劳动争议调解仲裁法》第五条：发生劳动争议，当事人不愿协商、协商不成或者达成和解协议后不履行的，可以向调解组织申请调解。
• 《中华人民共和国劳动争议调解仲裁法》第四十二条：仲裁庭在作出裁决前，应当先行调解。"""
    
    async def _generate_defense_response(self, case_data: Dict[str, Any]) -> str:
        """
        生成答辩书 - 使用内置模板
        """
        facts = case_data.get('facts', '未提供')
        respondent_name = case_data.get('applicant_info', {}).get('employer_name', '被申请人')
        
        return f"""劳动仲裁答辩书

答辩人（被申请人）：{respondent_name}
法定代表人：______ 职务：______
地址：____________________________________________
联系电话：________________________________________

因申请人与答辩人劳动争议一案，现针对申请人的仲裁申请，提出如下答辩意见：

【答辩请求】

1. 请求驳回申请人的全部仲裁请求；
2. 本案仲裁费用由申请人承担。

【事实和理由】

{facts if facts else '请在此处详细陈述答辩人对案件事实的意见和反驳理由。'}

综上所述，申请人的仲裁请求缺乏事实和法律依据，恳请贵委依法驳回申请人的全部仲裁请求，维护答辩人的合法权益。

此致
重庆市______区劳动人事争议仲裁委员会

答辩人（盖章）：____________
法定代表人（签名）：____________
______年______月______日

【附项】

1. 本答辩书副本______份；
2. 证据材料清单及副本______份；
3. 营业执照复印件______份；
4. 法定代表人身份证明______份。

【相关法律条款】
• 《中华人民共和国劳动争议调解仲裁法》第六条：发生劳动争议，当事人对自己提出的主张，有责任提供证据。
• 《中华人民共和国劳动合同法》第三十九条：劳动者有下列情形之一的，用人单位可以解除劳动合同……"""
    
    async def _generate_evidence_list(self, case_data: Dict[str, Any]) -> str:
        """
        生成证据清单 - 使用内置模板
        """
        case_type = case_data.get('case_type', '劳动纠纷')
        rows = self._build_evidence_rows(case_data)
        evidence_table = "\n".join(
            f"| {idx} | {row['name']} | {row['purpose']} | ____ | □原件 □复印件 |"
            for idx, row in enumerate(rows, 1)
        )
        
        return f"""证据清单

案号：〔20____〕____号
申请人：________________
被申请人：________________

就申请人与被申请人 {case_type} 一案，申请人现向贵委提交以下证据材料，请予核查：

【证据清单】

| 序号 | 证据名称 | 证明内容 | 页码 | 原件/复印件 |
|------|----------|----------|------|-------------|
{evidence_table}

【证据说明】

1. 以上证据共____页，分为____组；
2. 所有复印件均与原件核对无误，愿在庭审时出示原件供核对；
3. 证据____至证据____为新增证据，说明：________________________。

此致
重庆市______区劳动人事争议仲裁委员会

提交人（签名）：____________
______年______月______日

【相关法律条款】
• 《中华人民共和国劳动争议调解仲裁法》第六条：发生劳动争议，当事人对自己提出的主张，有责任提供证据。
• 《最高人民法院关于审理劳动争议案件适用法律问题的解释（一）》第四十四条：因用人单位作出的开除、除名、辞退、解除劳动合同、减少劳动报酬、计算劳动者工作年限等决定而发生的劳动争议，用人单位负举证责任。"""
    
    async def _generate_proxy_letter(self, case_data: Dict[str, Any]) -> str:
        """
        生成代理词 - 使用内置模板
        """
        case_type = case_data.get('case_type', '劳动纠纷')
        facts = case_data.get('facts', '未提供')
        
        return f"""代理词

审判长、审判员（或仲裁员）：

______律师事务所接受本案______（原告/被告/申请人/被申请人）的委托，指派我作为其诉讼代理人参与其与______（对方当事人）{case_type}一案的审理活动。现结合庭审查明的事实和相关证据，发表如下代理意见：

【案件基本情况】

{facts if facts else '请在此处简要描述案件的基本情况和争议焦点。'}

【主要代理意见】

一、关于案件事实方面

（请在此处详细阐述对案件事实的认定意见，结合证据进行分析论证。）

二、关于法律适用方面

（请在此处阐述适用的法律法规及司法解释，分析法律适用问题。）

三、关于责任承担方面

（请在此处分析各方当事人的责任承担问题。）

四、其他需要说明的问题

（请在此处补充其他需要说明的事项。）

【结论】

综上所述，代理人认为：（请在此处总结核心观点和处理建议。）

恳请贵委（院）充分考虑上述代理意见，依法作出公正裁决（判决）。

此致
重庆市______区劳动人事争议仲裁委员会

代理人：____________
______律师事务所
______年______月______日

【相关法律条款】
• 《中华人民共和国劳动法》第七十八条：解决劳动争议，应当根据合法、公正、及时处理的原则，依法维护劳动争议当事人的合法权益。
• 《中华人民共和国劳动合同法》第四条：用人单位应当依法建立和完善劳动规章制度，保障劳动者享有劳动权利、履行劳动义务。"""
