import { motion } from "framer-motion";
import { User, Bot, AlertCircle } from "lucide-react";

export function MessageList({ messages }) {
  if (messages.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-muted-foreground text-sm">
        <Bot className="h-12 w-12 mb-3 opacity-30" />
        <p>سلام! من دستیار هوشمند هرمزگان هستم.</p>
        <p className="text-xs mt-1">سؤالی درباره ترافیک، گردشگری یا مکان‌ها دارید؟</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {messages.map((msg, idx) => (
        <motion.div
          key={msg.id || idx}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: idx === messages.length - 1 ? 0 : 0 }}
          className={`flex gap-3 ${
            msg.role === "user" ? "flex-row-reverse" : ""
          }`}
        >
          {/* Avatar */}
          <div
            className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
              msg.role === "user"
                ? "bg-teal-100 text-teal-700"
                : msg.isError
                ? "bg-red-100 text-red-700"
                : "bg-slate-100 text-slate-700"
            }`}
          >
            {msg.role === "user" ? (
              <User className="h-4 w-4" />
            ) : msg.isError ? (
              <AlertCircle className="h-4 w-4" />
            ) : (
              <Bot className="h-4 w-4" />
            )}
          </div>

          {/* Content */}
          <div
            className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
              msg.role === "user"
                ? "bg-teal-600 text-white rounded-tr-sm"
                : msg.isError
                ? "bg-red-50 text-red-800 border border-red-200 rounded-tl-sm"
                : "bg-slate-100 text-slate-800 rounded-tl-sm"
            }`}
          >
            {msg.content}
            {msg.metadata && (
              <div className="mt-2 pt-2 border-t border-white/20 text-xs opacity-70">
                {JSON.stringify(msg.metadata)}
              </div>
            )}
          </div>
        </motion.div>
      ))}
    </div>
  );
}
