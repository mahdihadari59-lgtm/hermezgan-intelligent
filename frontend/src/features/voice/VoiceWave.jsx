import { motion } from "framer-motion";

export function VoiceWave({ isActive, color = "teal" }) {
  const colorClasses = {
    teal: "bg-teal-500",
    red: "bg-red-500",
    blue: "bg-blue-500",
  };

  if (!isActive) return null;

  return (
    <div className="flex items-center justify-center gap-1 h-8">
      {[...Array(7)].map((_, i) => (
        <motion.div
          key={i}
          animate={{
            height: [6, 20 + Math.sin(i) * 10, 6],
            opacity: [0.5, 1, 0.5],
          }}
          transition={{
            duration: 0.6,
            repeat: Infinity,
            delay: i * 0.08,
            ease: "easeInOut",
          }}
          className={`w-1 rounded-full ${colorClasses[color] || colorClasses.teal}`}
        />
      ))}
    </div>
  );
}
