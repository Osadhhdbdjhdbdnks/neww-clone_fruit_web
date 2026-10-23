import type { Metadata } from "next";
import "./globals.css";
import { SiteHeader } from "@/components/site-header";

export const metadata: Metadata = {
  title: "Agrumea Farm | Jams, pestos and flavours of Sicily",
  description:
    "Agrumea Farm transforms Sicilian citrus fruits, other fruits and produce into artisanal jams, pestos and preserves with an authentic flavour",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col">
        <a href="#site-main" className="visually-hidden">
          Skip to content
        </a>
        <SiteHeader />
        <main id="site-main" className="site-main flex-1">
          {children}
        </main>
        <footer className="site-shell__legal">
          <div className="site-legal">
            <a href="/privacy" className="site-legal__link">
              Privacy &amp; Cookies
            </a>
          </div>
        </footer>
      </body>
    </html>
  );
}
