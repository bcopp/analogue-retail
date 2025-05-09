const { createProxyMiddleware } = require('http-proxy-middleware');

const requireEnv = (envVar) => {
    const value = process.env[envVar];
    if (!value) {
        throw new Error(`Required environment variable ${envVar} is not set`);
    }
    return value;
};

// Verify required environment variables exist
let apiUrl = requireEnv('REACT_APP_API_URL');

module.exports = function(app) {
    app.use(
        '/api',
        createProxyMiddleware({
            target: apiUrl,
            changeOrigin: true,
            secure: false,
            pathRewrite: {
                '^/api': '' // Remove /api prefix when forwarding to backend
            },
            logLevel: 'debug',
            onError: (err, req, res) => {
                console.error('Proxy Error:', err);
                res.writeHead(500, {
                    'Content-Type': 'text/plain',
                });
                res.end('Something went wrong with the proxy.');
            },
            onProxyReq: (proxyReq, req, res) => {
                console.log('Proxying request to:', proxyReq.path);
            }
        })
    );

    app.use(
        '/image',
        createProxyMiddleware({
            target: 'http://localstack:4566',
            changeOrigin: true,
            secure: false,
            logLevel: 'debug'
        })
    );
};