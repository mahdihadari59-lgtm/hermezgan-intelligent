import { useState, useCallback, useRef } from "react";
import { voiceApi } from "@api/voice.api";
import { useAssistantStore } from "@stores/assistant.store";

export function useVoice() {
  const store = useAssistantStore();
  const audioRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const synthesize = useCallback(async (text, options = {}) => {
    try {
      const result = await voiceApi.synthesize(text, options);

      if (result.audio) {
        const audioUrl = `data:audio/wav;base64,${result.audio}`;
        store.setAudioUrl(audioUrl);
        return audioUrl;
      }

      return null;
    } catch (error) {
      console.error("Synthesize error:", error);
      throw error;
    }
  }, [store]);

  const playAudio = useCallback((audioUrl) => {
    if (audioRef.current) {
      audioRef.current.pause();
    }

    const audio = new Audio(audioUrl);
    audioRef.current = audio;

    audio.onplay = () => {
      setIsPlaying(true);
      store.setIsSpeaking(true);
    };

    audio.onended = () => {
      setIsPlaying(false);
      store.setIsSpeaking(false);
    };

    audio.onerror = () => {
      setIsPlaying(false);
      store.setIsSpeaking(false);
    };

    audio.play();
  }, [store]);

  const stopAudio = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
    setIsPlaying(false);
    store.setIsSpeaking(false);
  }, [store]);

  const speak = useCallback(async (text, options = {}) => {
    try {
      const audioUrl = await synthesize(text, options);
      if (audioUrl) {
        playAudio(audioUrl);
      }
      return audioUrl;
    } catch (error) {
      console.error("Speak error:", error);
      return null;
    }
  }, [synthesize, playAudio]);

  return {
    isPlaying,
    isSpeaking: store.isSpeaking,
    audioUrl: store.audioUrl,
    synthesize,
    playAudio,
    stopAudio,
    speak,
  };
}
