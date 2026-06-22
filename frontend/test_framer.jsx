import React from 'react';
import { renderToString } from 'react-dom/server';
import { AnimatePresence } from 'framer-motion';

try {
  const html = renderToString(
    <AnimatePresence>
      {"" && <div />}
    </AnimatePresence>
  );
  console.log("Success:", html);
} catch (e) {
  console.error("Crash!", e.message);
}
