import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "About | Agrumea Farm",
  description:
    "Agrumea Farm — Azienda Agricola Sebastiano Piazza: a Sicilian farm transforming citrus fruits and produce into artisanal preserves.",
};

export default function AboutPage() {
  return (
    <section className="story-section" style={{ paddingTop: "calc(var(--header-pad-y) * 4 + var(--header-brand-width))" }}>
      <p className="story-kicker">About</p>
      <h1 className="story-title">A farm that keeps Sicilian flavours alive.</h1>
      <p className="story-text">
        Agrumea Farm is the agricultural estate of Sebastiano Piazza, a family that has
        chosen to keep working the land the honest way: growing citrus fruits, almonds,
        pistachios and vegetables, then transforming them by hand into jams, pestos and
        preserves with an authentic flavour.
      </p>
      <p className="story-text">
        Every jar carries the story of our orchards — a small piece of Sicily, cooked
        slowly and shared generously.
      </p>
      <p className="story-text" style={{ marginTop: "2rem", fontSize: "var(--text-small)" }}>
        ©2026 | Agrumea Farm — Azienda Agricola Sebastiano Piazza
      </p>
    </section>
  );
}
