from flask import Flask 
app = Flask(__name__, 
    template_folder="../templates", 
    static_url_path="/static", static_folder="../static")

app.secret_key = "123456789"

from app import views_public, views_admin, views_customers, views_planners
