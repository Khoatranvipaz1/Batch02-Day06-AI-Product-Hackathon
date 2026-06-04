from __future__ import annotations

from typing import Any

from codebase.chatbot_parser.openai_parser import OpenAIParserError, parse_user_query_with_gpt
from codebase.chatbot_parser.parser import parse_user_query

from .answerer import FinalAnswerError, build_template_answer, generate_final_answer_with_gpt
from .retriever import retrieve_items_for_task


def run_food_chatbot(
    user_message: str,
    *,
    task: dict[str, Any] | None = None,
    conversation_history: list[dict[str, str]] | None = None,
    data_dir: str | None = None,
    parse_mode: str = "api",
    answer_mode: str = "api",
    model: str | None = None,
    fallback_rules: bool = False,
    fallback_template: bool = False,
) -> dict[str, Any]:
    parsed_task = task or _parse_task(
        user_message,
        data_dir=data_dir,
        parse_mode=parse_mode,
        model=model,
        fallback_rules=fallback_rules,
        conversation_history=conversation_history,
    )
    retrieved_data = retrieve_items_for_task(parsed_task, data_dir=data_dir)
    answer = _answer(
        user_message,
        parsed_task,
        retrieved_data,
        conversation_history=conversation_history,
        answer_mode=answer_mode,
        model=model,
        fallback_template=fallback_template,
    )
    return {
        "answer": answer,
        "task": parsed_task,
        "retrieved_data": retrieved_data,
    }


def _parse_task(
    user_message: str,
    *,
    data_dir: str | None,
    parse_mode: str,
    model: str | None,
    fallback_rules: bool,
    conversation_history: list[dict[str, str]] | None,
) -> dict[str, Any]:
    if parse_mode == "rules":
        return parse_user_query(
            _contextual_user_message(user_message, conversation_history),
            data_dir=data_dir,
        )
    if parse_mode != "api":
        raise ValueError("parse_mode must be 'api' or 'rules'.")

    try:
        return parse_user_query_with_gpt(
            user_message,
            data_dir=data_dir,
            model=model,
            conversation_history=conversation_history,
        )
    except OpenAIParserError:
        if not fallback_rules:
            raise
        task = parse_user_query(
            _contextual_user_message(user_message, conversation_history),
            data_dir=data_dir,
        )
        task["parser"] = "offline_rules_fallback"
        return task


def _answer(
    user_message: str,
    task: dict[str, Any],
    retrieved_data: dict[str, Any],
    *,
    conversation_history: list[dict[str, str]] | None,
    answer_mode: str,
    model: str | None,
    fallback_template: bool,
) -> str:
    if answer_mode == "template":
        return build_template_answer(
            user_message,
            task,
            retrieved_data,
            conversation_history=conversation_history,
        )
    if answer_mode != "api":
        raise ValueError("answer_mode must be 'api' or 'template'.")

    try:
        return generate_final_answer_with_gpt(
            user_message,
            task,
            retrieved_data,
            model=model,
            conversation_history=conversation_history,
        )
    except FinalAnswerError:
        if not fallback_template:
            raise
        return build_template_answer(
            user_message,
            task,
            retrieved_data,
            conversation_history=conversation_history,
        )


def _contextual_user_message(
    user_message: str,
    conversation_history: list[dict[str, str]] | None,
) -> str:
    if not conversation_history:
        return user_message

    previous_user_messages = [
        message["content"]
        for message in conversation_history[-6:]
        if message.get("role") == "user" and message.get("content")
    ]
    if not previous_user_messages:
        return user_message

    context = " ".join(previous_user_messages[-3:])
    return f"{context}. {user_message}"
