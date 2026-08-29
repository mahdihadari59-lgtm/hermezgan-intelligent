import { useState, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useSpeech } from "@hooks/useSpeech";
import { useVoice } from "@hooks/useVoice";
import { useAssistantStore } from "@stores/assistant.store";
import { Button } from "@components/common/Button";
import { Mic, MicOff, Loader2 } from "lucide-react";

export function VoiceButton({ onTranscript, size = "default" }) {
  const { isSupported, isListening, voiceText, startListening, stopListening, processAudio } = useSpeech();
  const { speak } = useVoice();
  const { processing } = useAssistantStore();
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const handleToggle = useCallback(async () => {
    if (isListening) {
      // Stop recording
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
        mediaRecorderRef.current.stop();
      }
      stopListening();
    } else {
      // Start recording
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        audioChunksRef.current = [];

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            audioChunksRef.current.push(event.data);
          }
        };

        mediaRecorder.onstop = async () => {
          const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
          try {
            const result = await processAudio(audioBlob, {
              returnAudio: true,
              useBandari: true,
            });

            if (result.response_text) {
              onTranscript?.(result.response_text);
            }

            if (result.audio) {
              await speak(result.response_text || "پاسخ دریافت شد", { returnAudio: true });
            }
          } catch (error) {
            console.error("Voice processing error:", error);
          }

          stream.getTracks().forEach((track) => track.stop());
        };

        mediaRecorderRef.current = mediaRecorder;
        mediaRecorder.start();
        startListening();
      } catch (error) {
        console.error("Microphone access error:", error);
      }
    }
  }, [isListening, startListening, stopListening, processAudio, speak, onTranscript]);

  if (!isSupported) {
    return null;
  }

  const sizeClasses = {
    default: "h-12 w-12",
    sm: "h-9 w-9",
    lg: "h-16 w-16",
  };

  return (
    <div className="relative">
      <Button
        variant={isListening ? "default" : "outline"}
        size="icon"
        onClick={handleToggle}
        disabled={processing}
        className={`${sizeClasses[size]} rounded-full ${
          isListening ? "bg-red-500 hover:bg-red-600 animate-pulse" : ""
        }`}
      >
        {processing ? (
          <Loader2 className="h-5 w-5 animate-spin" />
        ) : isListening ? (
          <MicOff className="h-5 w-5" />
        ) : (
          <Mic className="h-5 w-5" />
        )}
      </Button>

      {/* Voice wave animation */}
      <AnimatePresence>
        {isListening && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="absolute -bottom-8 left-1/2 -translate-x-1/2 flex gap-0.5"
          >
            {[...Array(5)].map((_, i) => (
              <motion.div
                key={i}
                animate={{ height: [4, 12 + Math.random() * 8, 4] }}
                transition={{ duration: 0.5, repeat: Infinity, delay: i * 0.1 }}
                className="w-1 rounded-full bg-red-500"
              />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
