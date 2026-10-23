"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

const primaryLinks = [
  { href: "/", label: "Home" },
  { href: "/dispensa", label: "Pantry" },
  { href: "/produzione", label: "Production" },
];

const secondaryLinks = [
  { href: "/experience", label: "Experience" },
  { href: "/chi-siamo", label: "About" },
  { href: "/contatti", label: "Contacts" },
  { href: "https://www.riblo.it/agrumea-farm/", label: "Shop", external: true },
];

export function SiteHeader() {
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    document.body.style.overflow = menuOpen ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [menuOpen]);

  return (
    <>
      <header className="site-header">
        <div className="site-header__bar">
          <div className="site-header__side site-header__side--start">
            <nav className="site-lang-switcher" aria-label="Language switcher">
              <Link href="/" className="site-lang-switcher__item">
                IT
              </Link>
              <span
                aria-current="true"
                className="site-lang-switcher__item is-active"
              >
                EN
              </span>
            </nav>
          </div>

          <div className="site-header__center">
            <div className="site-header__brand">
              <Link href="/" aria-label="Agrumea Farm">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src="/assets/agrumea/logotipo.svg" alt="Agrumea Farm" />
              </Link>
            </div>
          </div>

          <div className="site-header__side site-header__side--end">
            <button
              type="button"
              className="site-menu-toggle"
              aria-controls="site-full-page-nav"
              aria-expanded={menuOpen}
              aria-label={menuOpen ? "close" : "menu"}
              onClick={() => setMenuOpen((v) => !v)}
            >
              <span className="site-menu-toggle__pill">
                <span className="site-menu-toggle__diamond" aria-hidden />
                {menuOpen ? "close" : "menu"}
              </span>
            </button>
          </div>
        </div>
      </header>

      <div
        id="site-full-page-nav"
        className={`site-full-page-nav${menuOpen ? " is-open" : ""}`}
        aria-hidden={!menuOpen}
      >
        <div className="site-full-page-nav__inner">
          <nav aria-label="Primary">
            <ul className="fp-nav__list">
              {primaryLinks.map((l) => (
                <li key={l.href} className="fp-nav__item">
                  <Link
                    href={l.href}
                    className="fp-nav__link"
                    onClick={() => setMenuOpen(false)}
                  >
                    <span className="fp-nav__marker" aria-hidden />
                    {l.label}
                  </Link>
                </li>
              ))}
              <li className="fp-nav__item fp-nav__item--is-last">
                <Link
                  href="/experience"
                  className="fp-nav__link"
                  onClick={() => setMenuOpen(false)}
                >
                  <span className="fp-nav__marker" aria-hidden />
                  Experience
                </Link>
                <ul className="fp-nav__secondary">
                  {secondaryLinks.slice(1).map((l) =>
                    l.external ? (
                      <li key={l.label} className="fp-nav__secondary-item">
                        <a
                          href={l.href}
                          className="fp-nav__secondary-link"
                          target="_blank"
                          rel="noreferrer"
                        >
                          {l.label}
                          <span className="fp-nav__arrow" aria-hidden>
                            ↗
                          </span>
                        </a>
                      </li>
                    ) : (
                      <li key={l.label} className="fp-nav__secondary-item">
                        <Link
                          href={l.href}
                          className="fp-nav__secondary-link"
                          onClick={() => setMenuOpen(false)}
                        >
                          {l.label}
                        </Link>
                      </li>
                    ),
                  )}
                </ul>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </>
  );
}
