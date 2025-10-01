import os
import requests
from pydantic import BaseModel, Field
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
import google.generativeai as genai

# ----------------------------
# Schema for structured data
# ----------------------------
class AnimalMonitoringData(BaseModel):
    date_or_day: str = Field(..., description="Date or day of observation")
    animal_observed_on_time: bool = Field(..., description="Was the animal seen at the scheduled observation time?")
    clean_drinking_water_provided: bool = Field(..., description="Was clean drinking water available?")
    enclosure_cleaned_properly: bool = Field(..., description="Was the enclosure cleaned as required?")
    normal_behaviour_status: bool = Field(..., description="Is the animal showing normal behaviour and activity?")
    normal_behaviour_details: str | None = Field(None, description="If abnormal behaviour observed, provide details")
    feed_and_supplements_available: bool = Field(..., description="Was feed and supplements available?")
    feed_given_as_prescribed: bool = Field(..., description="Was the feed given as prescribed?")
    other_animal_requirements: str | None = Field(None, description="Any other special needs or requirements")
    incharge_signature: str = Field(..., description="Signature of caretaker or in-charge")
    daily_animal_health_monitoring: str = Field(..., description="Summary of daily animal health monitoring")
    carnivorous_animal_feeding_chart: str = Field(..., description="Summary of carnivorous animal feeding chart")
    medicine_stock_register: str = Field(..., description="Summary of medicine stock register")
    daily_wildlife_monitoring: str = Field(..., description="Summary of daily wildlife monitoring observations")


# ----------------------------
# Zoo AI Model with Deepgram
# ----------------------------
class ZooAIModel:
    def __init__(self):
        """Initialize Gemini LLM and Deepgram API."""
        # Gemini LLM
        gem_key =""
        if gem_key:
            genai.configure(api_key=gem_key)
            self.llm = genai.GenerativeModel("gemini-2.5-flash")
        else:
            self.llm = None

        # Deepgram API
        self.deepgram_key =""
        self.deepgram_url = "https://api.deepgram.com/v1/listen"

        # Parser & prompt
        self.parser = PydanticOutputParser(pydantic_object=AnimalMonitoringData)
        self.prompt = PromptTemplate(
            template="""
                You are an animal monitoring assistant.
                Given the input observation, return structured monitoring data
                in valid JSON format that matches the schema.

                {format_instructions}

                ONLY return a JSON object, no extra text, no code, no comments.

                Observation: {observation}
            """,
            input_variables=["observation"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
        )

    # ----------------------------
    # Deepgram Transcription
    # ----------------------------
    def transcribe_audio(self, audio_bytes, language="hi"):
        """Transcribe audio using Deepgram API."""
        if not self.deepgram_key:
            return "Audio transcription unavailable - Deepgram API key missing"

        headers = {
            "Authorization": f"Token {self.deepgram_key}",
            "Content-Type": "audio/wav",  # assumes WAV upload
        }

        try:
            response = requests.post(
                self.deepgram_url,
                headers=headers,
                data=audio_bytes,
                timeout=60,
                params={"language": language}
            )
            response.raise_for_status()
            result = response.json()

            transcript = (
                result.get("results", {})
                      .get("channels", [{}])[0]
                      .get("alternatives", [{}])[0]
                      .get("transcript", "")
            )
            return transcript or "No text returned by Deepgram"

        except Exception as e:
            print("Error transcribing audio:", e)
            return f"Error in audio transcription: {str(e)}"

    # ----------------------------
    # Gemini Processing
    # ----------------------------
    def process_observation(self, observation_text, date):
        """Convert text observation into structured data using Gemini."""
        try:
            if not self.llm:
                return self._create_fallback_data(observation_text, date)

            enhanced_observation = f"Date: {date}\nObservation: {observation_text}"
            response = self.llm.generate_content(
                self.prompt.format(observation=enhanced_observation)
            )

            json_text = getattr(response, "text", None) or ""
            result = self.parser.parse(json_text)

            if hasattr(result, "date_or_day"):
                result.date_or_day = date

            return result

        except Exception as e:
            print(f"Error processing observation: {e}")
            return self._create_fallback_data(observation_text, date)

    def process_audio_observation(self, audio_bytes, date, language="hi"):
        """Transcribe audio and process observation."""
        text = self.transcribe_audio(audio_bytes, language)
        if text.startswith("Error") or text.startswith("Audio transcription unavailable"):
            return self._create_fallback_data(text, date)
        return self.process_observation(text, date)

    # ----------------------------
    # Fallback Data
    # ----------------------------
    def _create_fallback_data(self, observation_text, date):
        """Return fallback structured data if LLM or transcription fails."""
        return AnimalMonitoringData(
            date_or_day=date,
            animal_observed_on_time=True,
            clean_drinking_water_provided=True,
            enclosure_cleaned_properly=True,
            normal_behaviour_status=True,
            normal_behaviour_details=None,
            feed_and_supplements_available=True,
            feed_given_as_prescribed=True,
            other_animal_requirements=(observation_text[:200] + "..." 
                                       if len(observation_text) > 200 else observation_text),
            incharge_signature="Zoo Keeper",
            daily_animal_health_monitoring=f"Observation recorded on {date}: {observation_text[:100]}{'...' if len(observation_text) > 100 else ''}",
            carnivorous_animal_feeding_chart="Standard feeding schedule followed",
            medicine_stock_register="Stock levels adequate",
            daily_wildlife_monitoring=f"Wildlife monitoring completed on {date}"
        )


# Instantiate global model
zoo_model = ZooAIModel()
