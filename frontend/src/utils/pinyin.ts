import { pinyin } from 'pinyin-pro'

export function toPinyin(text: string): string {
  return pinyin(text, { toneType: 'none' })
}

export function pinyinSort<T>(items: T[], getName: (item: T) => string): T[] {
  return [...items].sort((a, b) => {
    return toPinyin(getName(a)).localeCompare(toPinyin(getName(b)))
  })
}

export function getInitial(name: string): string {
  const py = pinyin(name, { toneType: 'none', pattern: 'first' })
  return py.charAt(0).toUpperCase()
}

export function groupByInitial<T>(items: T[], getName: (item: T) => string): Map<string, T[]> {
  const groups = new Map<string, T[]>()
  for (const item of items) {
    const init = getInitial(getName(item))
    if (!groups.has(init)) groups.set(init, [])
    groups.get(init)!.push(item)
  }
  return groups
}

export const ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('')
