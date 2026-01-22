from __future__ import annotations

from dataclasses import dataclass, field
import os
from typing import Dict, List, Optional

from anthropic import Anthropic, AuthenticationError, PermissionDeniedError
from colorama import Fore, Style, init as colorama_init
from dotenv import load_dotenv
from openai import OpenAI


Message = Dict[str, str]


def create_openai_client(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
) -> OpenAI:
    resolved_api_key = api_key or os.getenv("OPENAI_API_KEY")
    resolved_base_url = base_url or os.getenv("OPENAI_BASE_URL")
    if resolved_base_url:
        return OpenAI(api_key=resolved_api_key, base_url=resolved_base_url)
    return OpenAI(api_key=resolved_api_key)


def create_anthropic_client(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
) -> Anthropic:
    resolved_api_key = api_key or os.getenv("OPENAI_API_KEY")
    resolved_base_url = base_url or os.getenv("ANTHROPIC_BASE_URL")
    if resolved_base_url:
        return Anthropic(api_key=resolved_api_key, base_url=resolved_base_url)
    return Anthropic(api_key=resolved_api_key)


def add_message(history: List[Message], role: str, content: str) -> None:
    history.append({"role": role, "content": content})


def chat_once_openai(
    client: OpenAI,
    history: List[Message],
    user_message: str,
    model: str = "gpt-4o",
) -> str:
    add_message(history, "user", user_message)
    response = client.chat.completions.create(model=model, messages=history)
    assistant_message = response.choices[0].message.content or ""
    add_message(history, "assistant", assistant_message)
    return assistant_message


def chat_once_anthropic(
    client: Anthropic,
    history: List[Message],
    user_message: str,
    model: str = "claude-sonnet-4-5-20250929",
    system_prompt: Optional[str] = None,
) -> str:
    add_message(history, "user", user_message)
    messages = [msg for msg in history if msg["role"] != "system"]
    try:
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            messages=messages,
            system=system_prompt,
        )
    except (PermissionDeniedError, AuthenticationError) as exc:
        raise RuntimeError(
            "Claude не принял ключ. Убедись, что ключ подходит для Anthropic "
            "или выбери обычный режим (OpenAI)."
        ) from exc
    assistant_message = "".join(
        block.text for block in response.content if block.type == "text"
    )
    add_message(history, "assistant", assistant_message)
    return assistant_message


@dataclass
class ChatSession:
    provider: str
    model: str
    openai_client: Optional[OpenAI] = None
    anthropic_client: Optional[Anthropic] = None
    history: List[Message] = field(default_factory=list)
    system_prompt: Optional[str] = None

    def system(self, content: str) -> None:
        self.system_prompt = content
        add_message(self.history, "system", content)

    def user(self, content: str) -> str:
        if self.provider == "anthropic":
            if not self.anthropic_client:
                raise RuntimeError("Anthropic client is not initialized.")
            return chat_once_anthropic(
                self.anthropic_client,
                self.history,
                content,
                model=self.model,
                system_prompt=self.system_prompt,
            )
        if not self.openai_client:
            raise RuntimeError("OpenAI client is not initialized.")
        return chat_once_openai(
            self.openai_client,
            self.history,
            content,
            model=self.model,
        )


def choose_provider() -> str:
    print("Режим по умолчанию: обычная (OpenAI).")
    print("Введите 2 для думающей модели (Claude), или Enter для обычной.")
    choice = input("Режим [Enter/2]: ").strip().lower()
    if choice in {"2", "думающая", "думающий", "claude", "anthropic"}:
        return "anthropic"
    return "openai"


if __name__ == "__main__":
    colorama_init()
    load_dotenv()
    provider = choose_provider()
    if provider == "anthropic":
        session = ChatSession(
            provider="anthropic",
            model="claude-sonnet-4-5-20250929",
            anthropic_client=create_anthropic_client(),
        )
    else:
        session = ChatSession(
            provider="openai",
            model="gpt-4o",
            openai_client=create_openai_client(),
        )
    session.system("Ты полезный ассистент. Отвечай кратко.")

    while True:
        user_input = input("Вы: ").strip()
        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            break
        try:
            answer = session.user(user_input)
        except RuntimeError as exc:
            print(f"{Fore.RED}Ошибка: {exc}{Style.RESET_ALL}")
            print("Подсказка: выбери обычный режим или проверь ключ.")
            break
        print(f"{Fore.CYAN}AI: {answer}{Style.RESET_ALL}")

    print("\nИстория диалога:")
    for message in session.history:
        role = message.get("role", "unknown")
        content = message.get("content", "")
        print(f"{role}: {content}")