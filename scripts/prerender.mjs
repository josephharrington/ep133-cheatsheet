import { readFile, writeFile } from 'node:fs/promises';
import process from 'node:process';
import { JSDOM, VirtualConsole } from 'jsdom';

const indexUrl = new URL('../index.html', import.meta.url);
const source = await readFile(indexUrl, 'utf8');
const startMarker = '<!-- prerender:start -->';
const endMarker = '<!-- prerender:end -->';
const prerenderedPattern = new RegExp(
  `(?<=${startMarker})[\\s\\S]*?(?=${endMarker})`,
);

if (!prerenderedPattern.test(source)) {
  throw new Error('Could not find the pre-render markers in index.html');
}

const runtimeErrors = [];
const virtualConsole = new VirtualConsole();
virtualConsole.on('jsdomError', error => runtimeErrors.push(error));

// Run the real page renderer so the crawlable fallback cannot drift from the UI.
const dom = new JSDOM(source, {
  runScripts: 'dangerously',
  url: 'https://ep133.joeyh.org/',
  virtualConsole,
  beforeParse(window) {
    // Render every section expanded; the browser reapplies responsive state at load.
    window.matchMedia = query => ({
      matches: false,
      media: query,
      onchange: null,
      addEventListener() {},
      removeEventListener() {},
      addListener() {},
      removeListener() {},
      dispatchEvent() { return false; },
    });
    window.requestAnimationFrame = callback => {
      callback(0);
      return 0;
    };
    window.cancelAnimationFrame = () => {};
    window.scrollTo = () => {};
    window.ResizeObserver = class {
      observe() {}
      unobserve() {}
      disconnect() {}
    };
    window.addEventListener('error', event => runtimeErrors.push(event.error));
  },
});

const renderedMain = dom.window.document.getElementById('main');
const sectionCount = renderedMain.querySelectorAll('.section-group').length;
const expectedSectionCount = dom.window.document.querySelectorAll(
  '#filters .filter:not([data-id="all"]):not([data-id="overview"])',
).length;
const renderedMarkup = renderedMain.innerHTML.trim().replace(/[ \t]+$/gm, '');
const rendered = `\n${renderedMarkup}\n`;

dom.window.close();

if (runtimeErrors.length) {
  throw new AggregateError(runtimeErrors, 'The page failed while pre-rendering');
}
if (!sectionCount || sectionCount !== expectedSectionCount) {
  throw new Error(
    `Expected ${expectedSectionCount} rendered sections, found ${sectionCount}`,
  );
}

const output = source.replace(prerenderedPattern, rendered);

if (process.argv.includes('--check')) {
  if (output !== source) {
    console.error('index.html pre-rendered content is out of date. Run npm run prerender.');
    process.exitCode = 1;
  }
} else if (output !== source) {
  await writeFile(indexUrl, output);
  console.log(`Pre-rendered ${sectionCount} sections into index.html.`);
} else {
  console.log(`Pre-rendered content is current (${sectionCount} sections).`);
}
