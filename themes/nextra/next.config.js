const _nextra = require('nextra');
const nextra = _nextra.default || _nextra;

const withNextra = nextra({
  theme: 'nextra-theme-docs',
  themeConfig: './theme.config.js',
  unstable_staticImage: true,
  flexsearch: {
    codeblocks: true
  },
  defaultShowCopyCode: true
})

let nextConfig = {};
try {
  const themeOptions = require('./theme.options.json');
  if (themeOptions.i18n && Array.isArray(themeOptions.i18n) && themeOptions.i18n.length > 0) {
    const validLocales = themeOptions.i18n
      .map(item => item.locale)
      .filter(l => l && l !== 'auto');
    if (validLocales.length > 0) {
      const defLoc = (!themeOptions.defaultLocale || themeOptions.defaultLocale === 'auto')
        ? (validLocales.includes('zh') ? 'zh' : validLocales[0])
        : themeOptions.defaultLocale;
      nextConfig.i18n = {
        locales: validLocales,
        defaultLocale: defLoc,
        localeDetection: false,
      };
    }
  }
} catch (e) {}

module.exports = withNextra(nextConfig)

