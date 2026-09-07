"""Política de segurança determinística para o Alfred."""

from alfred.contracts import SafetyPolicy
from alfred.models import (
    AssistantRequest,
    IntentDecision,
    IntentCategory,
    SafetyDecision,
    SafetyStatus,
)


class DeterministicSafetyPolicy(SafetyPolicy):
    """Política de segurança determinística com regras pré-definidas."""

    _patterns_block = [
        "rm -rf",
        "rm -rf /",
        "sudo",
        "chmod 777",
        "chown",
        "dd if=",
        "mkfs",
        "格式化",
        "format ",
        ">",
        ">>",
    ]

    patterns_confirm_sensitive = [
        "database",
        "banco de dados",
        "delete database",
        "drop table",
        "export ",
        "backup ",
        "password",
        "senha",
        "api key",
        "chave ",
        "credencial",
        "private",
        "privado",
        "confidential",
        "confidencial",
        "financeiro",
        "finance",
        "payment",
        "pagamento",
        "transfer",
        "transferir",
        "withdraw",
        "sacar",
        "legal",
        "law",
        "lawyer",
        "advogado",
        "contrato",
        "contract",
        "nudity",
        "nude",
        "nua",
        "porn",
        "pornografia",
        "violence",
        "violência",
        "kill",
        "matar",
        "attack",
        "atacar",
        "hacker",
        "injetar",
        "sql injection",
        "xss",
        "cross-site",
    ]

    _patterns_dangerous_commands = [
        "rm ",
        "rmdir ",
        "mv ",
        "cp ",
        "touch ",
        "chmod ",
        "chown ",
        "ln ",
        "mktemp ",
        "mkdir ",
        "curl ",
        "wget ",
        "python ",
        "node ",
        "bash ",
        "sh ",
        "zsh ",
        "eval ",
        "exec ",
        "system ",
        "os.system ",
        "subprocess ",
        "popen ",
        "shell",
        "cmd.exe",
        "/bin/",
        "/etc/",
        "/usr/",
        "/root",
        "/home/",
        ".ssh/",
        ".env",
        "config.json",
        "credentials",
        "passwords",
    ]

    def evaluate(
        self, decision: IntentDecision, request: AssistantRequest
    ) -> SafetyDecision:
        """Avaliar decisão e aplicar política de segurança."""
        message_lower = request.message.lower()

        for pattern in self._patterns_block:
            if pattern.lower() in message_lower:
                return SafetyDecision(
                    status=SafetyStatus.BLOCK,
                    reason_code="blocked_dangerous_command",
                    human_message="Bloqueado: comando potencialmente perigoso",
                )

        for pattern in self._patterns_dangerous_commands:
            if pattern.lower() in message_lower:
                return SafetyDecision(
                    status=SafetyStatus.CONFIRM,
                    reason_code="dangerous_command_detected",
                    human_message="Confirmar execução de comando perigoso",
                )

        for pattern in self.patterns_confirm_sensitive:
            if pattern.lower() in message_lower:
                return SafetyDecision(
                    status=SafetyStatus.CONFIRM,
                    reason_code="sensitive_operation",
                    human_message="Operação sensível requer confirmação",
                )

        if decision.risk_labels:
            risk_categories = {
                "destructive": SafetyStatus.BLOCK,
                "private": SafetyStatus.CONFIRM,
                "financial": SafetyStatus.CONFIRM,
                "legal": SafetyStatus.CONFIRM,
                "credentials": SafetyStatus.BLOCK,
                "external": SafetyStatus.CONFIRM,
            }
            for label in decision.risk_labels:
                if label.lower() in risk_categories:
                    status = risk_categories[label.lower()]
                    reason_map = {
                        "destructive": "destructive_operation",
                        "private": "private_data",
                        "financial": "financial_operation",
                        "legal": "legal_operation",
                        "credentials": "credentials_exposure",
                        "external": "external_dependency",
                    }
                    return SafetyDecision(
                        status=status,
                        reason_code=reason_map[label.lower()],
                        human_message=self._get_risk_message(label.lower()),
                    )

        if decision.category == IntentCategory.BLOCKED:
            return SafetyDecision(
                status=SafetyStatus.BLOCK,
                reason_code="blocked_by_router",
                human_message="Solicitação bloqueada pelo classificador de intenção.",
            )

        if decision.category == IntentCategory.OUT_OF_SCOPE:
            return SafetyDecision(
                status=SafetyStatus.BLOCK,
                reason_code="out_of_scope",
                human_message="Fora do escopo da versão atual.",
            )

        return SafetyDecision(
            status=SafetyStatus.ALLOW,
            reason_code="no_risk_detected",
            human_message="Solicitação permitida.",
        )

    def _get_risk_message(self, risk_type: str) -> str:
        """Obter mensagem humana curta para tipo de risco."""
        messages = {
            "destructive": "Bloqueado: operação destrutiva detectada.",
            "private": "Operação sensível requer confirmação.",
            "financial": "Operação financeira requer confirmação.",
            "legal": "Operação legal requer confirmação.",
            "credentials": "Bloqueado: exposição de credenciais detectada.",
            "external": "Operação com dependência externa requer confirmação.",
        }
        return messages.get(risk_type, "Operação sensível requer confirmação.")
