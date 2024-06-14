# main.py

from flask_sqlalchemy import SQLAlchemy
# from flask import Flask

#urlparse
from urllib.parse import quote_plus



# app = Flask(__name__)

connection_format = 'mssql+pymssql://{0}:{1}@{2}/{3}?charset=utf8'
connection_str = connection_format.format('sa',quote_plus("pass@word1"),'10.8.0.6','C10')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = connection_str
db = SQLAlchemy(app)



class Users(db.Model):
    _id = db.Column('no', db.Integer, primary_key=True)
    name = db.Column('stockcode', db.String(100))
    email = db.Column('stockname',db.String(100))
    def __init__(self, name, email):
        self.name =name
        self.email = email


db.create_all()


usr = Users('9999','test')
db.session.add(usr)
db.session.commit()




# db.init_app(app)

# @app.route('/')
# def index():

sql_cmd = """
    select *
    from stockinfo
    """

query_data = db.engine.execute(sql_cmd)
print(query_data)
    # return 'ok'


# if __name__ == "__main__":
#     app.run()