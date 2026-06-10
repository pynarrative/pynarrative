from setuptools import setup, find_packages

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='pynarrative',  # Nome del pacchetto
    version='0.4',   # Versione del pacchetto
    packages=find_packages(where='src'),  # Cerca pacchetti solo nella cartella 'src'
    package_dir={'': 'src'},  # Definisco 'src' come la directory principale del codice sorgente
    install_requires=[
        'altair',  # Dipendenza necessaria per il pacchetto
    ],
    author='Roberto Olinto Barsotti, Angelica Lo Duca',
    author_email='robeolinto.barsotti@gmail.com, angelica.loduca@iit.cnr.it',
    description='Una libreria per creare visualizzazioni narrative con Altair',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Versione minima di Python
    long_description=long_description,
    long_description_content_type='text/markdown'
)
