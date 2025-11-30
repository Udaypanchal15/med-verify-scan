"""
LLM Service for medicine information summarization
Uses OpenAI API or local LLM for generating summaries
"""
import os
import openai
from typing import Dict, Any, Optional, List
import json

class LLMService:
    """LLM service for medicine information summarization"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = 'gpt-3.5-turbo'):
        """
        Initialize LLM service
        api_key: OpenAI API key (if None, will try to get from environment)
        model: Model to use (gpt-3.5-turbo, gpt-4, etc.)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model or os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        
        if self.api_key:
            openai.api_key = self.api_key
        else:
            print("Warning: OpenAI API key not provided. LLM features will be disabled.")
    
    def is_available(self) -> bool:
        """Check if LLM service is available"""
        return self.api_key is not None and self.api_key != ""
    
    def summarize_medicine_info(self, medicine_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a summary of medicine information
        Returns structured summary with side effects, dosage, interactions, etc.
        """
        if not self.is_available():
            return self._generate_fallback_summary(medicine_data)
        
        try:
            # Prepare prompt
            prompt = self._create_summary_prompt(medicine_data)
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a medical information assistant. Provide accurate, concise information about medicines."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Parse response
            summary_text = response.choices[0].message.content.strip()
            
            # Parse structured summary
            summary = self._parse_summary(summary_text, medicine_data)
            
            return summary
        except Exception as e:
            print(f"Error generating LLM summary: {e}")
            return self._generate_fallback_summary(medicine_data)
    
    def _create_summary_prompt(self, medicine_data: Dict[str, Any]) -> str:
        """Create prompt for LLM"""
        name = medicine_data.get('name', 'Unknown Medicine')
        dosage = medicine_data.get('dosage', 'Not specified')
        strength = medicine_data.get('strength', 'Not specified')
        description = medicine_data.get('description', '')
        
        prompt = f"""Please provide a concise summary for the following medicine:

Name: {name}
Dosage: {dosage}
Strength: {strength}
Description: {description}

Please provide the following information in a structured format:
1. Brief description of what this medicine is used for
2. Common side effects (list 3-5 most common)
3. Important drug interactions (list 2-3 most important)
4. Contraindications (who should not take this medicine)
5. Dosage instructions (when and how to take)

Format the response as a JSON object with the following keys:
- description
- side_effects (array)
- drug_interactions (array)
- contraindications (array)
- dosage_instructions

Be concise and accurate. Only include information that is commonly known about this type of medicine."""
        
        return prompt
    
    def _parse_summary(self, summary_text: str, medicine_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        try:
            # Try to parse as JSON
            if summary_text.startswith('{'):
                summary = json.loads(summary_text)
            else:
                # If not JSON, create structured summary from text
                summary = self._extract_from_text(summary_text)
        except json.JSONDecodeError:
            # Fallback to text extraction
            summary = self._extract_from_text(summary_text)
        
        # Add source information
        summary['source'] = 'llm'
        summary['medicine_name'] = medicine_data.get('name', 'Unknown')
        summary['model'] = self.model
        
        return summary
    
    def _extract_from_text(self, text: str) -> Dict[str, Any]:
        """Extract structured information from text response"""
        summary = {
            'description': '',
            'side_effects': [],
            'drug_interactions': [],
            'contraindications': [],
            'dosage_instructions': ''
        }
        
        # Simple text parsing (can be improved)
        lines = text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect sections
            if 'description' in line.lower() or 'used for' in line.lower():
                current_section = 'description'
            elif 'side effects' in line.lower():
                current_section = 'side_effects'
            elif 'interactions' in line.lower():
                current_section = 'drug_interactions'
            elif 'contraindications' in line.lower() or 'should not' in line.lower():
                current_section = 'contraindications'
            elif 'dosage' in line.lower() or 'instructions' in line.lower():
                current_section = 'dosage_instructions'
            
            # Extract content
            if current_section:
                if current_section in ['side_effects', 'drug_interactions', 'contraindications']:
                    if line.startswith('-') or line.startswith('•'):
                        item = line.lstrip('- •').strip()
                        if item:
                            summary[current_section].append(item)
                else:
                    if summary[current_section]:
                        summary[current_section] += ' ' + line
                    else:
                        summary[current_section] = line
        
        return summary
    
    def _generate_fallback_summary(self, medicine_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback summary when LLM is not available"""
        name = medicine_data.get('name', 'Unknown Medicine')
        
        # Use predefined knowledge base
        medicine_knowledge = {
            "Paracetamol": {
                "description": "Paracetamol is a common pain reliever and fever reducer.",
                "side_effects": ["Nausea", "Rash", "Headache", "Liver damage in overdose"],
                "drug_interactions": ["Avoid alcohol", "Avoid other hepatotoxic drugs"],
                "contraindications": ["Severe liver disease", "Allergy to paracetamol"],
                "dosage_instructions": "500mg every 4-6 hours, max 4g per day"
            },
            "Ibuprofen": {
                "description": "Ibuprofen is a non-steroidal anti-inflammatory drug (NSAID) used for pain and inflammation.",
                "side_effects": ["Stomach pain", "Heartburn", "Dizziness", "Increased bleeding risk"],
                "drug_interactions": ["Avoid other NSAIDs", "Avoid blood thinners"],
                "contraindications": ["Peptic ulcer", "Severe heart failure", "Allergy to NSAIDs"],
                "dosage_instructions": "200-400mg every 4-6 hours, max 1200mg per day OTC"
            }
        }
        
        # Check if medicine is in knowledge base
        medicine_name = name.lower()
        for key, value in medicine_knowledge.items():
            if key.lower() in medicine_name or medicine_name in key.lower():
                summary = value.copy()
                summary['source'] = 'knowledge_base'
                summary['medicine_name'] = name
                return summary
        
        # Default summary
        return {
            'description': f"{name} is a medicine. Please consult a healthcare professional for detailed information.",
            'side_effects': ["Consult healthcare professional for side effects"],
            'drug_interactions': ["Consult healthcare professional for drug interactions"],
            'contraindications': ["Consult healthcare professional for contraindications"],
            'dosage_instructions': medicine_data.get('dosage', 'Consult healthcare professional for dosage instructions'),
            'source': 'fallback',
            'medicine_name': name
        }
    
    def generate_ai_summary(self, medicine_data: Dict[str, Any]) -> str:
        """
        Generate a human-readable AI summary of medicine information
        Returns formatted text summary
        """
        summary = self.summarize_medicine_info(medicine_data)
        
        # Format as readable text
        text_summary = f"""**{summary.get('medicine_name', 'Medicine')}**

**Description:**
{summary.get('description', 'No description available')}

**Side Effects:**
{', '.join(summary.get('side_effects', [])) if summary.get('side_effects') else 'None listed'}

**Drug Interactions:**
{', '.join(summary.get('drug_interactions', [])) if summary.get('drug_interactions') else 'None listed'}

**Contraindications:**
{', '.join(summary.get('contraindications', [])) if summary.get('contraindications') else 'None listed'}

**Dosage Instructions:**
{summary.get('dosage_instructions', 'Consult healthcare professional')}
"""
        
        return text_summary



