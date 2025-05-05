const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
    app.use(
        '/api',
        createProxyMiddleware({
            target: 'http://backend:8000',
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