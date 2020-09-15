from flask_script import Manager,Server,Shell
# from flask_migrate import Migrate
from flask_migrate import MigrateCommand

from flaskr import create_app
from flaskr.models import *

app = create_app()
manager = Manager(app)
# migrate = Migrate(app,models.db)

#python manager.py server  取代runserver
#黑科技段
def make_shell_context():
    return dict(app=app, db=db, User=User)
    # return dict(app=app, db=models.db, User=models.User)

manager.add_command("shell", Shell(make_context=make_shell_context))

#
manager.add_command("server", Server(host='0.0.0.0', port=8081))
manager.add_command("db", MigrateCommand)

if __name__ == "__main__":
    manager.run()