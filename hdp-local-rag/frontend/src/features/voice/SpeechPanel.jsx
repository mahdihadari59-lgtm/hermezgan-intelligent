import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useSpeech } from "@hooks/useSpeech";
import { useAssistantStore } from "@stores/assistant.store";
import { Card, CardContent, CardHeader, CardTitle } from "@components/common/Card";
import { VoiceButton } from "./VoiceButton";
import { VoiceWave } from "./VoiceWave";
import { Mic, MessageSquare, RotateCcw } from "lucide-react";

export function SpeechPanel() {
  const { isListening, voiceText } = useSpeech();
  const { processing } = useAssistantStore();
  const [history, setHistory] = useState([]);

  const handleTranscript = (text) => {
    setHistory((prev) => [...prev, { text, timestamp: Date.now() }]);
  };

  return (
    <Card className="overflow-hidden">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-base">
          <Mic className="h-5 w-5 text-teal-500" />
          دستیار صوتی
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Voice button center */}
        <div className="flex flex-col items-center gap-4 py-4">
          <VoiceButton onTranscript={handleTranscript} size="lg" />
          <VoiceWave isActive={isListening} color="red" />

          <AnimatePresence>
            {voiceText && (
              <motion.p
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="text-sm text-center text-muted-foreground max-w-xs"
              >
                {voiceText}
              </motion.p>
            )}
          </AnimatePresence>

          {processing && (
            <p className="text-xs text-teal-600 animate-pulse">
              در حال پردازش...
            </p>
          )}
        </div>

        {/* History */}
        {history.length > 0 && (
          <div className="border-t pt-3">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-muted-foreground">تاریخچه</span>
              <button
                onClick={() => setHistory([])}
                className="text-xs text-teal-600 hover:underline"
              >
                پاک کردن
              </button>
            </div>
            <div className="space-y-2 max-h-32 overflow-y-auto">
              {history.slice(-5).map((item, idx) => (
                <div
                  key={item.timestamp}
                  className="flex items-start gap-2 text-xs"
                >
                  <MessageSquare className="h-3 w-3 mt-0.5 text-teal-500 shrink-0" />
                  <span className="text-muted-foreground">{item.text}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
