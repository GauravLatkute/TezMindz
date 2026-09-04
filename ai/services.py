import os
from django.conf import settings
try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

class AIService:
    @staticmethod
    def _get_client():
        api_key = getattr(settings, "GEMINI_API_KEY", None)
        if not api_key or not genai:
            return None
        try:
            return genai.Client(api_key=api_key)
        except Exception as e:
            print("Failed to initialize Gemini Client:", e)
            return None

    @classmethod
    def _generate(cls, prompt: str, system_instruction: str) -> str:
        client = cls._get_client()
        if not client:
            # Safe local mockup callback for development if API key is not configured
            return f"[Dev Mode Mockup Explanation]\n\nPrompt: {prompt[:80]}...\n\n(To retrieve real AI results, configure GEMINI_API_KEY in backend/.env)"

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7,
                )
            )
            return response.text
        except Exception as e:
            return f"Tutoring assistant is currently resting. Concept Hint: Review rules. (Error: {str(e)})"

    @classmethod
    def get_system_instruction(cls, student_class) -> str:
        grade = student_class.grade_number
        base_instruction = (
            "You are TezGPT, an AI-powered expert Olympiad Learning assistant on the TezMindz EdTech platform. "
            "Your goal is to guide students to understand concepts deeply, not just give away direct answers."
        )

        if grade <= 5:
            # Cartoon style primary analogies
            return base_instruction + (
                "\n\nClass Context: The student is in Class 5 or below (elementary level).\n"
                "Constraints:\n"
                "1. Use simple vocabulary suitable for a 10-year-old.\n"
                "2. Explain using fun everyday analogies like candy, chocolates, sports, toys, or playground games.\n"
                "3. Keep paragraphs short (maximum 2 sentences per paragraph).\n"
                "4. Use visual formatting like bullet points and occasional fun emojis."
            )
        else:
            # Analytical senior style
            return base_instruction + (
                "\n\nClass Context: The student is in Class 8 or similar senior level.\n"
                "Constraints:\n"
                "1. Use precise academic vocabulary and formal reasoning.\n"
                "2. Show formulas, fractions, and symbols clearly.\n"
                "3. Explain step-by-step logic, helping them understand underlying properties and theorems."
            )

    @classmethod
    def explain_concept(cls, concept_name: str, description: str, student_class) -> str:
        prompt = (
            f"Explain the concept '{concept_name}' which is defined as: '{description}'.\n"
            "Provide a short explanation, a real-world example, and a simple analogy."
        )
        system_instruction = cls.get_system_instruction(student_class)
        return cls._generate(prompt, system_instruction)

    @classmethod
    def explain_wrong_answer(cls, question_text: str, incorrect_option: str, correct_option: str, student_class) -> str:
        prompt = (
            f"A student was asked: '{question_text}'\n"
            f"The correct option is: '{correct_option}'\n"
            f"The student incorrectly chose: '{incorrect_option}'\n"
            "Diagnose the potential misconception in their wrong answer without saying 'You are wrong' or calling them silly. "
            "Explain step-by-step why the correct option makes sense and how they can correct their thinking."
        )
        system_instruction = cls.get_system_instruction(student_class)
        return cls._generate(prompt, system_instruction)

    @classmethod
    def generate_smart_hint(cls, question_text: str, options: list, student_class, attempts_so_far: int) -> str:
        options_text = ", ".join(options)
        prompt = (
            f"The question is: '{question_text}'\n"
            f"The choices are: [{options_text}]\n"
            f"This is the student's request for Hint #{attempts_so_far + 1}.\n"
            "Write a helpful, encouraging clue. DO NOT reveal the correct option directly or eliminate choices. "
            "Instead, guide them to examine the problem properties (like denominator, numerator, word rules)."
        )
        system_instruction = cls.get_system_instruction(student_class)
        return cls._generate(prompt, system_instruction)
