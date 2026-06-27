"""Pydantic models for Wellness OS modules: members, consultations, AI reports, etc."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class MemberCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    gender: Optional[str] = None
    age: Optional[int] = Field(None, ge=0, le=150)
    country: Optional[str] = Field(None, max_length=100)
    preferred_language: str = Field(default="English")
    contact_info: Optional[str] = None
    notes: Optional[str] = None


class MemberUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    gender: Optional[str] = None
    age: Optional[int] = Field(None, ge=0, le=150)
    country: Optional[str] = Field(None, max_length=100)
    preferred_language: Optional[str] = None
    contact_info: Optional[str] = None
    notes: Optional[str] = None


class MemberResponse(BaseModel):
    id: int
    name: str
    gender: Optional[str] = None
    age: Optional[int] = None
    country: Optional[str] = None
    preferred_language: str
    contact_info: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class MemberListResponse(BaseModel):
    items: list[MemberResponse]
    total: int
    limit: int
    offset: int


class ConsultationCreate(BaseModel):
    member_id: int
    consultation_type: Optional[str] = None
    main_concern: Optional[str] = None
    questionnaire_data: Optional[Any] = None
    notes: Optional[str] = None


class ConsultationResponse(BaseModel):
    id: int
    member_id: int
    consultation_type: Optional[str] = None
    main_concern: Optional[str] = None
    questionnaire_data: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ConsultationListResponse(BaseModel):
    items: list[ConsultationResponse]
    total: int
    limit: int
    offset: int


class AIReportGenerateRequest(BaseModel):
    member_id: int
    consultation_id: Optional[int] = None


class AIReportResponse(BaseModel):
    id: int
    member_id: int
    consultation_id: Optional[int] = None
    summary: Optional[str] = None
    risk_level: Optional[str] = None
    key_findings: Optional[Any] = None
    recommendations: Optional[Any] = None
    model_used: Optional[str] = None
    created_at: datetime
    model_config = {"from_attributes": True}


class AIReportListResponse(BaseModel):
    items: list[AIReportResponse]
    total: int
    limit: int
    offset: int


class HealingPlanCreate(BaseModel):
    member_id: int
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    plan_items: Optional[Any] = None
    status: str = Field(default="active")


class HealingPlanUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    plan_items: Optional[Any] = None
    status: Optional[str] = None


class HealingPlanResponse(BaseModel):
    id: int
    member_id: int
    title: str
    description: Optional[str] = None
    plan_items: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class HealingPlanListResponse(BaseModel):
    items: list[HealingPlanResponse]
    total: int
    limit: int
    offset: int


class CommunityCaseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    category: Optional[str] = None
    anonymized_summary: Optional[str] = None
    healing_approach: Optional[str] = None
    outcome: Optional[str] = None
    language: str = Field(default="English")
    is_public: bool = False


class CommunityCaseResponse(BaseModel):
    id: int
    title: str
    category: Optional[str] = None
    anonymized_summary: Optional[str] = None
    healing_approach: Optional[str] = None
    outcome: Optional[str] = None
    language: str
    is_public: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CommunityCaseListResponse(BaseModel):
    items: list[CommunityCaseResponse]
    total: int
    limit: int
    offset: int


class DashboardSummaryResponse(BaseModel):
    total_members: int
    total_consultations: int
    total_ai_reports: int
    total_healing_plans: int
    total_community_cases: int
    recent_members: list[MemberResponse]
    recent_consultations: list[ConsultationResponse]
