import { motion } from "framer-motion";
import { Scale } from "lucide-react";

export default function TypingIndicator() {
  return (
    <motion.div
      className="bubble-row bubble-row--bot"
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
    >
      <div className="avatar avatar--bot">
        <Scale size={16} />
      </div>
      <div className="bubble bubble--bot typing-bubble">
        <span className="dot" />
        <span className="dot" />
        <span className="dot" />
      </div>
    </motion.div>
  );
}
