"""
Chat service module
Handles AI chat functionality
"""
import logging
from services.prompt import chat_with_patient_context

def process_chat_message(patient_data, patient_id, message, chat_history=None):
    """
    Process a chat message with patient context
    
    Args:
        patient_data: The patient data for context
        patient_id: ID of the patient
        message: The message from the dietitian
        chat_history: Optional chat history
        
    Returns:
        Dictionary with response and updated chat history
    """
    logger = logging.getLogger(__name__)
    
    if chat_history is None:
        chat_history = []
    
    logger.info(f"Processing chat message for patient {patient_id}: {message[:50]}...")
    
    try:
        # Get response from AI
        chat_response = chat_with_patient_context(
            patient_data=patient_data,
            message=message,
            chat_history=chat_history
        )
        
        logger.info(f"Chat response generated successfully")
        
        return {
            "response": chat_response.get("response", ""),
            "chat_history": chat_response.get("chat_history", [])
        }
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise