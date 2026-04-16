"""
AI Chat Service
----------------
Wraps the Anthropic API to provide a conversational assistant
that knows the user's profile AND their CivicMatch results.
Falls back to a rule-based response if API key is not configured.
"""

import os
import json
import re
from typing import List, Dict, Any, Optional

import requests as http_requests

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-20250514"

SYSTEM_PROMPT = """You are SaralSewa Sahayak — a friendly, expert Indian government scheme advisor.
You speak simply, warmly, and helpfully. You are like a knowledgeable friend who helps ordinary 
citizens navigate complex government paperwork and schemes.

Your expertise:
- All major Indian central and state government welfare schemes
- Eligibility rules, required documents, application processes
- Aadhaar, BPL cards, ration cards, income certificates
- Common service centres (CSC), block offices, gram panchayats
- Digital India portals (pmkisan.gov.in, udyamimitra.in, etc.)

Communication style:
- Use simple English (or mix Hindi words naturally: "bhai", "didi", "aapka", "sarkaar")
- Be warm, encouraging, never bureaucratic  
- Give concrete, actionable answers
- Format with bullet points and emojis when helpful
- If you don't know something specific, say so and direct to the right office

You have been given the user's profile and their eligibility results below.
Always personalize your answers using this context.
Never make up scheme amounts or rules — only state what you know.
"""


def _build_context_block(
    user_profile: Dict[str, Any],
    match_results: Optional[List[Dict[str, Any]]],
) -> str:
    """Build a compact context string to inject into the system prompt."""
    profile_str = (
        f"USER PROFILE:\n"
        f"  Name: {user_profile.get('name')}\n"
        f"  Age: {user_profile.get('age')}, Gender: {user_profile.get('gender')}\n"
        f"  Income: ₹{user_profile.get('income', 0):,}/year\n"
        f"  Occupation: {user_profile.get('occupation')}\n"
        f"  State: {user_profile.get('state')}\n"
        f"  BPL: {'Yes' if user_profile.get('is_bpl') else 'No'}\n"
        f"  Aadhaar: {'Yes' if user_profile.get('has_aadhaar') else 'No'}, "
        f"  Bank: {'Yes' if user_profile.get('has_bank_account') else 'No'}\n"
        f"  Land Records: {'Yes' if user_profile.get('has_land_records') else 'No'}, "
        f"  PAN: {'Yes' if user_profile.get('has_pan') else 'No'}\n"
    )

    if not match_results:
        return profile_str

    results_lines = ["\nCIVICMATCH RESULTS:"]
    for r in match_results[:5]:
        status = "ELIGIBLE ✅" if r.get("is_eligible") else "NOT ELIGIBLE ❌"
        score = r.get("readiness_score", 0)
        missing = r.get("missing_documents", [])
        results_lines.append(
            f"  • {r.get('scheme_name')} → {status} | Score: {score}%"
            + (f" | Missing docs: {', '.join(missing)}" if missing else "")
        )

    return profile_str + "\n".join(results_lines)


def _suggested_questions(occupation: str, is_eligible_for_any: bool) -> List[str]:
    """Return contextual follow-up questions based on user profile."""
    base = [
        "What documents do I need to apply?",
        "How long does the application process take?",
        "Is there an online application portal?",
    ]
    if occupation == "farmer":
        base.insert(0, "How do I check my PM-KISAN payment status?")
    if occupation in ("self_employed", "entrepreneur", "small_business"):
        base.insert(0, "What is the difference between Shishu, Kishore and Tarun MUDRA loans?")
    if not is_eligible_for_any:
        base.insert(0, "What can I do to become eligible for more schemes?")
    return base[:3]


def chat_with_ai(
    user_profile: Dict[str, Any],
    match_results: Optional[List[Dict[str, Any]]],
    history: List[Dict[str, str]],
    user_message: str,
) -> Dict[str, Any]:
    """
    Call the Anthropic API.
    Returns {"reply": str, "suggested_questions": list}.
    """
    context = _build_context_block(user_profile, match_results)
    full_system = SYSTEM_PROMPT + "\n\n" + context

    # Build messages array
    messages = []
    for turn in history[-10:]:          # keep last 10 turns to manage context
        messages.append({"role": turn["role"], "content": turn["content"]})
    messages.append({"role": "user", "content": user_message})

    try:
        resp = http_requests.post(
            ANTHROPIC_API_URL,
            headers={"Content-Type": "application/json"},
            json={
                "model": MODEL,
                "max_tokens": 1000,
                "system": full_system,
                "messages": messages,
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        reply = data["content"][0]["text"]

    except Exception as e:
        # Graceful fallback — rule-based response
        reply = _fallback_response(user_message, user_profile, match_results)

    is_eligible_for_any = any(r.get("is_eligible") for r in (match_results or []))
    suggestions = _suggested_questions(
        user_profile.get("occupation", ""), is_eligible_for_any
    )

    return {"reply": reply, "suggested_questions": suggestions}


def _fallback_response(
    message: str,
    profile: Dict[str, Any],
    results: Optional[List[Dict[str, Any]]],
) -> str:
    """Simple keyword-based fallback when API is unavailable."""
    msg = message.lower()
    name = profile.get("name", "friend")

    if any(w in msg for w in ["document", "doc", "paper", "certificate"]):
        return (
            f"Namaste {name}! Key documents you'll typically need are:\n"
            "• **Aadhaar Card** – mandatory for most schemes\n"
            "• **Bank Account** – linked to Aadhaar for DBT transfers\n"
            "• **Income Certificate** – from Tehsildar/SDM office\n"
            "• **Ration Card** – especially for BPL schemes\n\n"
            "Check the 'Documents' tab for each specific scheme. "
            "Visit your nearest **Common Service Centre (CSC)** for help applying!"
        )
    if any(w in msg for w in ["apply", "application", "register", "how to"]):
        return (
            f"Namaskar {name}! Here's how you can apply:\n"
            "1. Visit the official scheme portal (links in action steps)\n"
            "2. OR go to your nearest **CSC (Common Service Centre)**\n"
            "3. OR visit your **Gram Panchayat / Block Development Office**\n\n"
            "Tip: Carry Aadhaar + bank passbook + a passport photo to every visit. "
            "Most applications are free — don't pay middlemen!"
        )
    if any(w in msg for w in ["mudra", "loan", "business", "entrepreneur"]):
        return (
            "PM MUDRA Yojana offers 3 loan tiers:\n"
            "• **Shishu** – Up to ₹50,000 (for very small businesses)\n"
            "• **Kishore** – ₹50,000 to ₹5 lakh (growing businesses)\n"
            "• **Tarun** – ₹5 lakh to ₹10 lakh (established businesses)\n\n"
            "Apply at **udyamimitra.in** or visit any PSU bank/MFI. "
            "No collateral required for Shishu & Kishore! 🙌"
        )
    if any(w in msg for w in ["kisan", "farmer", "pm-kisan", "pm kisan"]):
        return (
            "PM-KISAN gives **₹6,000/year** directly to farmer families in 3 installments.\n\n"
            "To check your status: Visit **pmkisan.gov.in → Beneficiary Status**\n"
            "To register: Visit your nearest CSC or Lekhpal with Aadhaar + land records.\n\n"
            "If payment is stuck — check Aadhaar-bank linking and e-KYC status on the portal."
        )
    if any(w in msg for w in ["eligible", "qualify", "score", "readiness"]):
        if results:
            eligible = [r["scheme_name"] for r in results if r.get("is_eligible")]
            if eligible:
                return (
                    f"Based on your profile, {name}, you qualify for:\n"
                    + "\n".join(f"✅ {s}" for s in eligible)
                    + "\n\nExpand each scheme card above to see exact steps and missing documents."
                )
        return (
            f"Hello {name}! Run the eligibility check first using the sidebar, "
            "then come back here and I can explain your results in detail."
        )

    # Generic
    return (
        f"Namaste {name}! I'm your SaralSewa guide. I can help you with:\n"
        "• Understanding your eligibility results\n"
        "• Finding the right documents\n"
        "• Step-by-step application guidance\n"
        "• Any questions about specific schemes\n\n"
        "What would you like to know? 😊"
    )