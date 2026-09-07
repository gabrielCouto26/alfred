"""Adaptador CLI do Alfred."""

import os
import sys
import json
from typing import Annotated

import typer

from alfred.models import AssistantRequest


app = typer.Typer(
    name="alfred",
    help="Assistente pessoal Alfred - orquestração de IA para CLI e WhatsApp",
    no_args_is_help=True,
)


def _load_session_context(session_id: str) -> dict:
    """Carregar contexto de sessão (placeholder)."""
    return {"session_id": session_id, "messages": []}


def _save_session_context(session_id: str, context: dict) -> None:
    """Salvar contexto de sessão (placeholder)."""
    pass


@app.command()
def main(
    message: Annotated[
        str,
        typer.Argument(..., help="Mensagem do usuário")
    ] = "",
    session: Annotated[
        str,
        typer.Option("--session", "-s", help="ID da sessão para contexto")
    ] = "default-cli-session",
    json_output: Annotated[
        bool,
        typer.Option("--json", "-j", help="Retornar saída em formato JSON")
    ] = False,
    no_trace: Annotated[
        bool,
        typer.Option("--no-trace", help="Desabilitar tracing")
    ] = False,
) -> int:
    """Processar uma solicitação única do usuário."""
    
    if not message:
        if json_output:
            result = {
                "error": "INPUT_ERROR",
                "message": "Mensagem é obrigatória",
                "session_id": session
            }
            print(json.dumps(result))
        else:
            typer.echo("Erro: mensagem é obrigatória.", err=True)
            typer.echo("Uso: alfred <mensagem> [--session ID] [--json] [--no-trace]", err=True)
        return 1
    
    try:
        request = AssistantRequest(
            message=message,
            session_id=session,
            channel="cli",
            output_format="json" if json_output else "text",
            interactive_confirmation=True,
            trace_enabled=not no_trace
        )
        
        context = _load_session_context(session)
        
        response = {
            "text": "Alfred: Recebi sua solicitação. Estou processando...",
            "category": "CHITCHAT",
            "safety_status": "ALLOW",
            "session_id": session,
            "metadata": {
                "input_format": "text",
                "trace_enabled": not no_trace
            }
        }
        
        _save_session_context(session, context)
        
        if json_output:
            print(json.dumps(response))
        else:
            typer.echo(response["text"])
        
        return 0
        
    except Exception as exc:
        if json_output:
            result = {
                "error": "INTERNAL_ERROR",
                "message": str(exc),
                "session_id": session
            }
            print(json.dumps(result))
        else:
            typer.echo(f"Erro interno: {exc}", err=True)
        return 2


if __name__ == "__main__":
    app()
