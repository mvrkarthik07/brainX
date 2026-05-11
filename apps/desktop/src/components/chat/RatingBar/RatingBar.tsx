import { motion } from "framer-motion";
import { Star } from "lucide-react";
import { useState } from "react";

import { useChat } from "@/hooks/useChat";
import { cn } from "@/utils/cn";
import styles from "@/components/chat/RatingBar/RatingBar.module.css";

const RATING_LABELS: Record<1 | 2 | 3 | 4 | 5, string> = {
  1: "wrong path",
  2: "mostly off",
  3: "mixed",
  4: "useful",
  5: "excellent",
};

export function RatingBar({
  queryId,
  currentRating,
}: {
  queryId: string;
  currentRating?: 1 | 2 | 3 | 4 | 5;
}) {
  const [hovered, setHovered] = useState<number | null>(null);
  const { rateMessage } = useChat();

  return (
    <motion.div
      className={styles.ratingBar}
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4, duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
    >
      <span className={styles.ratingLabel}>Rate this response</span>
      <div className={styles.stars}>
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            className={cn(
              styles.star,
              currentRating && styles.starLocked,
              (hovered ?? currentRating ?? 0) >= star && styles.starActive,
            )}
            onMouseEnter={() => {
              if (!currentRating) {
                setHovered(star);
              }
            }}
            onMouseLeave={() => {
              if (!currentRating) {
                setHovered(null);
              }
            }}
            onClick={() => {
              if (!currentRating) {
                void rateMessage(queryId, star as 1 | 2 | 3 | 4 | 5);
              }
            }}
            type="button"
            disabled={Boolean(currentRating)}
          >
            <Star size={14} />
          </button>
        ))}
      </div>
      {currentRating ? (
        <motion.span className={styles.ratingFeedback} initial={{ opacity: 0, x: -4 }} animate={{ opacity: 1, x: 0 }}>
          {RATING_LABELS[currentRating]}
        </motion.span>
      ) : null}
    </motion.div>
  );
}
