import Link from "next/link";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { products } from "@/data/products";

type Props = { params: Promise<{ slug: string }> };

export function generateStaticParams() {
  return products.map((p) => ({ slug: p.slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const product = products.find((p) => p.slug === slug);
  if (!product) return { title: "Product not found | Agrumea Farm" };
  return {
    title: `${product.name} | Agrumea Farm`,
    description: `${product.name} — artisanal Sicilian preserve from Agrumea Farm.`,
  };
}

export default async function ProductPage({ params }: Props) {
  const { slug } = await params;
  const product = products.find((p) => p.slug === slug);
  if (!product) notFound();

  return (
    <section className="story-section" style={{ textAlign: "center", paddingTop: "calc(var(--header-pad-y) * 4 + var(--header-brand-width))" }}>
      <p className="story-kicker">Pantry</p>
      <h1 className="story-title">{product.name}</h1>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={product.image}
        alt={product.name}
        style={{
          height: "min(420px, 60vh)",
          margin: "0 auto",
          display: "block",
          filter: "drop-shadow(0 24px 40px color-mix(in srgb, var(--color-border-brand) 25%, transparent))",
        }}
      />
      <p className="story-text" style={{ margin: "2rem auto 0" }}>
        An artisanal Sicilian preserve from Agrumea Farm, made with fruit and produce
        from our orchards and vegetable gardens, cooked slowly the traditional way.
      </p>
      <div style={{ marginTop: "var(--space-s)", display: "flex", gap: "1rem", justifyContent: "center", flexWrap: "wrap" }}>
        <a
          className="cta-pill"
          href="https://www.riblo.it/agrumea-farm/"
          target="_blank"
          rel="noreferrer"
        >
          Buy online
        </a>
        <Link className="cta-pill cta-pill--outline" href="/dispensa">
          Back to pantry
        </Link>
      </div>
    </section>
  );
}
