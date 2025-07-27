from typing import Dict


class OpenRouterClient:
    """Einfacher HTTP-Client für OpenRouter."""

    API_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def generate_document(self, idea: str, doc_type: str = "concept") -> str:
        import requests
        import json

        prompts = {
            "concept": (
                "Du bist eine technische Projektplanungs‑KI. Nimm die folgende "
                "App‑Beschreibung und erstelle ein detailliertes Konzept. Das "
                "Konzept sollte Anforderungen, Benutzerrollen, Funktionsumfang, "
                "empfohlene Programmiersprachen und Bibliotheken, Datenmodelle "
                "und einen groben Projektplan enthalten. Nutze Markdown‑Syntax "
                "und strukturiere das Ergebnis mit Überschriften und Listen."
            ),
            "requirements": (
                "Du bist ein Requirements‑Engineer. Verwandle die folgende App‑Idee "
                "in eine detaillierte Liste von Anforderungen. Formuliere klare User Stories, "
                "Edge Cases, Akzeptanzkriterien und technischen Einschränkungen. Nutze "
                "Markdown mit Überschriften, Listen und Tabellen, wo sinnvoll."
            ),
            "design": (
                "Du bist ein Softwarearchitekt. Erstelle auf Grundlage der folgenden Idee "
                "einen architektonischen Entwurf. Beschreibe die wichtigsten Komponenten, "
                "deren Schnittstellen, Datenflüsse und Speicherstrukturen. Verwende Markdown mit "
                "Diagrammen in ASCII oder PlantUML, wo hilfreich."
            ),
            "testing": (
                "Du bist ein QA‑Ingenieur. Erstelle einen Testplan für die folgende App. "
                "Liste Unit‑Tests, Integrations‑Tests, Performance‑Tests, Security‑Tests "
                "und Usability‑Tests auf. Gib außerdem Beispiel‑Testdaten und erwartete "
                "Ergebnisse an. Nutze Markdown zur Strukturierung."
            ),
        }
        system_prompt = prompts.get(doc_type, prompts["concept"])
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": idea},
        ]
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://example.com/",
            "X-Title": "FlowProjectPlanner",
        }
        body: Dict[str, object] = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 1024,
            "temperature": 0.3,
        }
        print(f"[OpenRouter] Generiere {doc_type}-Dokument mit Modell {self.model} …")
        try:
            response = requests.post(self.API_URL, headers=headers, data=json.dumps(body), timeout=60)
            response.raise_for_status()
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content")
            if not content:
                raise RuntimeError("Keine Antwort von OpenRouter erhalten.")
            return content.strip()
        except Exception as e:
            raise RuntimeError(f"Fehler beim Abruf des {doc_type}-Dokuments: {e}")

    def generate_concept(self, idea: str) -> str:
        return self.generate_document(idea, doc_type="concept")

__all__ = ["OpenRouterClient"]
