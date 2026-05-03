import { BLOB_BASE_URL, RAW_BASE_URL } from '../data/content';

export function formatKey(value: string): string {
  return value
    .replaceAll('_', ' ')
    .replace(/(^|\s)\S/g, (s) => s.toUpperCase());
}

export function countEntries(value: unknown): number {
  if (Array.isArray(value)) return value.length;
  if (value && typeof value === 'object') {
    return Object.values(value).reduce((sum, child) => sum + countEntries(child), 0);
  }
  return 0;
}

export function toRawUrl(path: string): string {
  return `${RAW_BASE_URL}/${path}`;
}

export function toBlobUrl(path: string): string {
  return `${BLOB_BASE_URL}/${path}`;
}
