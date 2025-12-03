"""
AI Interview Bot
- Removed score threshold override
- Score-based acknowledgments
- Simplified logic
"""

import json
import requests
import time
from ai_interview_prompt import (
    get_evaluation_prompt,
    get_rephrase_prompt,
    get_new_question_prompt,
    get_start_interview_prompt,
    get_encouragement_message
)

# API Configuration
GEMINI_API_KEY = "AIzaSyDyn113sejmtGatyFaQneuqHrFfFmJv3Oc"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"


def call_gemini_api(prompt, retry_count=0):
    """Call Gemini API with retry logic"""
    try:
        response = requests.post(
            f"{GEMINI_URL}?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.6, "maxOutputTokens": 400}
            },
            timeout=30
        )
        
        if not response.ok:
            if response.status_code in [429, 503] and retry_count < 3:
                time.sleep((2 ** retry_count) * 1)
                return call_gemini_api(prompt, retry_count + 1)
            raise Exception(f"API Error: {response.status_code}")
        
        data = response.json()
        text = data['candidates'][0]['content']['parts'][0]['text']
        text = text.replace('```json\n', '').replace('```\n', '').replace('```', '').strip()
        
        return json.loads(text)
        
    except Exception as e:
        if retry_count < 2:
            time.sleep(1)
            return call_gemini_api(prompt, retry_count + 1)
        raise


class AikamInterviewBot:
    """Interview Bot with Deterministic Rephrasing Logic"""
    
    def __init__(self, job_description, resume):
        self.job_description = job_description
        self.resume = resume
        
        # State
        self.current_question = ""
        self.current_round = "HR"
        self.is_rephrased = False  # CRITICAL FLAG - managed by Python
        self.total_score = 0
        self.question_count = 0
        self.asked_questions = []  # Store FULL questions
    
    def _evaluate_answer(self, question, answer):
        """Evaluate answer - NO threshold override"""
        prompt = get_evaluation_prompt(question, answer, self.job_description, self.resume)
        
        try:
            result = call_gemini_api(prompt)
            
            score = result.get('score') or result.get('score_out_of_10') or 0
            is_adequate = result.get('is_adequate', True)  # Default to True
            reason = result.get('reason') or result.get('evaluation_reason') or "No reason"
            
            # NO OVERRIDE - trust LLM evaluation completely
            
            return {
                'is_adequate': is_adequate,
                'score': score,
                'reason': reason
            }
        except Exception as e:
            print(f"[ERROR] Evaluation failed: {e}")
            return {'is_adequate': True, 'score': 0, 'reason': f"Error: {e}"}
    
    def _rephrase_question(self, question):
        """Rephrase question"""
        prompt = get_rephrase_prompt(question)
        return call_gemini_api(prompt)
    
    def _generate_new_question(self, score=0):
        """Generate new question"""
        prompt = get_new_question_prompt(
            self.current_round,
            self.job_description,
            self.resume,
            self.asked_questions
        )
        return call_gemini_api(prompt)
    
    def process_turn(self, user_answer):
        """Process turn - Main entry point"""
        
        # Start interview
        if not self.current_question:
            return self._start_interview()
        
        # Empty answer
        if not user_answer or not user_answer.strip():
            return self._handle_empty_answer()
        
        # Evaluate and proceed
        return self._evaluate_and_proceed(user_answer)
    
    def _start_interview(self):
        """Start interview"""
        self.current_question = get_start_interview_prompt()
        self.current_round = "HR"
        self.asked_questions.append("introduction")
        
        return {
            "is_inadequate": False,
            "score_out_of_10": 0,
            "evaluation_reason": "Interview started",
            "question": self.current_question,
            "is_rephrased": False,
            "action": "start_interview"
        }
    
    def _handle_empty_answer(self):
        """Handle empty answer"""
        encouragement = get_encouragement_message("empty")
        question_data = self._generate_new_question(0)
        
        self.current_question = question_data['question']
        self.is_rephrased = False
        self.asked_questions.append(question_data['question'])
        
        message = f"{encouragement} {question_data['question']}"
        
        return {
            "is_inadequate": False,
            "score_out_of_10": 0,
            "evaluation_reason": "Empty response",
            "question": message,
            "is_rephrased": False,
            "action": "empty_response"
        }
    
    def _evaluate_and_proceed(self, answer):
        """Evaluate and proceed - UPDATED LOGIC per team lead"""
        
        evaluation = self._evaluate_answer(self.current_question, answer)
        
        is_adequate = evaluation['is_adequate']
        score = evaluation['score']
        reason = evaluation['reason']
        
        print(f"\n[DEBUG] ========================================")
        print(f"[DEBUG] Question: {self.current_question[:50]}...")
        print(f"[DEBUG] Answer: {answer[:50]}...")
        print(f"[DEBUG] Evaluation: adequate={is_adequate}, score={score}")
        print(f"[DEBUG] is_rephrased flag: {self.is_rephrased}")
        
        # UPDATED LOGIC per team lead
        if (not is_adequate) and (not self.is_rephrased):
            # Only rephrase if inadequate AND not already rephrased
            print(f"[DEBUG] Decision: INADEQUATE + NOT REPHRASED → REPHRASE")
            print(f"[DEBUG] ========================================\n")
            return self._rephrase_current_question(evaluation)
        else:
            # All other cases: move to next question
            # This includes: adequate OR (inadequate + already rephrased)
            print(f"[DEBUG] Decision: IS_ADEQUATE or IS_REPHRASED → NEW QUESTION")
            print(f"[DEBUG] ========================================\n")
            return self._ask_new_question(evaluation, is_adequate)
    
    def _rephrase_current_question(self, evaluation):
        """Rephrase SAME question"""
        rephrase_data = self._rephrase_question(self.current_question)
        encouragement = get_encouragement_message("rephrase", evaluation['score'])
        
        self.current_question = rephrase_data['rephrased_question']
        self.is_rephrased = True  # CRITICAL
        
        message = f"{encouragement} {rephrase_data['rephrased_question']}"
        
        return {
            "is_inadequate": True,
            "score_out_of_10": evaluation['score'],
            "evaluation_reason": evaluation['reason'],
            "question": message,
            "is_rephrased": True,
            "action": "inadequate_first_time"
        }
    
    def _ask_new_question(self, evaluation, is_adequate):
        """Ask NEW question with score-based acknowledgment"""
        question_data = self._generate_new_question(evaluation['score'])
        
        self.current_question = question_data['question']
        self.is_rephrased = False  # RESET
        self.total_score += evaluation['score']
        self.question_count += 1
        self.asked_questions.append(question_data['question'])
        
        if is_adequate:
            action = "adequate_response"
            # Score-based acknowledgment
            acknowledgment = get_encouragement_message("adequate", evaluation['score'])
            message = f"{acknowledgment} {question_data['question']}"
        else:
            action = "inadequate_move_on"
            encouragement = get_encouragement_message("move_on", evaluation['score'])
            message = f"{encouragement} {question_data['question']}"
        
        return {
            "is_inadequate": not is_adequate,
            "score_out_of_10": evaluation['score'],
            "evaluation_reason": evaluation['reason'],
            "question": message,
            "is_rephrased": False,
            "action": action
        }
    
    def get_summary(self):
        """Get summary"""
        return {
            "total_score": self.total_score,
            "question_count": self.question_count,
            "current_round": self.current_round
        }


# Global instances
_bot_instances = {}


def get_aikam_response(session_id, job_description, resume, question_type, user_answer):
    """Main function for backend integration"""
    if session_id not in _bot_instances:
        _bot_instances[session_id] = AikamInterviewBot(job_description, resume)
    
    bot = _bot_instances[session_id]
    return bot.process_turn(user_answer)


def clear_session(session_id):
    """Clear session"""
    if session_id in _bot_instances:
        del _bot_instances[session_id]


if __name__ == "__main__":
    print("Production-ready interview bot")
    print("For Streamlit UI: streamlit run app.py")
