import {access, readFile} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const read = path => readFile(resolve(root, path), 'utf8');
const localPath = path => new URL(path, 'https://ep133.local').pathname.replace(/^\//, '');
const accessPublishedAsset = async asset => {
  const path = resolve(root, localPath(asset));
  try {
    await access(path);
  } catch (error) {
    // Cloudflare Pages resolves extensionless requests to sibling HTML files.
    if (error.code !== 'ENOENT') throw error;
    await access(`${path}.html`);
  }
};
const assert = (condition, message) => {
  if (!condition) throw new Error(message);
};

const [html, serviceWorker, headers, manifestText] = await Promise.all([
  read('index.html'),
  read('sw.js'),
  read('_headers'),
  read('manifest.webmanifest')
]);
const manifest = JSON.parse(manifestText);

assert(html.includes('rel="manifest"'), 'index.html must link the web app manifest');
assert(html.includes("serviceWorker.register('/sw.js')"), 'index.html must register the service worker');
assert(!html.includes('fonts.googleapis.com'), 'fonts must be hosted locally for offline use');
assert(html.includes("localStorage.setItem(analyticsOptOutKey, '1')"), '?no-analytics must persist its opt-out');
assert(html.includes("localStorage.removeItem(analyticsOptOutKey)"), '?analytics must clear the saved opt-out');
assert(headers.includes('/sw.js\n  Cache-Control: no-cache'), 'sw.js must revalidate on every visit');

const shellBlock = serviceWorker.match(/const APP_SHELL = \[([\s\S]*?)\];/);
assert(shellBlock, 'sw.js must define APP_SHELL');
const shellPaths = [...shellBlock[1].matchAll(/'([^']+)'/g)].map(match => match[1]);
for (const asset of shellPaths) {
  await accessPublishedAsset(asset);
}

for (const icon of manifest.icons || []) {
  await accessPublishedAsset(icon.src);
}
