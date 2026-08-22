import re
import uuid
from typing import Dict, Any, Optional, Tuple, List
from sqlalchemy.orm import Session
from app.schemas.chatbot import ChatRequest, ChatResponse, ChatIntent, ChatContext
from app.schemas.commute import CommuteAnalyzeRequest
from app.services.commute_service import commute_service
from app.services.weather_service import weather_service
from app.services.ai_service import ai_service
from app.models.project import GovernmentProject
from app.models.warning import Warning, WarningStatus
from app.models.asset import InfrastructureAsset
from app.core.logging import logger


class ChatbotService:
    """
    Citizen & Officer Natural Language AI Chatbot Service.
    Pipeline: User Query -> Intent Extraction -> Backend Grounding / Commute Intelligence -> Gemini / Synthesis -> Response.
    """

    async def handle_message(self, db: Session, request: ChatRequest) -> ChatResponse:
        conv_id = request.conversation_id or str(uuid.uuid4())
        user_msg = request.message.strip()

        # 1. Intent & Entity Extraction
        intent_data = self._extract_intent_and_entities(user_msg)
        intent = intent_data.intent

        context: Dict[str, Any] = {
            "intent": intent,
            "user_query": user_msg,
            "entities": intent_data.entities,
        }
        precautions_list: List[str] = []

        # 2. Intent-Specific Backend Grounding
        if intent == "COMMUTE_QUERY":
            origin = intent_data.origin or "Hinjawadi"
            destination = intent_data.destination or "Pune Station"
            
            commute_req = CommuteAnalyzeRequest(
                origin=origin,
                destination=destination,
                mode="driving"
            )
            commute_res = await commute_service.analyze_commute(db, commute_req)
            
            context["route"] = commute_res.route.model_dump()
            context["risk"] = commute_res.risk.model_dump()
            context["weather"] = commute_res.weather.model_dump()
            context["projects"] = [p.model_dump() for p in commute_res.projects]
            context["warnings"] = [w.model_dump() for w in commute_res.warnings]
            context["precautions"] = commute_res.recommendations
            precautions_list = commute_res.recommendations

        elif intent in ("PROJECT_QUERY", "OFFICER_QUERY"):
            # Search relevant projects by text matching
            projects = db.query(GovernmentProject).all()
            matched_projects = []
            for p in projects:
                if any(w.lower() in p.name.lower() or w.lower() in p.department.lower() for w in user_msg.split()):
                    matched_projects.append(p)
            if not matched_projects:
                matched_projects = projects[:3]  # top active projects

            context["projects"] = [
                {
                    "project_id": p.project_id,
                    "name": p.name,
                    "department": p.department,
                    "status": p.status.value,
                    "progress": p.progress,
                    "officer_id": p.officer_id
                } for p in matched_projects
            ]
            if matched_projects and matched_projects[0].officer:
                off = matched_projects[0].officer
                context["officer"] = {
                    "employee_id": off.employee_id,
                    "department": off.department,
                    "designation": off.designation,
                    "public_contact": off.public_contact,
                    "email": off.email
                }

        elif intent == "WEATHER_QUERY":
            weather = await weather_service.get_current_weather()
            context["weather"] = weather.model_dump()

        elif intent in ("WARNING_QUERY", "INFRASTRUCTURE_QUERY"):
            warnings = db.query(Warning).filter(Warning.status == WarningStatus.ACTIVE).limit(5).all()
            context["warnings"] = [
                {
                    "title": w.title,
                    "severity": w.severity.value,
                    "risk_score": w.risk_score,
                    "description": w.description,
                    "trigger": w.trigger
                } for w in warnings
            ]
            assets = db.query(InfrastructureAsset).filter(InfrastructureAsset.risk_score >= 60).limit(5).all()
            context["infrastructure"] = [
                {
                    "asset_id": a.asset_id,
                    "name": a.name,
                    "asset_type": a.asset_type.value,
                    "health_score": a.health_score,
                    "risk_score": a.risk_score,
                    "condition": a.condition
                } for a in assets
            ]

        # 3. Call AI Service with verified context
        ai_reply = await ai_service.generate_response(user_msg, context)

        return ChatResponse(
            response=ai_reply,
            intent=intent,
            conversation_id=conv_id,
            context_used=context,
            precautions=precautions_list
        )

    def _extract_intent_and_entities(self, text: str) -> ChatIntent:
        """
        Rule-based intent and origin/destination parsing for Pune queries.
        """
        lower = text.lower()
        
        # Check for commute keywords: "go from X to Y", "commute", "travel", "route", "drive from"
        commute_patterns = [
            r"(?:go|travel|drive|commute|from)\s+([a-zA-Z\s]+?)\s+(?:to|towards|until)\s+([a-zA-Z\s\?]+)",
            r"route\s+(?:between|from)\s+([a-zA-Z\s]+?)\s+(?:and|to)\s+([a-zA-Z\s\?]+)",
        ]

        for pat in commute_patterns:
            match = re.search(pat, lower)
            if match:
                origin = match.group(1).replace("from", "").replace("i want to", "").replace("going", "").strip()
                dest = match.group(2).replace("?", "").replace(".", "").strip()
                if origin and dest:
                    return ChatIntent(
                        intent="COMMUTE_QUERY",
                        origin=origin.title(),
                        destination=dest.title(),
                        entities={"origin": origin.title(), "destination": dest.title()}
                    )

        if any(w in lower for w in ["hinjawadi", "pune station", "kothrud", "hadapsar", "baner", "wakad", "route", "traffic", "commute", "travel"]):
            return ChatIntent(
                intent="COMMUTE_QUERY",
                origin="Hinjawadi",
                destination="Pune Station",
                entities={"origin": "Hinjawadi", "destination": "Pune Station"}
            )

        if any(w in lower for w in ["project", "metro", "road work", "flyover", "construction", "officer", "in charge"]):
            return ChatIntent(intent="PROJECT_QUERY")

        if any(w in lower for w in ["weather", "rain", "monsoon", "rainfall", "flood", "temperature"]):
            return ChatIntent(intent="WEATHER_QUERY")

        if any(w in lower for w in ["warning", "alert", "danger", "precaution", "caution"]):
            return ChatIntent(intent="WARNING_QUERY")

        if any(w in lower for w in ["pipeline", "pressure", "leak", "sensor", "health score", "risk score", "bridge", "sewage"]):
            return ChatIntent(intent="INFRASTRUCTURE_QUERY")

        return ChatIntent(intent="GENERAL_CITY_QUERY")


chatbot_service = ChatbotService()
