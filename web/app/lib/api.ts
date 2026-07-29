// Read-only client for the FastAPI service (ADR-0004). Runs on the server only —
// these functions are called from Server Components so pages are server-rendered
// HTML, which is what our search-driven acquisition depends on.

const API_BASE_URL = process.env.API_BASE_URL ?? "http://localhost:8000";

export interface Recommendation {
  recommender: { name: string; slug: string };
  // The date it was said — the only date a reader is shown. There is no
  // ingestion field on this type by design.
  said_on: string;
  source: { title: string; url: string; position_label: string };
}

export interface Work {
  id: string;
  slug: string;
  title: string;
  author: string;
  recommendations: Recommendation[];
}

export async function getWork(slug: string): Promise<Work | null> {
  const res = await fetch(`${API_BASE_URL}/works/${encodeURIComponent(slug)}`, {
    // Skeleton: always fetch fresh. On-demand revalidation (ISR) arrives with
    // SCRUM-3 / SCRUM-10.
    cache: "no-store",
  });
  if (res.status === 404) {
    return null;
  }
  if (!res.ok) {
    throw new Error(`API returned ${res.status} for work "${slug}"`);
  }
  return (await res.json()) as Work;
}
