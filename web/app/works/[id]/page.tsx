import { notFound } from "next/navigation";
import { getWork } from "@/app/lib/api";

// Async Server Component — no "use client". The page is server-rendered HTML so
// crawlers get the full content (ADR-0004).

function formatSaidOn(isoDate: string): string {
  // Render the date it was said in the reader's locale-neutral long form.
  const [year, month, day] = isoDate.split("-").map(Number);
  const date = new Date(Date.UTC(year, month - 1, day));
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
    timeZone: "UTC",
  });
}

export default async function WorkPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const work = await getWork(id);
  if (!work) {
    notFound();
  }

  return (
    <main>
      <p>
        <a href="/">← goodreadsby</a>
      </p>
      <h1>{work.title}</h1>
      <p>by {work.author}</p>

      {work.formats.length > 0 && (
        <p>Available in: {work.formats.join(", ")}</p>
      )}

      <h2>
        Recommended by {work.recommendations.length}{" "}
        {work.recommendations.length === 1 ? "person" : "people"}
      </h2>

      <ul style={{ listStyle: "none", padding: 0 }}>
        {work.recommendations.map((rec, i) => (
          <li key={i} style={{ marginBottom: "1.5rem" }}>
            <strong>{rec.recommender.name}</strong>
            <div>on {formatSaidOn(rec.said_on)}</div>
            <div>
              <a href={rec.source.url}>
                {rec.source.title} — {rec.source.position_label}
              </a>
            </div>
          </li>
        ))}
      </ul>
    </main>
  );
}
