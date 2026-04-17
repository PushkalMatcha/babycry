const { createProxyMiddleware } = require("http-proxy-middleware");

function parseStreamUrl() {
  const raw = process.env.REACT_APP_STREAM_URL || "http://127.0.0.1:5000/video";

  try {
    const parsed = new URL(raw);
    return {
      target: `${parsed.protocol}//${parsed.host}`,
      path: `${parsed.pathname}${parsed.search}` || "/video",
    };
  } catch (_err) {
    return {
      target: "http://127.0.0.1:5000",
      path: "/video",
    };
  }
}

module.exports = function setupProxy(app) {
  const { target, path } = parseStreamUrl();

  app.use(
    "/video-proxy",
    createProxyMiddleware({
      target,
      changeOrigin: true,
      secure: false,
      ws: false,
      pathRewrite: () => path,
      headers: {
        "ngrok-skip-browser-warning": "true",
      },
      on: {
        proxyReq(proxyReq) {
          // Required for ngrok free-domain browser interstitial bypass.
          proxyReq.setHeader("ngrok-skip-browser-warning", "true");
        },
      },
    })
  );
};
