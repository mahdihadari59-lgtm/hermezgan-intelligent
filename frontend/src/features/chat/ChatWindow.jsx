import { useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useChat } from "@hooks/useChat";
import { useAssistantStore } from "@stores/assistant.store";
import { Card, CardContent, CardHeader, CardTitle } from "@components/common/Card";
import { Button } from "@components/common/Button";
import { MessageList } from "./MessageList";
import { ChatInput } from "./ChatInput";
import { Suggestions } from "./Suggestions";
import { VoiceButton } from "@features/voice/VoiceButton";
import { MessageCircle, Trash2, Loader2 } from "lucide-react";

export function ChatWindow() {
  const { messages, isTyping, suggestions, sendMessage, clearHistory } = useChat();
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  return (
    <Card className="flex flex-col h-[600px] overflow-hidden">
      <CardHeader className="pb-3 border-b shrink-0">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-base">
            <MessageCircle className="h-5 w-5 text-teal-500" />
            دستیار هوشمند هرمزگان
          </CardTitle>
          <div className="flex items-center gap-2">
            <VoiceButton
              size="sm"
              onTranscript={(text) => sendMessage(text)}
            />
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={clearHistory}
              title="پاک کردن تاریخچه"
            >
              <Trash2 className="h-4 w-4 text-muted-foreground" />
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col p-0 overflow-hidden">
        {/* Messages */}
        <div
          ref={scrollRef}
          className="flex-1 overflow-y-auto p-4 space-y-4"
        >
          <MessageList messages={messages} />

          <AnimatePresence>
            {isTyping && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="flex items-center gap-2 text-sm text-muted-foreground"
              >
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>دستیار در حال تایپ...</span>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Suggestions */}
        <Suggestions
          suggestions={suggestions}
          onSelect={(text) => sendMessage(text)}
        />

        {/* Input */}
        <div className="border-t p-3">
          <ChatInput onSend={sendMessage} disabled={isTyping} />
        </div>
      </CardContent>
    </Card>
  );
}
