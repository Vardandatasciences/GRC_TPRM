module.exports = {
  presets: [
    '@vue/cli-plugin-babel/preset',
    // Add TypeScript support for TPRM components
    ['@babel/preset-typescript', { 
      isTSX: true,
      allExtensions: true 
    }]
  ],
  plugins: []
}
