import { useMemo } from 'react'
import { FOOD_EMOJIS } from '../constants'

export default function FloatingIcons({ count = 16 }) {
  const icons = useMemo(() =>
    Array.from({ length: count }, (_, i) => ({
      emoji:    FOOD_EMOJIS[i % FOOD_EMOJIS.length],
      left:     Math.random() * 90,
      size:     0.9 + Math.random() * 1.1,
      duration: 14 + Math.random() * 20,
      delay:    Math.random() * 22,
    })), [count])

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none z-0" aria-hidden>
      {icons.map((ic, i) => (
        <div
          key={i}
          className="absolute anim-float-up select-none"
          style={{
            left: `${ic.left}%`,
            fontSize: `${ic.size}rem`,
            animationDuration: `${ic.duration}s`,
            animationDelay: `${ic.delay}s`,
            opacity: 0.06,
          }}
        >
          {ic.emoji}
        </div>
      ))}
    </div>
  )
}
