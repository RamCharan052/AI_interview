"""
AI Interview Prompt - Updated per team lead feedback
- Elaborated scoring guidelines
- Removed strict inadequate criteria
- More lenient evaluation
"""

def get_evaluation_prompt(question, answer, job_description, resume):
    """
    Evaluate answer - LENIENT (focus on intent and effort)
    """
    prompt = f"""You are a professional interview evaluator. Evaluate this answer with focus on candidate's intent and effort.

Question: "{question}"
Candidate Answer: "{answer}"

EVALUATION PHILOSOPHY:
Mark as ADEQUATE (is_adequate: true) if answer shows ANY of:
- ANY attempt to address the question (even brief)
- Shows understanding or relevant thought
- Contains any relevant information
- Demonstrates effort to engage with the question
- Has some connection to the topic

Mark as INADEQUATE (is_adequate: false) ONLY if:
- Complete gibberish or random characters
- Totally unrelated to the question with zero connection
- No effort or intent to answer at all

IMPORTANT: Even short answers like "No", "Yes", "I don't know", "it is what it is" should be marked ADEQUATE (is_adequate: true) 
but given appropriate low scores. The goal is to move forward with the interview, not block it.

SCORING GUIDELINES (Detailed and Elaborated):

Score 0:
- Completely blank/empty response
- Pure gibberish with no meaning
- Random characters or symbols only

Score 1-2: Minimal Effort
- Single word responses: "No", "Yes", "ok", "yeah"
- Non-committal: "I don't know", "Not sure", "Maybe"
- Very vague: "it is what it is", "nothing much"
- Shows almost no effort but has some intent
- Answer is extremely brief (under 5 words)

Score 3-4: Poor Response
- Vague or unclear statements
- Incomplete thoughts that trail off
- Answers that barely touch the topic
- Very brief (5-15 words) without substance
- Shows some intent but lacks detail
- Partially relevant but doesn't address core question

Score 5-6: Basic/Adequate Response
- Addresses the question with some relevance
- Provides basic information (20-30 words)
- Shows understanding but lacks depth
- Has some specific details but limited
- Demonstrates effort to answer properly
- Somewhat relevant with minimal examples

Score 7-8: Good Response
- Clear and relevant answer
- Provides specific details or examples
- Well-structured thoughts (30-60 words)
- Shows good understanding
- Includes context or reasoning
- Addresses question directly with substance

Score 9-10: Excellent Response
- Comprehensive and detailed answer
- Multiple specific examples or scenarios
- Well-articulated thoughts (60+ words)
- Shows deep understanding and expertise
- Provides context, reasoning, and outcomes
- Impressive depth and clarity

BE LENIENT: Focus on whether candidate is trying to engage, not perfection. 
Even weak attempts should be marked ADEQUATE with appropriate low scores.

Job Description: {job_description}
Resume: {resume}

Respond with ONLY valid JSON (no markdown):
{{"is_adequate": true, "score": 5, "reason": "Brief reason for the score"}}"""

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


def get_encouragement_message(context="move_on", score=0):
    """
    Encouragement messages based on context and score
    """
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
    elif context == "adequate":
        # Score-based acknowledgments for adequate responses
        if score >= 8:
            messages = [
                "Excellent! That's impressive.",
                "Outstanding answer!",
                "Fantastic! Very well explained.",
                "Brilliant response!",
                "Perfect! That's exactly right."
            ]
        elif score >= 5:
            messages = [
                "Great, thanks for sharing!",
                "Good answer!",
                "That's helpful, appreciate it!",
                "Nice, thank you!",
                "Understood, thanks!"
            ]
        else:
            messages = [
                "Got it, thanks.",
                "Okay, understood.",
                "I see, thank you.",
                "Alright, thanks.",
                "Noted, appreciate it."
            ]
    else:
        messages = ["Great!"]
    
    return random.choice(messages)