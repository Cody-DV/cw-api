import logging
from flask import Flask
from flask_cors import CORS
from routes import routes_bp

def create_app():
    app = Flask(__name__, instance_relative_config=False)
    CORS(app)  # Enable CORS for the app

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    app.register_blueprint(routes_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5174)