import { createServer } from 'vite';

async function test() {
  const server = await createServer({
    server: { middlewareMode: true },
    appType: 'custom'
  });
  try {
    await server.ssrLoadModule('/src/main.jsx');
    console.log("Module loaded successfully without throwing");
  } catch (e) {
    console.error("RUNTIME ERROR:");
    console.error(e);
  } finally {
    await server.close();
  }
}

test();
