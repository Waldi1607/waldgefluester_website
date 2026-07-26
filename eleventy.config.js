const fs = require("fs");
const translations = require("./src/_data/translations.json");

module.exports = function (eleventyConfig) {
  // Snippet-Dateien roh einlesen (keine Template-Verarbeitung — Inhalte
  // enthalten CSS/JS mit {#- und {%-Sequenzen, die Nunjucks stören würden)
  eleventyConfig.addShortcode("rawfile", function (path) {
    return fs.existsSync(path) ? fs.readFileSync(path, "utf8") : "";
  });

  // Übersetzungs-Filter: deutscher Text bleibt im Template stehen und wird
  // bei locale == 'en' über src/_data/translations.json ersetzt. Fehlt eine
  // Übersetzung, bleibt der deutsche Text sichtbar (fail-open).
  eleventyConfig.addNunjucksFilter("t", function (str) {
    const locale = this.ctx && this.ctx.locale;
    if (locale === "en") return translations[str] || str;
    return str;
  });

  return {
    dir: {
      input: "src/pages",
      includes: "../_includes",
      data: "../_data",
      output: ".",
    },
    htmlTemplateEngine: "njk",
    markdownTemplateEngine: false,
  };
};
