"""Modelos de dados para o Alfred."""

from pydantic import BaseModel, Field


class AssistantRequest(BaseModel):
    """Solicitação recebida pelo assistente."""
    
    message: str = Field(..., description="Mensagem do usuário")
    session_id: str = Field(..., description="ID da sessão para contexto")
    channel: str = Field(default="cli", description="Canal de entrada (cli, whatsapp)")
    output_format: str = Field(default="text", description="Formato de saída (text, json)")
    interactive_confirmation: bool = Field(default=True, description="Solicitar confirmação interativa")
    trace_enabled: bool = Field(default=True, description="Habilitar tracing")


class IntentDecision(BaseModel):
    """Decisão de classificação de intenção."""
    
    category: str = Field(..., description="Categoria da intenção")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confiança da classificação")
    rationale_code: str = Field(..., description="Código de justificativa")
    required_clarification: str | None = Field(default=None, description="Informação necessária")
    simulated_tool_name: str | None = Field(default=None, description="Nome da tool simulada")
    risk_labels: list[str] = Field(default_factory=list, description="Rótulos de risco")


class SafetyDecision(BaseModel):
    """Decisão de segurança."""
    
    status: str = Field(..., description="Status (ALLOW, CONFIRM, BLOCK)")
    reason_code: str = Field(..., description="Código de justificativa")
    human_message: str = Field(..., description="Mensagem para o usuário")


class AssistantResponse(BaseModel):
    """Resposta do assistente."""
    
    text: str = Field(..., description="Resposta em texto")
    category: str = Field(..., description="Categoria da resposta")
    safety_status: str = Field(..., description="Status de segurança")
    session_id: str = Field(..., description="ID da sessão")
    metadata: dict = Field(default_factory=dict, description="Metadados adicionais")
    json_payload: dict | None = Field(default=None, description="Payload JSON opcional")
