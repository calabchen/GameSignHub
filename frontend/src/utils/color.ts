export function gameColor(gameId: string): string {
  let hash = 0
  for (const c of gameId) hash = c.charCodeAt(0) + ((hash << 5) - hash)
  const hue = Math.abs(hash % 360)
  return `hsl(${hue}, 65%, 55%)`
}

export function gameGradient(gameId: string): string {
  const c = gameColor(gameId)
  return `linear-gradient(90deg, ${c.replace('hsl', 'hsla').replace(')', ', 0.1)')}, ${c})`
}
