import os
import sys
import json
import logging
from typing import Dict, List, Optional, Any

from openai import AzureOpenAI
from dotenv import load_dotenv


load_dotenv()

endpoint = os.getenv(
    "AZUREAI_ENDPOINT_URL", "https://cardwatch-reporting-ai.openai.azure.com/"
)
deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")

azure_openai = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=subscription_key,
    api_version="2024-10-01-preview",
)


def get_ai_prompt_response(data):
    """
    Generate a structured JSON report based on dietary data using the OpenAI model.
    This format is meant for the PDF report format.
    """
    with open("services/templates/response_format.json", "r") as f:
        response_format = f.read()

    response_format_str = str(response_format)

    response = azure_openai.chat.completions.create(
        model=deployment,
        temperature=0.3,  # Lower temperature for more consistent results
        messages=[
            {
                "role": "system",
                "content": f"Given some dietary data you generate a report summarizing the user's caloric and \
                            nutritional intake. Assess if they are at risk of common dietary concerns based on \
                            their allergies and risk factors. The response should only contain a json object following the \
                            format of the template provided below. Replace all placeholder values with data gathered from the \
                            data provided by the user. If no data is available, replace empty fields with 'na' \
                            and ensure valid json in the response. Template: {response_format_str}",
            },
            {"role": "user", "content": str(data)},
        ],
    )

    return response.choices[0].message.content


def get_ai_analysis(data):
    """
    Generate a comprehensive analysis and recommendations for the dashboard display.
    Includes nutritional analysis, recommendations, and health insights.
    """
    system_prompt = """
    You are a nutrition expert assistant helping dietitians analyze patient nutritional data. 
    Given the patient's dietary information, allergies, and nutrient targets, provide a comprehensive analysis 
    with the following sections:
    
    1. SUMMARY: A concise overview of the patient's nutritional status (2-3 sentences)
    2. ANALYSIS: Detailed analysis of nutrient intake compared to targets
    3. RECOMMENDATIONS: Specific dietary recommendations based on the data
    4. HEALTH_INSIGHTS: Potential health implications based on allergies and nutritional patterns
    
    Format your response as a JSON object with these four fields. Be precise, professional, and actionable.
    If data is insufficient for certain sections, note this in your response. Do not return nested JSON in the categories.
    """
    
    try:
        response = azure_openai.chat.completions.create(
            model=deployment,
            temperature=0.4,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": str(data)}
            ],
            response_format={"type": "json_object"}
        )
        
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Error generating dashboard analysis: {str(e)}")
        return '{"SUMMARY": "Unable to generate analysis due to an error.", "ANALYSIS": "", "RECOMMENDATIONS": "", "HEALTH_INSIGHTS": ""}'


class ChatContext:
    """
    Manages conversation context for the AI chat interface.
    Stores message history and patient data context.
    """
    def __init__(self, patient_data: Dict[str, Any]):
        self.patient_data = patient_data
        self.messages: List[Dict[str, str]] = []
        self.system_prompt = self._create_system_prompt()
    
    def _create_system_prompt(self) -> str:
        """Create a system prompt that includes relevant patient context"""
        patient_info = self.patient_data.get('patient_info', {})
        allergies = self.patient_data.get('allergies', [])
        nutrient_targets = self.patient_data.get('nutrient_targets', [])
        
        # Extract basic patient info
        name = f"{patient_info.get('first_name', '')} {patient_info.get('last_name', '')}".strip()
        age = patient_info.get('age', 'unknown')
        gender = patient_info.get('gender', 'unknown')
        
        # Format allergies
        allergy_list = ', '.join([a.get('allergen', '') for a in allergies]) if allergies else "None recorded"
        
        # Format nutrient targets
        target_info = ""
        if nutrient_targets:
            for target in nutrient_targets:
                if isinstance(target, dict):
                    target_info += "- "
                    if 'calories_target' in target:
                        target_info += f"Calories: {target.get('calories_target')} "
                    if 'protein_target' in target:
                        target_info += f"Protein: {target.get('protein_target')}g "
                    if 'carbs_target' in target:
                        target_info += f"Carbs: {target.get('carbs_target')}g "
                    if 'fat_target' in target:
                        target_info += f"Fat: {target.get('fat_target')}g "
                    target_info += "\n"
        
        # Create the system prompt with patient context
        return f"""
        You are CardWatch AI, an expert nutrition assistant helping dietitians analyze and provide insights for their patients.
        
        PATIENT CONTEXT:
        - Name: {name}
        - Age: {age}
        - Gender: {gender}
        - Allergies: {allergy_list}
        - Nutrient Targets: 
        {target_info}
        
        As a nutrition expert, your role is to:
        1. Answer questions about the patient's nutritional needs based on their data
        2. Provide scientifically backed nutritional advice
        3. Suggest meal plans and food alternatives appropriate for the patient
        4. Explain nutritional concepts in clear, professional language
        5. Flag potential health concerns based on the nutritional data
        
        Maintain a professional tone suitable for a healthcare professional. 
        Be concise but informative in your responses.
        If you don't have enough information to provide a specific recommendation, acknowledge this limitation 
        and suggest what additional data would be helpful.
        
        Always consider the patient's allergies when making food recommendations.
        """
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history"""
        self.messages.append({"role": role, "content": content})
    
    def get_messages_for_api(self) -> List[Dict[str, str]]:
        """Get messages formatted for the OpenAI API call, including the system prompt"""
        return [{"role": "system", "content": self.system_prompt}] + self.messages
    
    def clear_history(self) -> None:
        """Clear conversation history but keep patient context"""
        self.messages = []


def chat_with_patient_context(
    patient_data: Dict[str, Any],
    message: str,
    chat_history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    Chat with the AI using patient data as context.
    
    Args:
        patient_data: Dictionary containing patient information and nutritional data
        message: The user's message/question
        chat_history: Optional previous chat history
    
    Returns:
        Dictionary containing the AI response and updated chat history
    """
    try:
        # Initialize or update chat context
        if chat_history:
            context = ChatContext(patient_data)
            for msg in chat_history:
                context.add_message(msg["role"], msg["content"])
        else:
            context = ChatContext(patient_data)
        
        # Add the user's new message
        context.add_message("user", message)
        
        # Get response from OpenAI
        response = azure_openai.chat.completions.create(
            model=deployment,
            temperature=0.7,  # Slightly higher temperature for more natural conversation
            messages=context.get_messages_for_api()
        )
        
        # Extract the response content
        ai_response = response.choices[0].message.content
        
        # Add AI response to context
        context.add_message("assistant", ai_response)
        
        # Return response and updated history
        return {
            "response": ai_response,
            "chat_history": context.messages
        }
    
    except Exception as e:
        logging.error(f"Error in chat with patient context: {str(e)}")
        return {
            "response": "I apologize, but I encountered an error processing your request. Please try again or contact support if the issue persists.",
            "chat_history": chat_history or []
        }
