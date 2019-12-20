# run the app in a production environment

# import the app
from log import app

# setup logging to a file
import logging
logging.basicConfig(filename=app.config['LOG_PATH'], level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

# run it without debug
if __name__ == "__main__":
    app.run()