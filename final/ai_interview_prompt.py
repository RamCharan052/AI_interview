"""
AI Interview Prompt
- Balanced evaluation
- Professional rephrasing
- Round-specific questions
- Dynamic acknowledgments
"""

def get_evaluation_prompt(question, answer, job_description, resume):
    """
    Evaluate answer - BALANCED (not too strict, not too lenient)
    """
    prompt = f"""You are a professional interview evaluator. Evaluate this answer fairly.

Question: "{question}"
Candidate Answer: "{answer}"

MARK AS INADEQUATE (is_adequate: false) ONLY if answer has ANY of these:
1. Single word responses: "No", "Yes", "Pass", "Skip", "ok", "yeah", "idk"
2. Explicit non-answers: "I don't know", "Not sure", "Can't answer", "skip this"
3. Vague/meaningless phrases with NO substance: "it is what it is", "you overcome by doing that", "challenges are challenges"
4. Incomplete trailing off: "recently i learned that", "troubleshooting does what"
5. Less than 10 meaningful words
6. Just repeats the question without answering
7. Complete gibberish or totally unrelated

MARK AS ADEQUATE (is_adequate: true) if answer has ANY of:
- Multiple sentences with relevant content
- Specific technologies, projects, or examples mentioned
- Clear attempt to address the question
- Professional background or experience described
- Any meaningful details about skills or work

SCORING GUIDELINES (Be FAIR and BALANCED):
- Score 1-2: Non-answers, gibberish, single words
- Score 3-4: Vague or very brief (under 20 words)
- Score 5-6: Basic adequate - addresses question with some detail
- Score 7-8: Good - clear details, examples, relevant content
- Score 9-10: Excellent - comprehensive, well-structured, impressive

EXAMPLES:
❌ INADEQUATE: "nothing much", "idk", "you overcome by doing that" (vague, meaningless)
✅ ADEQUATE: "I'm a Python developer with 5 years experience in Django" (has substance)
✅ ADEQUATE: "I worked at X company where I built APIs using FastAPI" (specific details)
✅ ADEQUATE: Any answer with 20+ words that addresses the question

BE GENEROUS: If candidate puts in effort and provides relevant info, mark adequate.

Job Description: {job_description}
Resume: {resume}

Respond with ONLY valid JSON (no markdown):
{{"is_adequate": true, "score": 7, "reason": "Brief reason"}}"""

    return prompt


def get_rephrase_prompt(question):
    """
    Rephrase question - Professional, clearer
    """
    prompt = f"""Rephrase this interview question to be clearer and simpler.

Original Question: "{question}"

Requirements:
1. Use simpler, everyday language
2. Break down complex terms
3. Keep it professional
4. NO examples, NO "imagine" scenarios
5. Same topic, just clearer
6. Maximum 2 sentences

Respond with ONLY valid JSON (no markdown):
{{"rephrased_question": "Your clearer question"}}"""

    return prompt


def get_new_question_prompt(round_type, job_description, resume, asked_questions):
    """
    Generate NEW question - Must be DIFFERENT from previous
    """
    asked_list = ""
    if asked_questions:
        asked_list = "\n".join([f"- {q}" for q in asked_questions[-8:]])
    
    # Round-specific instructions
    round_instructions = {
        "HR": """Generate a BEHAVIORAL/SITUATIONAL question about:
- Teamwork and collaboration
- Handling conflict or pressure
- Time management and prioritization
- Career goals and motivation
- Communication with non-technical people
- Work style preferences
- Leadership or mentoring

DO NOT ask technical questions or about resume/job specifics.""",

        "Resume Validation": f"""Generate a question about SPECIFIC items from resume.

Resume: {resume}

Ask about:
- Specific projects they mentioned
- Technologies/tools they claim to know
- Their role in past jobs
- Achievements or results
- How they learned specific skills

Pick ONE specific item from their resume and ask them to elaborate.""",

        "JD Fitment": f"""Generate a question matching JOB REQUIREMENTS.

Job Description: {job_description}

Ask about:
- Specific technical skills from JD
- Experience with JD technologies
- How they'd handle job-specific scenarios
- Problem-solving for role requirements

Focus on job-specific technical abilities.""",

        "Personality Assessment": """Generate a question about PERSONALITY/VALUES:
- How they handle feedback
- Ideal work environment
- Staying motivated
- Learning style
- Handling stress
- Team preferences
- Long-term goals

Focus on personality, NOT technical skills."""
    }
    
    instruction = round_instructions.get(round_type, round_instructions["HR"])
    
    prompt = f"""Generate a NEW {round_type} interview question.

{instruction}

ALREADY ASKED (DO NOT REPEAT or ask similar):
{asked_list if asked_list else "None yet"}

CRITICAL RULES:
1. Ask about COMPLETELY DIFFERENT topic than previous questions
2. DO NOT start with "The job description mentions..." or "On your resume..."
3. Start directly with the question
4. Keep question simple and clear (1-2 sentences)

ACKNOWLEDGMENT:
5. Generate a SHORT (4-7 words), UNIQUE, WARM acknowledgment
6. Use varied phrases like: "Excellent!", "That's really helpful!", "Great example!", "Perfect, thank you!", "Fantastic!", "Wonderful!", "Got it, thanks!", "Understood!", "Brilliant!", "Impressive!"
7. Make it sound NATURAL and WARM, not robotic
8. VARY the phrase each time - generate different acknowledgment every time

Respond with ONLY valid JSON (no markdown):
{{"acknowledgment": "Excellent! That's really insightful.", "question": "Your NEW question"}}"""

    return prompt


def get_start_interview_prompt():
    """Starting question"""
    return "Let's begin the interview. Can you please introduce yourself and tell me about your background?"


def get_encouragement_message(context="move_on"):
    """Encouragement messages"""
    import random
    
    if context == "rephrase":
        messages = [
            "Let me rephrase that.",
            "Let me ask that differently.",
            "Here's a simpler way to phrase it.",
            "Let me make this clearer.",
            "Allow me to clarify."
        ]
    elif context == "move_on":
        messages = [
            "That's okay! Let's move on.",
            "No problem! Next question.",
            "All good! Let's try something else.",
            "That's fine! Moving forward.",
            "No worries! Here's another one."
        ]
    elif context == "empty":
        messages = [
            "No worries! Let's try another.",
            "That's fine! Next question.",
            "All good! Here's a different one.",
            "No problem! Let's continue.",
            "That's okay! Moving on."
        ]
    else:
        messages = ["Great!"]
    
    return random.choice(messages)