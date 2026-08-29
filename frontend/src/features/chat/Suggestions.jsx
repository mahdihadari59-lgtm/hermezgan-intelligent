import { motion, AnimatePresence } from "framer-motion";

const defaultSuggestions = [
  "وضعیت ترافیک بندرعباس چطوره؟",
  "بهترین رستوران‌های قشم کجاست؟",
  "نزدیک‌ترین بیمارستان کجاست؟",
  "جاهای دیدنی کیش رو بگو",
];

export function Suggestions({ suggestions, onSelect }) {
  const items = suggestions?.length > 0 ? suggestions : defaultSuggestions;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, height: 0 }}
        animate={{ opacity: 1, height: "auto" }}
        exit={{ opacity: 0, height: 0 }}
        className="border-t px-3 py-2"
      >
        <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-hide">
          {items.map((suggestion, idx) => (
            <button
              key={idx}
              onClick={() => onSelect(suggestion)}
              className="shrink-0 rounded-full bg-slate-50 px-3 py-1.5 text-xs text-slate-600 hover:bg-teal-50 hover:text-teal-700 transition-colors border whitespace-nowrap"
            >
              {suggestion}
            </button>
          ))}
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
