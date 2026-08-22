import json
from typing import Dict, Any, Optional, List
import httpx
from app.core.config import settings
from app.core.logging import logger


class AIService:
    """
    Google Gemini integration service.
    Enforces strict grounding on backend-verified context and anti-hallucination protocols.
    """

    SYSTEM_INSTRUCTION = """
You are the SmartInfra AI Citizen & Municipal Intelligence Assistant for Pune City.

STRICT OPERATIONAL RULES:
1. Grounding: Rely EXCLUSIVELY on the verified structured context provided in the user prompt (route data, projects, warnings, weather, infrastructure, and officers).
2. Anti-Hallucination: NEVER invent or assume officer names, phone numbers, project statuses, sensor readings, or weather measurements. If information is not in the context, explicitly state that it is not currently recorded in the PMC municipal registry.
3. Distinction: Clearly distinguish FACT (verified PMC datasets and live sensors) from PREDICTION (statistical/ML risk estimations) and RECOMMENDATION (safety advisories).
4. Tone: Concise, professional, helpful, objective, and action-oriented.
5. Safety: Do not provide unauthorized or dangerous structural repair instructions. Always recommend standard PMC citizen precautions and official contact helplines where relevant.
"""

    async def generate_response(
        self,
        prompt: str,
        context_data: Dict[str, Any],
        system_instruction: Optional[str] = None
    ) -> str:
        """
        Send contextualized prompt to Google Gemini.
        Falls back to a structured deterministic synthesis engine if API key is not configured.
        """
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            return self._deterministic_synthesizer(prompt, context_data)

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={api_key}"
        
        full_prompt = f"""
VERIFIED PUNE MUNICIPAL CONTEXT:
{json.dumps(context_data, indent=2, default=str)}

USER QUESTION:
{prompt}

Provide a direct, accurate, and structured answer adhering strictly to the operational rules.
"""

        body = {
            "contents": [
                {
                    "parts": [{"text": full_prompt}]
                }
            ],
            "systemInstruction": {
                "parts": [{"text": system_instruction or self.SYSTEM_INSTRUCTION}]
            },
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 1024,
            }
        }

        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                res = await client.post(url, json=body)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        text_part = candidates[0]["content"]["parts"][0]["text"]
                        return text_part.strip()
                else:
                    logger.warning(f"Gemini API returned status {res.status_code}: {res.text}")
        except Exception as e:
            logger.warning(f"Gemini API invocation failed: {e}")

        return self._deterministic_synthesizer(prompt, context_data)

    def _deterministic_synthesizer(self, user_query: str, context: Dict[str, Any]) -> str:
        """
        High-quality factual synthesis fallback matching Gemini output standards.
        """
        intent = context.get("intent", "GENERAL_CITY_QUERY")
        lines = []

        if intent == "COMMUTE_QUERY":
            route = context.get("route", {})
            weather = context.get("weather", {})
            projects = context.get("projects", [])
            warnings = context.get("warnings", [])
            risk = context.get("risk", {}).get("level", "MODERATE")

            start = route.get("start_address", "Origin")
            end = route.get("end_address", "Destination")
            dist_km = (route.get("distance_meters", 0)) / 1000.0
            dur_min = int((route.get("duration_seconds", 0)) / 60.0)

            lines.append(f"**Commute Summary ({start} → {end}):**")
            lines.append(f"• **Distance & Time:** Approx. {dist_km:.1f} km ({dur_min} mins via primary arterial road).")
            lines.append(f"• **Overall Corridor Risk:** **{risk}**")

            if weather:
                cond = weather.get("condition", "Normal")
                temp = weather.get("temperature", 28.0)
                rain = weather.get("rainfall", 0.0)
                lines.append(f"• **Weather Conditions:** {cond}, {temp}°C (Rainfall: {rain:.1f} mm).")

            if projects:
                lines.append("\n**Active Government Infrastructure Works on Route:**")
                for p in projects[:3]:
                    name = p.get("name", "Road Work")
                    dept = p.get("department", "PMC")
                    prog = p.get("progress", 0.0)
                    lines.append(f"  - **{name}** ({dept}): {prog:.0f}% completed (Status: {p.get('status', 'ONGOING')}).")

            if warnings:
                lines.append("\n**Active Infrastructure Warnings in Corridor:**")
                for w in warnings[:3]:
                    title = w.get("title", "Caution")
                    sev = w.get("severity", "MODERATE")
                    lines.append(f"  - [{sev}] **{title}**: {w.get('description', '')}")

            lines.append("\n**Citizen Precautions & Recommendations:**")
            if risk in ("HIGH", "CRITICAL"):
                lines.append("• Allow an extra 15–20 minutes travel buffer due to ongoing works and potential congestion.")
            if weather.get("rainfall", 0) > 2.0:
                lines.append("• Exercise caution on wet road sections and follow traffic diversion signage.")
            lines.append("• For road emergencies or open pothole hazards, contact PMC Smart City Helpline at 1800-1030-222.")

            return "\n".join(lines)

        elif intent == "PROJECT_QUERY":
            projects = context.get("projects", [])
            if projects:
                p = projects[0]
                lines.append(f"**Government Project Details:**")
                lines.append(f"• **Project Name:** {p.get('name')}")
                lines.append(f"• **Department:** {p.get('department')}")
                lines.append(f"• **Status:** {p.get('status')} ({p.get('progress', 0):.0f}% progress)")
                if "officer" in context and context["officer"]:
                    off = context["officer"]
                    lines.append(f"• **Responsible Officer:** {off.get('designation')} ({off.get('department')})")
                    if off.get("public_contact"):
                        lines.append(f"• **Authorized Public Contact:** {off.get('public_contact')}")
                return "\n".join(lines)

        # General response grounded in verified data
        return f"SmartInfra AI verified context retrieved for Pune Smart City infrastructure. Query processed for intent '{intent}' with {len(context.get('projects', []))} related project(s) and {len(context.get('warnings', []))} active warning(s)."


ai_service = AIService()
