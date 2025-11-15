import { v4 as uuidv4 } from 'uuid';

export function hashString(str: string): string {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  return Math.abs(hash).toString(16);
}

export function getOrCreateIdemKey(scope: 'order' | 'payment' | 'cancel', payload: string): string {
  const hash = hashString(payload);
  const key = `idem:${scope}:${hash}`;

  const existing = localStorage.getItem(key);
  if (existing) {
    return existing;
  }

  const value = `${scope}_${Date.now()}_${uuidv4().slice(0, 8)}`;
  localStorage.setItem(key, value);

  return value;
}
