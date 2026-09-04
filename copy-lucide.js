const fs = require("fs");
const path = require("path");

const origem = path.join(
  "node_modules",
  "lucide",
  "dist",
  "umd",
  "lucide.min.js",
);
const destino = path.join("frontend", "dist", "js", "lucide.min.js");

fs.copyFileSync(origem, destino);
console.log("Lucide copiado para frontend/dist/js/lucide.min.js");
