import { readdir, stat } from "node:fs/promises";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const distAssets = fileURLToPath(new URL("../dist/assets/", import.meta.url));
const limits = {
  mainBytes: 230_000,
  editorBytes: 560_000,
  cssBytes: 24_000,
  totalBytes: 900_000
};

async function assetStats() {
  const entries = await readdir(distAssets);
  const assets = [];
  for (const entry of entries) {
    const path = join(distAssets, entry);
    assets.push({ name: entry, size: (await stat(path)).size });
  }
  return assets;
}

function assertWithin(name, actual, limit) {
  if (actual > limit) {
    throw new Error(`${name} is ${actual} bytes, above ${limit} byte limit.`);
  }
}

const assets = await assetStats();
const editorChunk = assets.find((asset) => asset.name.startsWith("GeneratedCodeEditor-") && asset.name.endsWith(".js"));
const mainChunk = assets.find((asset) => asset.name.startsWith("index-") && asset.name.endsWith(".js"));
const cssBundle = assets.find((asset) => asset.name.startsWith("index-") && asset.name.endsWith(".css"));
const totalBytes = assets.reduce((total, asset) => total + asset.size, 0);

if (!editorChunk) {
  throw new Error("Expected GeneratedCodeEditor to remain lazy-loaded in a separate chunk.");
}
if (!mainChunk) {
  throw new Error("Expected an index JavaScript bundle in dist/assets.");
}
if (!cssBundle) {
  throw new Error("Expected an index CSS bundle in dist/assets.");
}

assertWithin("Main JavaScript bundle", mainChunk.size, limits.mainBytes);
assertWithin("GeneratedCodeEditor lazy chunk", editorChunk.size, limits.editorBytes);
assertWithin("CSS bundle", cssBundle.size, limits.cssBytes);
assertWithin("Total asset payload", totalBytes, limits.totalBytes);

console.log(
  JSON.stringify(
    {
      main: mainChunk.size,
      editor: editorChunk.size,
      css: cssBundle.size,
      total: totalBytes
    },
    null,
    2
  )
);
