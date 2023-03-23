from contextlib import nullcontext
from flask import Flask
import logging

# crear un logger y especificar el nivel de log que se guardará en el archivo
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# crear un manejador de archivo para guardar los logs en un archivo local
handler = logging.FileHandler('app.log')
handler.setLevel(logging.INFO)

# crear un formateador para especificar el formato del log
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# agregar el manejador al logger
logger.addHandler(handler)
app = Flask(__name__)


from SeLeTiene import *
from ArbelaezApp import *



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

    