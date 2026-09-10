# Number Builder 🚂

**Class 5** • **Mathematics** • **Chapter 1: Large Numbers** • **Topic 1: Reading & Writing Large Numbers**

## 🎯 Educational Objectives
- Learn the Indian Place Value System (Ones, Tens, Hundreds, Thousands, Ten Thousands, Lakhs, Ten Lakhs).
- Convert numbers written in words into standard numeral notation with Indian commas.
- Master zero placeholders in intermediate periods.

## 📁 Game Structure
```text
number_builder/
├── index.html       # Standalone game arena markup
├── style.css        # Scoped styles for the place value train
├── game.js          # Interactive game mechanics & validation
├── assets/          # Sprites, icons, and audio
└── README.md        # Documentation
```

## 🔌 API Integration
Communicates seamlessly with Django backend via `window.TezMindzGameBridge`:
- `TezMindzGameBridge.submitAnswer({ level, answer, scoreDelta })`
- `TezMindzGameBridge.getHint()`
- `TezMindzGameBridge.completeGame({ score, totalLevels })`
- `TezMindzGameBridge.finishAndRedirect()`

## 🛠️ Adding New Challenges
Modify `state.challenges` inside `game.js`:
```javascript
{
  level: 6,
  title: "Level 6: Crores Intro",
  instruction: "Construct 8-digit value:",
  words: "One Crore",
  targetNumber: 10000000,
  hint: "1 followed by 7 zeros.",
  xp: 60,
  coins: 20,
}
```
