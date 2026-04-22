const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  // Uses /Pathfinder.Ai/ on GitHub Pages, / locally
  publicPath: process.env.VUE_APP_BASE_URL || '/'
})
