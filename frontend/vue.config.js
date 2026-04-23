const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  // Uses /Pathfinder.Ai/ on GitHub Pages, / locally
  publicPath: process.env.VUE_APP_BASE_URL || '/',
  chainWebpack: config => {
    config.plugin('html').tap(args => {
      args[0].title = 'Pathfinder.Ai';
      return args;
    });
  }
})
