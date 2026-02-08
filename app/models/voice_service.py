"""
Voice Service: Speech Recognition and Text-to-Speech
Handles voice input and output with improved audio quality
"""

import speech_recognition as sr
import pyttsx3
import time


class VoiceService:
    """Service for voice recognition and text-to-speech with enhanced audio processing"""
    
    def __init__(self, pause_threshold: float = 2.0, timeout: int = 10):
        """
        Initialize voice service with optimized settings
        
        Args:
            pause_threshold: Seconds of silence before considering speech complete
            timeout: Maximum seconds to wait for speech
        """
        self.recognizer = sr.Recognizer()
        
        # Optimized audio settings for better recognition
        self.recognizer.pause_threshold = pause_threshold  # Reduced to 2 seconds
        self.recognizer.phrase_threshold = 0.3  # Minimum seconds of speaking audio
        self.recognizer.non_speaking_duration = 0.5  # Seconds of silence for phrase end
        
        # Dynamic energy threshold (auto-adjusts to ambient noise)
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = 300  # Lower for better sensitivity
        
        self.timeout = timeout
        
        # Initialize text-to-speech engine
        self.tts_engine = pyttsx3.init()
        self._configure_tts()
    
    def _configure_tts(self):
        """Configure TTS for better quality"""
        try:
            # Set speech rate (words per minute)
            self.tts_engine.setProperty('rate', 165)
            
            # Set volume
            self.tts_engine.setProperty('volume', 0.95)
            
            # Try to set a better voice if available
            voices = self.tts_engine.getProperty('voices')
            if len(voices) > 0:
                # Prefer English voices
                for voice in voices:
                    if 'english' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
        except Exception as e:
            print(f"⚠️  TTS configuration warning: {e}")
    
    def listen(self) -> tuple[bool, str]:
        """
        Listen for voice input with improved audio processing
        
        Returns:
            tuple: (success, message/error)
        """
        try:
            with sr.Microphone(sample_rate=16000) as source:
                print("🎤 Calibrating microphone...")
                # Longer calibration for better ambient noise adjustment
                self.recognizer.adjust_for_ambient_noise(source, duration=1.5)
                
                print("✅ Ready! Speak now...")
                print(f"   (Will auto-send after {self.recognizer.pause_threshold}s of silence)")
                
                # Listen with timeout
                audio = self.recognizer.listen(
                    source,
                    timeout=self.timeout,
                    phrase_time_limit=30  # Max 30 seconds of speech
                )
                
                print("🔄 Processing speech...")
                
                # Try multiple recognition methods for better accuracy
                text = self._recognize_speech(audio)
                
                if text:
                    print(f"✅ Recognized: {text}")
                    return True, text
                else:
                    return False, "Could not understand audio. Please speak clearly."
                
        except sr.WaitTimeoutError:
            return False, f"No speech detected within {self.timeout} seconds. Try speaking louder."
        except sr.UnknownValueError:
            return False, "Could not understand audio. Please speak more clearly and try again."
        except sr.RequestError as e:
            return False, f"Recognition service error: {e}. Check your internet connection."
        except OSError as e:
            error_msg = str(e)
            if "No Default Input" in error_msg or "not found" in error_msg:
                return False, "No microphone detected. Please connect a microphone and try again."
            return False, f"Microphone error: {e}"
        except Exception as e:
            return False, f"Unexpected error: {e}"
    
    def _recognize_speech(self, audio) -> str:
        """
        Recognize speech using multiple methods for best results
        
        Args:
            audio: Audio data to recognize
            
        Returns:
            str: Recognized text or empty string
        """
        # Try Google Speech Recognition (free, good quality)
        try:
            text = self.recognizer.recognize_google(audio, language='en-US')
            return text
        except sr.UnknownValueError:
            pass
        except sr.RequestError:
            pass
        
        # Fallback: Try Sphinx (offline, lower quality but works without internet)
        try:
            text = self.recognizer.recognize_sphinx(audio)
            return text
        except:
            pass
        
        return ""
    
    def speak(self, text: str) -> bool:
        """
        Speak the given text with better quality
        
        Args:
            text: Text to speak
            
        Returns:
            bool: Success status
        """
        try:
            if not text or not text.strip():
                return False
            
            print(f"🔊 Speaking: {text[:100]}...")
            
            # Clear any pending speech
            if self.tts_engine._inLoop:
                self.tts_engine.endLoop()
            
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            
            print("✅ Speech complete")
            return True
            
        except Exception as e:
            print(f"❌ TTS Error: {e}")
            return False
    
    def test_microphone(self) -> tuple[bool, str]:
        """
        Test if microphone is working
        
        Returns:
            tuple: (success, message)
        """
        try:
            with sr.Microphone() as source:
                print("🎤 Testing microphone...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=3)
                return True, "Microphone is working!"
        except Exception as e:
            return False, f"Microphone test failed: {e}"
    
    def list_microphones(self) -> list:
        """
        List available microphones
        
        Returns:
            list: Available microphone names
        """
        try:
            return sr.Microphone.list_microphone_names()
        except Exception as e:
            print(f"Error listing microphones: {e}")
            return []
    
    def set_microphone(self, device_index: int):
        """
        Set specific microphone device
        
        Args:
            device_index: Index of microphone to use
        """
        try:
            with sr.Microphone(device_index=device_index) as source:
                print(f"✅ Microphone {device_index} selected")
        except Exception as e:
            print(f"❌ Could not set microphone: {e}")
    
    def set_voice(self, voice_index: int = 0):
        """
        Set TTS voice
        
        Args:
            voice_index: Index of the voice (0=default, 1=alternative)
        """
        try:
            voices = self.tts_engine.getProperty('voices')
            if 0 <= voice_index < len(voices):
                self.tts_engine.setProperty('voice', voices[voice_index].id)
                print(f"✅ Voice set to: {voices[voice_index].name}")
        except Exception as e:
            print(f"⚠️  Could not set voice: {e}")
    
    def set_rate(self, rate: int):
        """
        Set speech rate
        
        Args:
            rate: Words per minute (recommended: 150-200)
        """
        self.tts_engine.setProperty('rate', max(100, min(300, rate)))
    
    def set_volume(self, volume: float):
        """
        Set volume
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.tts_engine.setProperty('volume', max(0.0, min(1.0, volume)))

