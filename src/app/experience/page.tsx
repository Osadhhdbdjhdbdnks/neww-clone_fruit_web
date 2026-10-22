import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Experience | Agrumea Farm",
  description:
    "Live the Agrumea Farm experience: tastings, tours and flavours of Sicily at the farm.",
};

export default function ExperiencePage() {
  return (
    <>
      <section className="experience-banner" style={{ marginTop: "var(--app-height)" }}>
        <div>
          <p className="story-kicker">Experience</p>
          <h1 className="story-title">Taste Sicily where it grows.</h1>
          <p className="story-text" style={{ margin: "0 auto var(--space-s)" }}>
            Wander the orchards, watch the slow cooking of the jars and sit down to a
            tasting of our marmalades, creams and pestos straight from the farm.
          </p>
          <Link className="cta-pill" href="/contatti">
            Get in touch
          </Link>
        </div>
      </section>
    </>
  );
}
