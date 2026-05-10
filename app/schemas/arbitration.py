from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CaseAnalysisRequest(BaseModel):
    case_type: str
    facts: str
    evidence: List[str] = Field(default_factory=list)
    applicant_info: Dict[str, Any] = Field(default_factory=dict)
    salary: Optional[float] = None
    years: Optional[float] = None
    amount: Optional[float] = None
    district: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    evidence_quality: str = "一般"
    applicant_background: str = "普通员工"
    enable_opposition_review: bool = True


class CaseAnalysisResponse(BaseModel):
    case_type: str
    risk_level: str
    risk_factors: List[str]
    cost_estimate: Dict[str, float]
    success_probability: str
    probability_confidence: float
    legal_basis: List[str]
    case_similarity: List[Dict[str, Any]]
    recommendations: List[str]
    missing_info: Optional[List[str]] = None
    opposition_review: Optional[Dict[str, Any]] = None
    jurisdiction: Optional[Dict[str, Any]] = None
    limitation: Optional[Dict[str, Any]] = None
    claim_items: Optional[List[Dict[str, Any]]] = None
    evidence_checklist: Optional[List[Dict[str, Any]]] = None
    action_plan: Optional[List[str]] = None
    negotiation_points: Optional[List[str]] = None
    warnings: Optional[List[str]] = None
    local_reference: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    analysis: Optional[Dict[str, Any]] = None


class DocumentGenerationRequest(BaseModel):
    document_type: str
    case_data: Dict[str, Any]


class DocumentGenerationResponse(BaseModel):
    document_type: str
    content: str
    generated_at: str
    advice: Optional[str] = None
    document: Optional[Dict[str, Any]] = None


class DocumentValidationRequest(BaseModel):
    document_type: str
    case_data: Dict[str, Any]
    content: str


class DocumentValidationResponse(BaseModel):
    document_type: str
    is_valid: bool
    issues: List[str]
    warnings: List[str]
    suggestions: List[str]
    checked_at: str


class ArbitrationCostEstimate(BaseModel):
    arbitration_fee: float
    lawyer_fee: float
    other_costs: float
    total_cost: float
    cost_estimate: Optional[float] = None
    explanation: Optional[str] = None


class SuccessRatePrediction(BaseModel):
    success_probability: str
    probability_value: float
    confidence: float
    key_factors: List[str]
    success_rate: Optional[str] = None
    explanation: Optional[str] = None


class ClaimCalculationRequest(BaseModel):
    calculation_type: str
    salary: float = 0.0
    years: float = 0.0
    reason: str = ""
    hours: float = 0.0
    day_type: str = "平日"
    injury_level: Optional[int] = None


class ClaimCalculationResponse(BaseModel):
    calculation_type: str
    amount: float
    formula: str
    notes: List[str]


class IntakeChecklistRequest(BaseModel):
    case_type: str = "劳动纠纷"
    facts: str = ""
    evidence: List[str] = Field(default_factory=list)
    applicant_info: Dict[str, Any] = Field(default_factory=dict)


class IntakeChecklistResponse(BaseModel):
    missing_questions: List[str]
    evidence_checklist: List[Dict[str, Any]]
    jurisdiction: Dict[str, Any]
    limitation: Dict[str, Any]


class LocalReferenceResponse(BaseModel):
    query: str
    references: List[Dict[str, Any]]


class CaseWorkupResponse(BaseModel):
    analysis: CaseAnalysisResponse
    intake: IntakeChecklistResponse
    cost: ArbitrationCostEstimate
    success_prediction: SuccessRatePrediction
    local_references: List[Dict[str, Any]]
    suggested_documents: List[str]
    workflow_stage: str
    service_recommendation: Dict[str, Any]
    pipeline_status: List[Dict[str, Any]] = Field(default_factory=list)
