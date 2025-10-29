export interface Quote {
  id: number;
  text: string;
  author: string;
  source: string;
  theme: string;
  favorite: boolean;
  notes: string | null;
  createdAt: string;
  addedBy: string;
}

export interface QuotesMetadata {
  lastId: number;
  version: string;
  lastModified: string;
}

export interface QuotesData {
  metadata: QuotesMetadata;
  quotes: Quote[];
}

export interface SearchParams {
  query?: string;
  author?: string;
  theme?: string;
}
