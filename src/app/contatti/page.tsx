import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Contacts | Agrumea Farm",
  description:
    "Contact Agrumea Farm — drop us a line, we'd be delighted to tell you all about our farm and products.",
};

export default function ContactsPage() {
  return (
    <section className="story-section" style={{ paddingTop: "calc(var(--header-pad-y) * 4 + var(--header-brand-width))" }}>
      <p className="story-kicker">Contacts</p>
      <h1 className="story-title">Drop us a line.</h1>
      <p className="story-text">
        Do you have a question or would you like to find out more about us? We&rsquo;d be
        delighted to tell you all about Agrumea Farm.
      </p>
      <div className="contact-list">
        <p className="contact-item">
          Email:{" "}
          <a href="mailto:info@agrumeafarm.it">info@agrumeafarm.it</a>
        </p>
        <p className="contact-item">
          Shop:{" "}
          <a href="https://www.riblo.it/agrumea-farm/" target="_blank" rel="noreferrer">
            riblo.it/agrumea-farm
          </a>
        </p>
        <p className="contact-item">Agrumea Farm — Azienda Agricola Sebastiano Piazza, Sicily</p>
      </div>
    </section>
  );
}
