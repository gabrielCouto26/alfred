"""Adaptador CLI do Alfred."""

import json
import sys
from typing import Annotated

import typer

from alfred.app import create_assistant_service
from alfred.exit_codes import (
    EXIT_INPUT_ERROR,
    EXIT_INTERNAL_ERROR,
    EXIT_SUCCESS,
)
from alfred.models import AssistantRequest, AssistantResponse, Channel, OutputFormat

app = typer.Typer(
    name="alfred",
    help="Assistente pessoal Alfred - orquestração de IA para CLI e WhatsApp",
    no_args_is_help=True,
)


def _render_text(response: AssistantResponse) -> None:
    """Imprimir respuesta en texto legible."""
    typer.echo(response.text)


def _render_json(response: AssistantResponse) -> None:
    """Imprimir respuesta en JSON parseable."""
    payload = response.model_dump(mode="json")
    print(json.dumps(payload, ensure_ascii=False))


def _render_error_json(session_id: str, code: str, message: str) -> None:
    """Imprimir error estructurado en JSON."""
    payload = {"error": code, "message": message, "session_id": session_id}
    print(json.dumps(payload, ensure_ascii=False))


@app.command()
def main(
    message: Annotated[
        str,
        typer.Argument(..., help="Mensagem del usuario"),
    ] = "",
    session: Annotated[
        str,
        typer.Option("--session", "-s", help="ID de la sesión para contexto"),
    ] = "default-cli-session",
    json_output: Annotated[
        bool,
        typer.Option("--json", "-j", help="Retornar salida en formato JSON"),
    ] = False,
    no_trace: Annotated[
        bool,
        typer.Option("--no-trace", help="Deshabilitar tracing"),
    ] = False,
) -> int:
    """Procesar una solicitud única del usuario."""
    if not message:
        if json_output:
            _render_error_json(session, "INPUT_ERROR", "Mensaje es obligatorio")
        else:
            typer.echo("Error: mensaje es obligatorio.", err=True)
            typer.echo(
                "Uso: alfred <mensaje> [--session ID] [--json] [--no-trace]",
                err=True,
            )
        raise typer.Exit(EXIT_INPUT_ERROR)

    try:
        request = AssistantRequest(
            message=message,
            session_id=session,
            channel=Channel.CLI,
            output_format=OutputFormat.JSON if json_output else OutputFormat.TEXT,
            interactive_confirmation=not json_output,
            trace_enabled=not no_trace,
        )

        service = create_assistant_service()
        response = service.handle(request)

        if json_output:
            _render_json(response)
        else:
            _render_text(response)

        raise typer.Exit(EXIT_SUCCESS)

    except typer.Exit:
        raise
    except Exception as exc:
        if json_output:
            _render_error_json(session, "INTERNAL_ERROR", str(exc))
        else:
            typer.echo(f"Error interno: {exc}", err=True)
        raise typer.Exit(EXIT_INTERNAL_ERROR)


if __name__ == "__main__":
    sys.exit(app())
