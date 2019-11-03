# run the app in a production environment

# setup logging to a file
import logging
logging.basicConfig(filename='/opt/log-api/logs/api.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

# import the app
from log import app

# run it without debug
if __name__ == "__main__":
    app.run()