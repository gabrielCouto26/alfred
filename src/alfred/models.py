"""Modelos de dados para o Alfred."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class IntentCategory(str, Enum):
    """Categorias de intenção do Alfred."""

    CHITCHAT = "CHITCHAT"
    CLOUD_TASK = "CLOUD_TASK"
    LOCAL_TASK = "LOCAL_TASK"
    AMBIGUOUS = "AMBIGUOUS"
    BLOCKED = "BLOCKED"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"


class SafetyStatus(str, Enum):
    """Status de segurança das decisões."""

    ALLOW = "ALLOW"
    CONFIRM = "CONFIRM"
    BLOCK = "BLOCK"


class OutputFormat(str, Enum):
    """Formatos de saída suportados."""

    TEXT = "text"
    JSON = "json"


class Channel(str, Enum):
    """Canais de entrada suportados."""

    CLI = "cli"
    WHATSAPP = "whatsapp"


class AssistantRequest(BaseModel):
    """Solicitação recebida pelo assistente."""

    message: str = Field(..., description="Mensagem do usuário")
    session_id: str = Field(..., description="ID da sessão para contexto")
    channel: Channel = Field(default=Channel.CLI, description="Canal de entrada")
    output_format: OutputFormat = Field(default=OutputFormat.TEXT, description="Formato de saída")
    interactive_confirmation: bool = Field(default=True, description="Solicitar confirmação interativa")
    trace_enabled: bool = Field(default=True, description="Habilitar tracing")


class IntentDecision(BaseModel):
    """Decisão de classificação de intenção."""

    category: IntentCategory = Field(..., description="Categoria da intenção")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confiança da classificação")
    rationale_code: str = Field(..., description="Código de justificativa")
    required_clarification: str | None = Field(default=None, description="Informação necessária")
    simulated_tool_name: str | None = Field(default=None, description="Nome da tool simulada")
    risk_labels: list[str] = Field(default_factory=list, description="Rótulos de risco")


class SafetyDecision(BaseModel):
    """Decisão de segurança."""

    status: SafetyStatus = Field(..., description="Status")
    reason_code: str = Field(..., description="Código de justificativa")
    human_message: str = Field(..., description="Mensagem para o usuário")


class AssistantResponse(BaseModel):
    """Resposta do assistente."""

    text: str = Field(..., description="Resposta em texto")
    category: IntentCategory = Field(..., description="Categoria da resposta")
    safety_status: SafetyStatus = Field(..., description="Status de segurança")
    session_id: str = Field(..., description="ID da sessão")
    metadata: dict = Field(default_factory=dict, description="Metadados adicionais")
    json_payload: dict | None = Field(default=None, description="Payload JSON opcional")


class SessionTurn(BaseModel):
    """Turno de sessão com resumo e metadados."""

    created_at: datetime = Field(..., description="Timestamp de criação")
    expires_at: datetime = Field(..., description="Timestamp de expiração")
    category: IntentCategory = Field(..., description="Categoria da intenção")
    summary: str = Field(..., description="Resumo da interação")
    decision_hash: str = Field(..., description="Hash da decisão")
    category_label: str | None = Field(default=None, description="Label da categoria")
    risk_labels: list[str] = Field(default_factory=list, description="Rótulos de risco")


class SessionContext(BaseModel):
    """Contexto de sessão com turnos."""

    session_id: str = Field(..., description="ID da sessão")
    turns: list[SessionTurn] = Field(default_factory=list, description="Turnos da sessão")
    created_at: datetime = Field(..., description="Timestamp de criação")
    expires_at: datetime = Field(..., description="Timestamp de expiração")
    version: str = Field(default="1.0", description="Versão do schema")
    last_message_at: datetime | None = Field(default=None, description="Última mensagem")


class SessionStoreConfig(BaseModel):
    """Configuração do armazenamento de sessão."""

    ttl_seconds: int = Field(default=7200, description="Tempo de vida da sessão em segundos (2h)")
    max_turns: int = Field(default=10, description="Número máximo de turnos por sessão")
    storage_path: str | None = Field(default=None, description="Caminho para persistência")


class IntentRequest(BaseModel):
    """Solicitação de classificação de intenção."""

    message: str = Field(..., description="Mensagem do usuário")
    session_id: str = Field(..., description="ID da sessão")
    channel: Channel = Field(..., description="Canal de entrada")
    history: list[str] = Field(default_factory=list, description="Histórico da conversa")


class IntentResponse(BaseModel):
    """Resposta da classificação de intenção."""

    category: IntentCategory = Field(..., description="Categoria classificada")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confiança")
    rationale_code: str = Field(..., description="Código de justificativa")
    requires_clarification: bool = Field(default=False, description="Requer clarificação")
    simulated_tool: str | None = Field(default=None, description="Tool simulada")
    risk_labels: list[str] = Field(default_factory=list, description="Rótulos de risco")
