const fs = require('fs');
const { JSDOM } = require('jsdom');
const jsdom = new JSDOM(`<!DOCTYPE html><html><body><div id="galaxy-3d"></div></body></html>`);
global.window = jsdom.window;
global.document = jsdom.window.document;

// Mock enough for 3d-force-graph to not crash
global.window.innerWidth = 1200;
global.window.innerHeight = 800;
global.Element = jsdom.window.Element;
global.navigator = { userAgent: 'node' };

try {
  const code = fs.readFileSync('/Volumes/Notebook/omni-hub/illacme-plenipes/web/dashboard/vendor/3d-force-graph.min.js', 'utf8');
  eval(code);
} catch (e) {
  console.log("Error loading 3d-force-graph:", e.message);
}
