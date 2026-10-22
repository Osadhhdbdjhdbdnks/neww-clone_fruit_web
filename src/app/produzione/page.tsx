import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Production | Agrumea Farm",
  description:
    "How Agrumea Farm transforms Sicilian citrus fruits and produce into artisanal jams, pestos and preserves.",
};

export default function ProductionPage() {
  return (
    <>
      <section className="story-section" style={{ paddingTop: "calc(var(--header-pad-y) * 4 + var(--header-brand-width))" }}>
        <p className="story-kicker">Production</p>
        <h1 className="story-title">From the orchard to the jar.</h1>
        <p className="story-text">
          At Agrumea Farm, production follows the rhythm of the Sicilian seasons. Citrus
          fruits, almonds, pistachios and vegetables are harvested at peak ripeness in our
          orchards and kitchen gardens, then transformed on-site with time-honoured methods.
        </p>
        <p className="story-text">
          Pulp, peel and sugar slowly cook together in small batches to preserve original
          colours and aromas — traditional craft paired with a touch of innovation.
        </p>
      </section>

      <section className="story-section story-section--tint">
        <div className="story-inner">
          <h2 className="story-title">The farm, by the numbers</h2>
          <div className="story-stats">
            <div>
              <p className="story-stat__value">100%</p>
              <p className="story-stat__label">Sicilian ingredients</p>
            </div>
            <div>
              <p className="story-stat__value">0 km</p>
              <p className="story-stat__label">From field to laboratory</p>
            </div>
            <div>
              <p className="story-stat__value">10+</p>
              <p className="story-stat__label">Artisanal recipes</p>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
