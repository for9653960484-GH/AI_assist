# TextAgent

Консольный чат-агент с выбором провайдера (OpenAI или Anthropic).

## Возможности
- Диалог в терминале с сохранением истории
- Быстрое переключение между OpenAI и Claude
- Поддержка `.env` для ключей и базовых URL

## Установка
```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Настройка окружения
Создайте файл `.env` в корне проекта:
```
OPENAI_API_KEY=ваш_ключ_openai
OPENAI_BASE_URL=опционально

ANTHROPIC_API_KEY=ваш_ключ_anthropic
ANTHROPIC_BASE_URL=опционально
```

## Запуск
```
python text_agent.py
```

При старте выберите режим:
- Enter — обычный (OpenAI)
- `2` — думающая модель (Claude)

## Зависимости
Список пакетов — в `requirements.txt`.
