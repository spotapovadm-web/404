FROM node:18-alpine
WORKDIR /app
RUN npx create-react-app . --template minimal --skip-git
RUN echo "import './App.css';\n\
function App() {\n\
  return (\n\
    <div className=\"App\">\n\
      <header className=\"App-header\">\n\
        <h1>Hello World</h1>\n\
      </header>\n\
    </div>\n\
  );\n\
}\n\
export default App;" > src/App.js
RUN npm run build
RUN npm install -g serve
EXPOSE 8080
CMD ["serve", "-s", "build", "-l", "8080"]
