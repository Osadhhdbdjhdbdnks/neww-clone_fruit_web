/* Products inspired by the slider at www.agrumeafarm.it/en.
   Visual assets are the REAL fruits themselves (no jars): rendered by
   scripts/generate-fruits.py into public/assets/agrumea (fruit-<slug>.webp). */
export type ProductCategory = "jams" | "creams" | "savoury";

export type Product = {
  slug: string;
  /** URL slug used on the live site (underscores). */
  siteSlug: string;
  name: string;
  image: string;
  /** Horizontally reversed view of the same fruit — cross-faded in while the
   * slider spins the item in 3D so the "back side" reads correctly. */
  sideImage: string;
  category: ProductCategory;
};

/**
 * Tropical fruit line-up (papaya, melon, sugarcane, rambutan, dragon fruit).
 * Each slider item shows the actual fruit — papaya halves with seeds, netted
 * cantaloupe with a wedge, jointed sugarcane stalks, spine-covered rambutan
 * cluster and magenta dragon fruit with recurved green scales.
 * The set is repeated twice so the slider keeps a dense marquee feel and the
 * loop wraps seamlessly (same fruit images reused, no invented variants).
 */
const tropical: Omit<Product, "image" | "sideImage">[] = [
  { slug: "papaya", siteSlug: "papaya", name: "Papaya", category: "jams" },
  { slug: "melone", siteSlug: "melone", name: "Melon", category: "jams" },
  { slug: "canna-zucchero", siteSlug: "canna_zucchero", name: "Sugarcane", category: "creams" },
  { slug: "rambutan", siteSlug: "rambutan", name: "Rambutan", category: "jams" },
  { slug: "frutta-drago", siteSlug: "frutta_drago", name: "Dragon Fruit", category: "jams" },
];

const fruitImg = (slug: string) => `/assets/agrumea/fruit-${slug}.webp`;
/** Reversed "back side" view used during the hover spin. */
const fruitSideImg = (slug: string) => `/assets/agrumea/fruit-${slug}-side.webp`;

/** Unique products (used by the pantry grid and product pages). */
export const products: Product[] = tropical.map((p) => ({
  ...p,
  image: fruitImg(p.slug),
  sideImage: fruitSideImg(p.slug),
}));

/** Slider list: the five fruits repeated twice for a seamless, dense marquee. */
export const sliderProducts: Product[] = [0, 1].flatMap((round) =>
  products.map((p) => ({
    ...p,
    slug: round === 0 ? p.slug : `${p.slug}-${round + 1}`,
  })),
);

export const categories: { key: ProductCategory; title: string; blurb: string }[] = [
  {
    key: "jams",
    title: "Marmelade & Jams",
    blurb:
      "Sicilian artisanal marmalades and jams prepared the traditional way: pulp, peel and sugar slowly cook together to preserve their original colours and aromas, with a touch of innovation.",
  },
  {
    key: "creams",
    title: "Spreadable creams",
    blurb:
      "The art of transformation reaches its most indulgent expression: slow processes that enhance the finest qualities of pistachio and almond, blended into creamy bases.",
  },
  {
    key: "savoury",
    title: "Savoury",
    blurb:
      "Sughi, pâtés and sauces made with Sicilian ingredients — pestos and preserves that bring the farm's orchards and vegetable gardens straight to the table.",
  },
];
