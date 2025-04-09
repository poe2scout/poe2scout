import { SitemapStream, streamToPromise } from "sitemap";
import { Readable } from "stream";
import fs from "fs";
import path from "path";

const hostname = "https://poe2scout.com";

// Define your routes and their properties
const urls = [
  { url: "/", changefreq: "daily", priority: 1.0 },
  { url: "/economy/currency", changefreq: "daily", priority: 0.8 },
  { url: "/economy/accessory", changefreq: "daily", priority: 0.8 },
  { url: "/economy/armour", changefreq: "daily", priority: 0.8 },
  { url: "/economy/weapon", changefreq: "daily", priority: 0.8 },
  { url: "/economy/jewel", changefreq: "daily", priority: 0.8 },
  { url: "/economy/gems", changefreq: "daily", priority: 0.8 },
  { url: "/builds", changefreq: "daily", priority: 0.8 },
];

async function generateSitemap() {
  try {
    // Create a stream
    const stream = new SitemapStream({ hostname });

    // Generate sitemap from URLs
    const data = await streamToPromise(Readable.from(urls).pipe(stream));

    // Ensure the public directory exists
    const publicDir = path.join("src", "..", "public");
    if (!fs.existsSync(publicDir)) {
      fs.mkdirSync(publicDir, { recursive: true });
    }

    // Write sitemap to file
    fs.writeFileSync(path.join(publicDir, "sitemap.xml"), data);

    console.log("Sitemap generated successfully!");
  } catch (error) {
    console.error("Error generating sitemap:", error);
  }
}

generateSitemap();
