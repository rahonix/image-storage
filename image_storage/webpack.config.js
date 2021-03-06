const path = require('path');

module.exports = {
  entry: {
    dataset: './assets/dataset/index.js',
    image: './assets/image/index.js',
  },
  output: {
    filename: '[name].js',  // output bundle file name
    path: path.resolve(__dirname, './static'),  // path to our Django static directory
  },
  module: {
    rules: [
      {
        test: /\.css$/i,
        use: ["style-loader", "css-loader"],
      },
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        loader: "babel-loader",
        options: { presets: ["@babel/preset-env", "@babel/preset-react"] }
      },
    ],
  },
};