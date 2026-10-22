import Link from "next/link";
import { categories, products } from "@/data/products";

export const metadata = {
  title: "Sicilian jams, pestos and preserves | Agrumea Farm",
  description:
    "Explore the Agrumea Farm pantry: Sicilian artisanal marmalades, jams, spreadable creams, pestos and savoury preserves.",
};

export default function PantryPage() {
  return (
    <>
      <section className="pantry-hero">
        <h1 className="pantry-hero__title">Pantry</h1>
        <p className="pantry-hero__lead">Our land, one jar at a time.</p>
      </section>

      {categories.map((c) => (
        <section key={c.key} className="story-section">
          <p className="story-kicker">{c.title}</p>
          <h2 className="story-title">{c.title}</h2>
          <p className="story-text">{c.blurb}</p>

          <div className="pantry-grid" style={{ paddingInline: 0, marginTop: "var(--space-s)" }}>
            {products
              .filter((p) => p.category === c.key)
              .map((p) => (
                <Link key={p.slug} href={`/dispensa/${p.slug}`} className="product-card">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img className="product-card__image" src={p.image} alt={p.name} loading="lazy" />
                  <span className="product-card__name">{p.name}</span>
                  <span className="product-card__cta">Discover</span>
                </Link>
              ))}
          </div>
        </section>
      ))}
    </>
  );
}
