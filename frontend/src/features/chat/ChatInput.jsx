import { useState, useRef } from "react";
import { Button } from "@components/common/Button";
import { Input } from "@components/common/Input";
import { Send, Loader2 } from "lucide-react";

export function ChatInput({ onSend, disabled }) {
  const [text, setText] = useState("");
  const inputRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim() || disabled) return;
    onSend(text.trim());
    setText("");
    inputRef.current?.focus();
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <Input
        ref={inputRef}
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="پیام خود را بنویسید..."
        disabled={disabled}
        className="flex-1"
        dir="rtl"
      />
      <Button
        type="submit"
        disabled={disabled || !text.trim()}
        size="icon"
        className="shrink-0"
      >
        {disabled ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <Send className="h-4 w-4" />
        )}
      </Button>
    </form>
  );
}
