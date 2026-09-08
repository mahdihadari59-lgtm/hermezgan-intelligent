import { useState, useCallback, useRef } from "react";
import { speechApi } from "@api/speech.api";
import { useAssistantStore } from "@stores/assistant.store";

export function useSpeech() {
  const store = useAssistantStore();
  const [isSupported, setIsSupported] = useState(
    "SpeechRecognition" in window || "webkitSpeechRecognition" in window
  );
  const recognitionRef = useRef(null);

  const startListening = useCallback(() => {
    if (!isSupported) return false;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.lang = "fa-IR";
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = (event) => {
      const lastResult = event.results[event.results.length - 1];
      const transcript = lastResult[0].transcript;
      store.setVoiceText(transcript);
    };

    recognition.onerror = (event) => {
      console.error("Speech error:", event.error);
      store.setIsListening(false);
    };

    recognition.onend = () => {
      if (store.isListening) {
        recognition.start();
      }
    };

    recognition.start();
    recognitionRef.current = recognition;
    store.setIsListening(true);
    return true;
  }, [isSupported, store]);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }
    store.setIsListening(false);
  }, [store]);

  const transcribeAudio = useCallback(async (audioBlob, options = {}) => {
    store.setProcessing(true);
    try {
      const result = await speechApi.transcribe(audioBlob, options);
      return result;
    } catch (error) {
      console.error("Transcribe error:", error);
      throw error;
    } finally {
      store.setProcessing(false);
    }
  }, [store]);

  const processAudio = useCallback(async (audioBlob, options = {}) => {
    store.setProcessing(true);
    try {
      const result = await speechApi.process(audioBlob, options);
      return result;
    } catch (error) {
      console.error("Process error:", error);
      throw error;
    } finally {
      store.setProcessing(false);
    }
  }, [store]);

  return {
    isSupported,
    isListening: store.isListening,
    voiceText: store.voiceText,
    processing: store.processing,
    startListening,
    stopListening,
    transcribeAudio,
    processAudio,
  };
}
