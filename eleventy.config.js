const fs = require("fs");

module.exports = function (eleventyConfig) {
  // Snippet-Dateien roh einlesen (keine Template-Verarbeitung — Inhalte
  // enthalten CSS/JS mit {#- und {%-Sequenzen, die Nunjucks stören würden)
  eleventyConfig.addShortcode("rawfile", function (path) {
    return fs.existsSync(path) ? fs.readFileSync(path, "utf8") : "";
  });

  return {
    dir: {
      input: "src/pages",
      includes: "../_includes",
      output: ".",
    },
    htmlTemplateEngine: "njk",
    markdownTemplateEngine: false,
  };
};
