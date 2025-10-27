from flask import Flask
import utils.db as db
from settings import settings
from controllers import main_bp, data_bp

app = Flask(__name__)
app.config.update(settings.flask_config)
# db.clear_database()
db.init_from_env()

app.register_blueprint(main_bp)
app.register_blueprint(data_bp)


if __name__ == '__main__':
    app.run(debug=True)
