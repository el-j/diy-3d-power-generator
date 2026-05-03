export type BomData = {
  totals: Record<string, string | number>;
  assemblies: Record<string, unknown>;
};

export type NavItem = {
  href: string;
  label: string;
};

export type FeatureCard = {
  title: string;
  body: string;
};

export type BuildStep = {
  id: string;
  title: string;
  detail: string;
};

export type DownloadCategory = 'generator' | 'tower' | 'base' | 'tools';

export type DownloadItem = {
  label: string;
  path: string;
  category: DownloadCategory;
};

export type AssemblyStatRow = {
  name: string;
  count: number;
};
