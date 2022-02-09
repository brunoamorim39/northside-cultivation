from werkzeug.middleware.proxy_fix import ProxyFix
from __init__ import app
import routes

if __name__ == '__main__':
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    app.run(debug=True, threaded=True)