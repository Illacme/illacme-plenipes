const _nextra = require('nextra');
const nextra = _nextra.default || _nextra;

const withNextra = nextra({
  theme: 'nextra-theme-docs',
  themeConfig: './theme.config.js',
  unstable_staticImage: true,
})

let nextConfig = {};
try {
  const themeOptions = require('./theme.options.json');
  if (themeOptions.i18n && Array.isArray(themeOptions.i18n) && themeOptions.i18n.length > 0) {
    nextConfig.i18n = {
      locales: themeOptions.i18n.map(item => item.locale),
      defaultLocale: themeOptions.defaultLocale || 'zh',
    };
  }
} catch (e) {}

module.exports = withNextra(nextConfig)

