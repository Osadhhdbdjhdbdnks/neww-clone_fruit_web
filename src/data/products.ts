/* Products extracted from the live jar slider at www.agrumeafarm.it/en.
   Images were saved locally into public/assets/agrumea during cloning. */
export type ProductCategory = "jams" | "creams" | "savoury";

export type Product = {
  slug: string;
  /** URL slug used on the live site (underscores). */
  siteSlug: string;
  name: string;
  image: string;
  /** Label overlay artwork shown when the jar spins on hover. */
  label: string;
  category: ProductCategory;
};

/**
 * Tropical fruit line-up (papaya, melon, sugarcane, rambutan, dragon fruit).
 * Jar artwork is procedurally tinted from the original transparent silhouettes;
 * each product repeats the set twice so the slider keeps a dense marquee feel.
 */
const tropical: Omit<Product, "image" | "label">[] = [
  { slug: "papaya", siteSlug: "papaya", name: "Papaya Jam", category: "jams" },
  { slug: "melone", siteSlug: "melone", name: "Melon Jam", category: "jams" },
  { slug: "canna-zucchero", siteSlug: "canna_zucchero", name: "Sugarcane Syrup", category: "creams" },
  { slug: "rambutan", siteSlug: "rambutan", name: "Rambutan Jam", category: "jams" },
  { slug: "frutta-drago", siteSlug: "frutta_drago", name: "Dragon Fruit Jam", category: "jams" },
];

const baseSlug = (slug: string) => slug.replace(/-\d+$/, "");
const jarImg = (slug: string) => `/assets/agrumea/jar-${baseSlug(slug)}.webp`;
const labelImg = (slug: string) => `/assets/agrumea/label-${baseSlug(slug)}.webp`;

export const products: Product[] = [0, 1].flatMap((round) =>
  tropical.map((p) => ({
    ...p,
    slug: round === 0 ? p.slug : `${p.slug}-${round + 1}`,
    name: round === 0 ? p.name : `${p.name} — Reserve`,
    image: jarImg(p.slug),
    label: labelImg(p.slug),
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
