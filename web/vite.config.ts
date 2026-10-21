import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'
import { createReadStream } from 'node:fs'

/** Serve only these two exports in dev. No backend dependency or broad filesystem access. */
function creaturePreviewAssets() {
  const exports = ['cetus-texture.glb', 'cetus-model.glb']
  return {
    name: 'creature-preview-assets',
    configureServer(server: import('vite').ViteDevServer) {
      server.middlewares.use((request, response, next) => {
        const file = exports.find((name) => request.url?.split('?')[0] === `/dev-assets/${name}`)
        if (!file) return next()
        const stream = createReadStream(new URL(`../assets/breeds/cetus/${file}`, import.meta.url))
        stream.on('error', () => {
          response.statusCode = 404
          response.end('Model not found')
        })
        response.setHeader('Content-Type', 'model/gltf-binary')
        stream.pipe(response)
      })
    },
  }
}

export default defineConfig({
  plugins: [react(), creaturePreviewAssets()],
  server: { port: 5173, strictPort: true }, // the API's CORS allows exactly FRONTEND_URL
})
