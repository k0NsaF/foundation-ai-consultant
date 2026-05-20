from openai import OpenAI
from typing import List, Dict
import re
import os
from dotenv import load_dotenv

load_dotenv()


class AnswerGenerator:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=os.getenv("GITHUB_TOKEN")
        )
        self.model = "gpt-4o-mini"

    def _clean_response(self, text: str) -> str:
        cleaned = re.sub(r'[^\u0400-\u04FF\u0500-\u052F\d\s\.,!?\-:;"\'\(\)\[\]]', '', text)
        return cleaned.strip()

    def build_prompt(
        self,
        user_input: str,
        retrieved_docs: List[Dict],
        cost_result: Dict,
        weather_result: Dict,
        stores: List[Dict],
        enriched_params: Dict
    ) -> str:
        docs_text = "\n\n".join([
            f"[Документ {i+1}] {doc['text'][:500]}"
            for i, doc in enumerate(retrieved_docs[:3])
        ])

        soil = enriched_params.get("soil", "не указан")
        freezing_depth = enriched_params.get("freezing_depth", "не рассчитана")
        load = enriched_params.get("total_load_tons", 0)
        material = enriched_params.get("material", "не указан")
        floors = enriched_params.get("floors", 1)
        
        foundation_type = cost_result.get("type", "Не определён")

        return f"""Ты опытный инженер-строитель, специалист по фундаментам.
Отвечай строго на основе приведенных документов.

Вопрос пользователя: {user_input}

Детальный анализ условий:
- Тип грунта: {soil}
- Глубина промерзания: {freezing_depth} м
- Нагрузка от дома: {load} тонн
- Материал стен: {material}
- Этажность: {floors}

ТИП ФУНДАМЕНТА (рассчитан калькулятором): {foundation_type}

Документы СНиП:
{docs_text}

Дай ответ строго в формате:

РЕКОМЕНДУЕМЫЙ ТИП ФУНДАМЕНТА:
{foundation_type}

ПОЧЕМУ ИМЕННО ОН:
(объясни, почему для этих условий подходит именно {foundation_type})

РИСКИ И ВАЖНЫЕ УСЛОВИЯ:
(на что обратить внимание)

Используй только русский язык. Тип фундамента должен быть ТОЧНО: {foundation_type}"""

    def generate(
        self,
        user_input: str,
        retrieved_docs: List[Dict],
        cost_result: Dict,
        weather_result: Dict,
        stores: List[Dict],
        enriched_params: Dict
    ) -> str:
        prompt = self.build_prompt(
            user_input, retrieved_docs, cost_result, weather_result, stores, enriched_params
        )
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=2000
            )
            raw_response = response.choices[0].message.content
            cleaned_response = self._clean_response(raw_response)
            
            foundation_type = cost_result.get("type", "Не определён")
            if foundation_type not in cleaned_response:
                cleaned_response = f"РЕКОМЕНДУЕМЫЙ ТИП ФУНДАМЕНТА:\n{foundation_type}\n\n" + cleaned_response
            
            return cleaned_response
        except Exception as e:
            foundation_type = cost_result.get("type", "Не определён")
            return f"""РЕКОМЕНДУЕМЫЙ ТИП ФУНДАМЕНТА: {foundation_type}

ПОЧЕМУ ИМЕННО ОН:
Рекомендация основана на расчетах калькулятора.

РИСКИ И ВАЖНЫЕ УСЛОВИЯ:
Уточните детали для более точной рекомендации."""


AnswerGenerator = AnswerGenerator