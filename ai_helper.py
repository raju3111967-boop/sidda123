"""
AI Helper Module - Google Gemini Integration
सिध्द गौतम सोसायटी AI Features
Developer: श्री. राजेश भालेराव
"""

from google.genai import Client
import os
from typing import Dict, List, Optional

# Gemini API Configuration
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'YOUR_API_KEY_HERE')

# Initialize Gemini
try:
    client = Client(api_key=GEMINI_API_KEY)
    AI_ENABLED = True
except Exception as e:
    print(f"⚠️ AI Features disabled: {e}")
    AI_ENABLED = False


class SocietyAI:
    """Housing Society AI Assistant with Legal Awareness"""
    
    LEGAL_SYSTEM_PROMPT = """
    तू “सिद्ध गौतम AI” आहेस.
    तू member/dashboard मध्ये कार्यरत Housing Society साठीचा माहितीपर व कायदेशीर AI Assistant आहेस.

    सध्या प्रश्न आणि उत्तर यांचा योग्य संबंध (Relevance) राहत नाही.
    ही चूक तात्काळ व कायमची थांबव.

    ====================================================
    🔴 ROOT RULE (ABSOLUTE)
    ====================================================
    प्रश्नाचा विषय (INTENT) जुळत नसेल तर कोणतेही उत्तर देऊ नकोस.
    ❌ प्रश्न वेगळा, ❌ उत्तर वेगळे हे कधीही होऊ देऊ नकोस.

    ====================================================
    🟢 STEP 1: QUESTION INTENT DETECTION (MANDATORY)
    ====================================================
    प्रत्येक प्रश्नाला आधी खालीलपैकी एकच Category दे:
    • Director / संचालक मंडळ
    • Society Notice / सभा
    • Maintenance
    • Redevelopment
    • Legal
    • Rules / Bye-laws

    ====================================================
    🟢 STEP 2: ANSWER MATCH CHECK
    ====================================================
    उत्तर देण्यापूर्वी तपास:
    IF (Answer.Category != Question.Category) → ❌ उत्तर देऊ नकोस

    ====================================================
    🟢 STEP 3: DATA AVAILABILITY CHECK
    ====================================================
    IF (Information not available in provided context):
    → सरळ आणि प्रामाणिक उत्तर दे: “सध्या ही माहिती सोसायटी रेकॉर्डमध्ये उपलब्ध नाही.”
    👉 नोटीस / सभा / इतर माहिती दाखवू नकोस.

    ====================================================
    🟢 STEP 4: CLARIFY INSTEAD OF GUESS
    ====================================================
    जर प्रश्न अपूर्ण वाटत असेल तर Clarifying question विचार.

    ====================================================
    🟢 STEP 5: STRICT CONTENT FILTER
    ====================================================
    • संचालक प्रश्नाला → फक्त संचालक माहिती
    • सभेच्या प्रश्नाला → फक्त सभा माहिती
    • नोटीस → फक्त नोटीस
    ❌ कोणतेही cross-mixing नाही.

    ====================================================
    🟢 FINAL ENFORCEMENT
    ====================================================
    तू:
    ✔ प्रश्न न समजता उत्तर देणार नाहीस
    ✔ नोटीसला उत्तर समजणार नाहीस
    ✔ अंदाजावर उत्तर देणार नाहीस
    ✔ विषयाशी असंबंध उत्तर देणार नाहीस

    Member Dashboard मधील “सिद्ध गौतम AI” फक्त प्रश्नाशी थेट संबंधित, अचूक व विश्वासार्ह उत्तरच देईल.
    उत्तराच्या शेवटी "सोसायटीचा Ai आपला आभारी राहील" असा मॅसेज दाखवा.
    """

    @staticmethod
    def detect_intent(question: str) -> str:
        """
        प्रश्नाचा हेतू (Intent) ओळखा - Strict Classification
        """
        if not AI_ENABLED: return "General"
        try:
            prompt = f"""
            Analyze the following question from a Housing Society Member and classify it into EXACTLY ONE of these categories:
            1. Director (Questions about committee members, chairman, secretary, board count, contact)
            2. Notice (Questions about meetings, AGM, SGM, agenda, announcements, notices)
            3. Maintenance (Questions about bills, funds, repairs, water, electricity, dues)
            4. Redevelopment (Questions about construction, builder, progress, status, offer)
            5. Legal (Questions about Act, rules, bye-laws, rights, duties, transfers, police, court)
            6. General (Greetings, unspecified, or unrelated)

            Question: "{question}"

            Output ONLY the Category Name (e.g. "Director"). Do not write anything else.
            """
            response = client.models.generate_content(model='gemini-1.5-flash', contents=prompt)
            formatted = response.text.strip().replace("Category: ", "").replace(".", "")
            # Mapping back to simple keys
            if "Director" in formatted: return "Director"
            if "Notice" in formatted: return "Notice"
            if "Maintenance" in formatted: return "Maintenance"
            if "Redevelopment" in formatted: return "Redevelopment"
            if "Legal" in formatted: return "Legal"
            return "General"
        except Exception as e:
            print(f"Intent Detection Error: {e}")
            return "General"

    @staticmethod
    def classify_complaint(subject: str, description: str) -> Dict[str, str]:
        """
        तक्रारीचा प्रकार ओळखा
        Returns: {category, priority, sentiment}
        """
        if not AI_ENABLED:
            return {
                'category': 'सामान्य',
                'priority': 'मध्यम',
                'sentiment': 'तटस्थ',
                'ai_enabled': False
            }
        
        try:
            prompt = f"""
            {SocietyAI.LEGAL_SYSTEM_PROMPT}
            
            खालील तक्रार वाचा आणि विश्लेषण करा:
            विषय: {subject}
            तपशील: {description}
            
            कृपया खालील माहिती द्या (फक्त मराठीत):
            1. Category (प्रकार): [पाणी पुरवठा / वीज / स्वच्छता / सुरक्षा / देखभाल / पार्किंग / कायदेशीर / इतर]
            2. Priority (प्राधान्यता): [अत्यावश्यक / उच्च / मध्यम / कमी]
            3. Sentiment (भावना): [नाराज / चिंतित / तटस्थ / सकारात्मक]
            
            फक्त या तीन ओळी द्या.
            """
            
            response = client.models.generate_content(model='gemini-1.5-flash', contents=prompt)
            result_text = response.text.strip()
            
            # Parse response
            lines = result_text.split('\n')
            category = 'सामान्य'
            priority = 'मध्यम'
            sentiment = 'तटस्थ'
            
            for line in lines:
                if 'Category' in line or 'प्रकार' in line:
                    category = line.split(':')[-1].strip()
                elif 'Priority' in line or 'प्राधान्यता' in line:
                    priority = line.split(':')[-1].strip()
                elif 'Sentiment' in line or 'भावना' in line:
                    sentiment = line.split(':')[-1].strip()
            
            return {
                'category': category,
                'priority': priority,
                'sentiment': sentiment,
                'ai_enabled': True
            }
            
        except Exception as e:
            print(f"AI Classification Error: {e}")
            return {
                'category': 'सामान्य',
                'priority': 'मध्यम',
                'sentiment': 'तटस्थ',
                'ai_enabled': False,
                'error': str(e)
            }
    
    @staticmethod
    def suggest_reply(subject: str, description: str, category: str = None) -> str:
        """
        Admin साठी उत्तर सुचवा (Draft Reply) - Admin Legal Support Mode
        """
        if not AI_ENABLED:
            return "धन्यवाद. तुमची तक्रार नोंदवली गेली आहे. लवकरच त्यावर कार्यवाही केली जाईल."
        
        try:
            prompt = f"""
            {SocietyAI.LEGAL_SYSTEM_PROMPT}

            ROLE: Admin Legal Support Mode.
            TASK: खालील तक्रारीसाठी कायदेशीरदृष्ट्या योग्य उत्तराचा मसुदा (Draft Reply) तयार करा.

            तक्रार:
            विषय: {subject}
            तपशील: {description}
            {"प्रकार: " + category if category else ""}
            
            सूचना:
            - भाषा: मराठी (व्यावसायिक आणि कायदेशीर)
            - संबंधित कायदा/उपविधीचा संदर्भ असल्यास नमूद करा.
            - गरज असल्यास "High Risk Legal Matter" असा इशारा द्या.
            - उत्तर नम्र पण स्पष्ट असावे.
            """
            
            response = client.models.generate_content(model='gemini-1.5-flash', contents=prompt)
            return response.text.strip()
            
        except Exception as e:
            print(f"AI Reply Suggestion Error: {e}")
            return "धन्यवाद. तुमची तक्रार नोंदवली गेली आहे. लवकरच त्यावर कार्यवाही केली जाईल."
    
    @staticmethod
    def humanize_society_info(question: str, info: str, source: str) -> str:
        """
        सोसायटी डेटाबेस (नोटिस/अपडेट) मधून मिळालेली माहिती AI व्यक्तिमत्त्वानुसार फॉरमॅट करणे
        """
        if not AI_ENABLED:
            return info

        try:
            prompt = f"""
            {SocietyAI.LEGAL_SYSTEM_PROMPT}

            CONTEXT:
            User asked: "{question}"
            We found this Official Information in Society Records ({source}): "{info}"

            TASK:
            Rewrite this information as "Siddha Gautam AI".
            1. **Accuracy**: The core facts (dates, numbers, names) from the Official Information must remain EXACTLY the same. Do not hallucinate new facts.
            2. **Style**: Conversational, helpful Marathi. "सोसायटीच्या रेकॉर्डनुसार..." or "अधिकृत सूचनेनुसार..." starts are good.
            3. **Legal**: Briefly mention that this is part of the society's administrative record keeping (Records of Society).
            4. **Disclaimer**: End with the standard disclaimer: "ही माहिती महाराष्ट्र सहकारी संस्था अधिनियम, 1960 आणि मॉडेल उपविधींवर आधारित सामान्य मार्गदर्शन आहे..."
            """
            
            response = client.models.generate_content(model='gemini-1.5-flash', contents=prompt)
            return response.text.strip()
            
        except Exception as e:
            print(f"AI Humanize Error: {e}")
            return info

    @staticmethod
    def get_legal_advice(question: str) -> str:
        """
        सदस्यांच्या कायदेशीर प्रश्नांसाठी उत्तर (Member Questions)
        """
        if not AI_ENABLED:
            return "क्षमस्व, AI सेवा सध्या उपलब्ध नाही."

        try:
            prompt = f"""
            {SocietyAI.LEGAL_SYSTEM_PROMPT}

            CONTEXT: 
            You are operating in the 'Member Dashboard' mode.
            User is a Member of the Cooperative Housing Society.
            
            USER QUESTION: "{question}"

            INSTRUCTIONS:
            - Follow the STRICT RULES defined above in the System Prompt.
            - Apply the RELEVANCE CHECK mandated above.
            - Provide the answer in the MANDATORY LEGAL ANSWER FORMAT.
            - Ensure the DISCLAIMER is present at the end.
            """
            
            response = client.models.generate_content(model='gemini-1.5-flash', contents=prompt)
            return response.text.strip()

        except Exception as e:
            print(f"AI Legal Advice Error: {e}")
            return "क्षमस्व, तांत्रिक अडचणीमुळे उत्तर देता येत नाही. कृपया ॲडमिनशी संपर्क साधा."

    @staticmethod
    def summarize_notices(notices: List[Dict]) -> str:
        """
        एकाधिक सूचनांचा सारांश तयार करा
        """
        if not AI_ENABLED or not notices:
            return "सध्या कोणत्याही सूचना नाहीत."
        
        try:
            notices_text = "\n\n".join([
                f"सूचना {i+1}:\nशीर्षक: {n['title']}\nसामग्री: {n['content']}"
                for i, n in enumerate(notices[:5])
            ])
            
            prompt = f"""
            {SocietyAI.LEGAL_SYSTEM_PROMPT}
            खालील Housing Society च्या सूचनांचा एक संक्षेप (Summary) तयार करा (मराठीत):
            {notices_text}
            """
            
            response = client.models.generate_content(model='gemini-1.5-flash', contents=prompt)
            return response.text.strip()
            
        except Exception as e:
            print(f"AI Summarization Error: {e}")
            return "सूचनांचा सारांश तयार करता आला नाही."
    
    @staticmethod
    def analyze_redevelopment_status(updates: List[Dict]) -> str:
        """
        रिडेव्हलपमेंट प्रगतीचे विश्लेषण
        """
        if not AI_ENABLED or not updates:
            return "रिडेव्हलपमेंट अपडेट्स उपलब्ध नाहीत."
        
        try:
            updates_text = "\n\n".join([
                f"अपडेट {i+1}:\nशीर्षक: {u['title']}\nतपशील: {u['description']}\nप्रगती: {u['progress']}%"
                for i, u in enumerate(updates[:5])
            ])
            
            prompt = f"""
            {SocietyAI.LEGAL_SYSTEM_PROMPT}
            Housing Society च्या रिडेव्हलपमेंट प्रकल्पाच्या खालील अपडेट्सचे कायदेशीर व प्रगतीच्या दृष्टीने विश्लेषण करा:
            
            {updates_text}
            
            एक संक्षिप्त विश्लेषण (मराठीत) द्या.
            """
            
            response = client.models.generate_content(model='gemini-1.5-flash', contents=prompt)
            return response.text.strip()
            
        except Exception as e:
            print(f"AI Analysis Error: {e}")
            return "विश्लेषण तयार करता आले नाही."
    
    @staticmethod
    def generate_meeting_agenda(complaints: List[Dict], notices: List[Dict]) -> str:
        """
        सभेसाठी agenda तयार करा
        """
        if not AI_ENABLED:
            return "AI सुविधा उपलब्ध नाही."
        
        try:
            complaints_text = "\n".join([
                f"- {c['subject']}"
                for c in complaints[:10]
            ])
            
            prompt = f"""
            {SocietyAI.LEGAL_SYSTEM_PROMPT}
            Housing Society च्या मासिक सभेसाठी Agenda (कार्यक्रम पत्रिका) तयार करा.
            नियम ९५ व उपविधींनुसार सभेची रचना असावी.
            
            अलीकडील तक्रारी:
            {complaints_text}
            
            Agenda (मराठीत) तयार करा.
            """
            
            response = client.models.generate_content(model='gemini-1.5-flash', contents=prompt)
            return response.text.strip()
            
        except Exception as e:
            print(f"AI Agenda Generation Error: {e}")
            return "Agenda तयार करता आले नाही."
    
    @staticmethod
    def get_ai_status() -> Dict:
        """AI सुविधेची स्थिती"""
        return {
            'enabled': AI_ENABLED,
            'model': 'gemini-1.5-flash' if AI_ENABLED else None,
            'features': [
                'Legal Knowledge Base (Act 1960)',
                'Model Bye-laws Support',
                'Complaint Classification',
                'Draft Legal Replies',
                'Meeting Agenda Generation'
            ] if AI_ENABLED else []
        }


# Helper function for easy access
def get_ai_assistant():
    """AI Assistant instance मिळवा"""
    return SocietyAI()


# Test function
if __name__ == "__main__":
    ai = SocietyAI()
    print("🤖 AI Status:", ai.get_ai_status())
    
    # Test classification
    result = ai.classify_complaint(
        "पाणी पुरवठा बंद",
        "आज सकाळपासून आमच्या इमारतीत पाणी येत नाहीये. कृपया लवकर तपासा."
    )
    print("\n📊 Classification:", result)
    
    # Test reply suggestion
    reply = ai.suggest_reply(
        "पाणी पुरवठा बंद",
        "आज सकाळपासून आमच्या इमारतीत पाणी येत नाहीये.",
        "पाणी पुरवठा"
    )
    print("\n💬 Suggested Reply:", reply)
