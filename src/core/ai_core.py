"""Core AI/Chatbot functionality using Google Gemini API"""
import os
import logging
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

# Plant care expert system prompt
SYSTEM_PROMPT = """You are an expert plant care assistant for a garden nursery. Your goal is to help customers grow healthy plants and make better buying decisions.

IMPORTANT RULES:
- Keep responses SHORT and PRACTICAL (max 3-4 sentences per topic)
- Use simple, beginner-friendly language
- Always provide SPECIFIC ADVICE (not generic tips)
- Format responses for easy scanning
- Be conversational and encouraging

RESPONSE FORMATS:

1. CARE GUIDANCE (when asked "How to care for..." or similar)
   ✓ Watering: "Water when top soil is dry, ~2x/week in summer. Check soil moisture with your finger."
   ✓ Light: "Bright indirect light, 3-4 hours/day minimum. A window seat is ideal."
   ✓ Soil: "Well-draining potting soil, avoid clay. Repot every 1-2 years."
   ✓ Temperature: "18-25°C ideal, avoid below 10°C. Keep away from cold drafts."

2. PROBLEM SOLVING (when user reports an issue like "leaves turning yellow")
   - Ask ONE clarifying question if needed (e.g., "How often are you watering?")
   - Suggest 2-3 MOST LIKELY causes
   - Give ONE specific solution per cause
   - Example: "Yellow leaves often mean overwatering or low light. Try reducing water to 1x/week and move near a window for a week."

3. PLANT RECOMMENDATIONS (when asked to suggest plants)
   - Ask about their environment (indoor/outdoor, light level, space size)
   - Suggest 3 plants matching their needs with names
   - Include care difficulty (Beginner/Easy/Intermediate/Advanced)
   - Give 1-2 key benefits per plant

4. GENERAL Q&A (other questions about plants)
   - Answer factually about plant biology and care
   - Connect to practical application when possible
   - If uncertain, be honest: "I'm not certain, but generally..."

5. BUYING ADVICE
   - When asked about specific plants or recommendations
   - Mention available care requirements
   - Suggest complementary items (pots, soil, fertilizers)

TONE: Friendly, encouraging, expert yet approachable, passionate about plants.

CONVERSATION CONTEXT:
- Remember and reference previous messages in the conversation
- Build on prior discussions to avoid repeating information
- Use conversational continuity: "Like the aloe vera we discussed earlier..."

CONSTRAINTS:
- If asked about non-plant topics, politely redirect: "I'm specifically trained for plant care - how can I help with your plants?"
- Do NOT pretend to have real-time data or current prices
- Do NOT make medical claims about plants
"""


class AICore:
    """Core AI functionality wrapper for Gemini API"""
    
    def __init__(self):
        """Initialize Gemini API client"""
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.model = None
        self.init_error = None
        
        logger.info(f"🔍 AI Core init: API Key present = {bool(self.api_key)}, Model = {self.model_name}")
        
        if not self.api_key:
            logger.warning("⚠️  GEMINI_API_KEY not found in environment variables - AI features will be unavailable")
            return
        
        try:
            # Lazy import of google.generativeai
            logger.info("📦 Step 1: Loading google.generativeai module...")
            import google.generativeai as genai
            logger.info("✅ Step 1: google.generativeai module loaded")
            
            logger.info("📦 Step 2: Loading HarmCategory, HarmBlockThreshold...")
            from google.generativeai.types import HarmCategory, HarmBlockThreshold
            logger.info("✅ Step 2: Types loaded")
            
            logger.info("🔑 Step 3: Configuring Gemini API...")
            genai.configure(api_key=self.api_key)
            logger.info("✅ Step 3: Gemini configured")
            
            logger.info("🤖 Step 4: Initializing Gemini model...")
            self.model = genai.GenerativeModel(
                self.model_name,
                system_instruction=SYSTEM_PROMPT,
                safety_settings=[
                    {
                        "category": HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                        "threshold": HarmBlockThreshold.BLOCK_ONLY_HIGH
                    },
                    {
                        "category": HarmCategory.HARM_CATEGORY_HARASSMENT,
                        "threshold": HarmBlockThreshold.BLOCK_ONLY_HIGH
                    },
                    {
                        "category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                        "threshold": HarmBlockThreshold.BLOCK_ONLY_HIGH
                    },
                    {
                        "category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                        "threshold": HarmBlockThreshold.BLOCK_ONLY_HIGH
                    },
                ]
            )
            logger.info(f"✅ Step 4: Gemini model initialized")
            logger.info(f"✅✅✅ Gemini AI initialized successfully with model: {self.model_name}")
            
        except ModuleNotFoundError as e:
            error_msg = f"❌ google-generativeai package not installed. Install with: pip install google-generativeai==0.7.2. Error: {e}"
            logger.error(error_msg)
            self.init_error = error_msg
            self.model = None
            
        except Exception as e:
            error_msg = f"❌ Failed to initialize Gemini API: {type(e).__name__}: {e}"
            logger.error(error_msg, exc_info=True)
            self.init_error = error_msg
            self.model = None
    
    async def generate_response(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate AI response using Gemini API
        
        Args:
            user_message: The user's input message
            conversation_history: List of dicts with 'role' and 'message' keys
                                 Example: [{"role": "USER", "message": "How to water ..."}, ...]
        
        Returns:
            AI generated response string
            
        Raises:
            RuntimeError: If API not initialized
            Exception: If API call fails
        """
        if not self.model or self.init_error:
            error_msg = self.init_error or "Gemini model not initialized. Check GEMINI_API_KEY environment variable."
            logger.error(f"❌ Cannot generate response: {error_msg}")
            raise RuntimeError(error_msg)
        
        try:
            logger.info(f"🤖 Generating response for message: {user_message[:50]}...")
            
            # Prepare conversation history in Gemini format
            chat_history = []
            if conversation_history:
                for msg in conversation_history[-10:]:  # Limit to last 10 messages for context window
                    role = "user" if msg.get("role") == "USER" else "model"
                    chat_history.append({
                        "role": role,
                        "parts": [{"text": msg.get("message", "")}]
                    })
            
            # Create chat session with history
            chat = self.model.start_chat(history=chat_history)
            
            # Send message and get response
            response = chat.send_message(user_message)
            
            # Extract text from response
            if response.parts:
                ai_response = response.parts[0].text
                logger.info(f"✅ AI response generated successfully")
                return ai_response
            else:
                logger.warning("⚠️  Empty response from Gemini API")
                return "I couldn't generate a response. Could you try rephrasing your question?"
                
        except Exception as e:
            logger.error(f"❌ Error calling Gemini API: {e}", exc_info=True)
            raise RuntimeError(f"Failed to generate AI response: {e}")
    
    def is_available(self) -> bool:
        """Check if Gemini API is available"""
        return self.model is not None and self.init_error is None


# Global AI instance (lazy initialization)
_ai_core: Optional[AICore] = None


def get_ai_core() -> AICore:
    """Get or initialize AI core singleton"""
    global _ai_core
    if _ai_core is None:
        logger.info("🔧 Initializing AI Core singleton...")
        _ai_core = AICore()
    return _ai_core
