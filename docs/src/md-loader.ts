// Eager glob of all docs markdown. Keys are relative to this file (docs/src/).
// e.g. '../bom/master_bom.md', '../build-guide/01_tower.md'
export const markdownFiles = import.meta.glob('../**/*.md', {
  query: '?raw',
  import: 'default',
  eager: true,
}) as Record<string, string>;

export function getMarkdown(path: string): string {
  // Accept paths like 'docs/build-guide/01_tower.md' or 'build-guide/01_tower.md'
  const stripped = path.startsWith('docs/') ? path.slice(5) : path;
  const key = `../${stripped}`;
  return markdownFiles[key] ?? `# Not Found\n\nCould not load \`${path}\`.`;
}
