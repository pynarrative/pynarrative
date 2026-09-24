from setuptools import setup, find_packages

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='pynarrative',  # Nome del pacchetto
    version='2.0',   # Versione del pacchetto
    packages=find_packages(where='src'),  # Cerca pacchetti solo nella cartella 'src'
    package_dir={'': 'src'},  # Definisco 'src' come la directory principale del codice sorgente
    install_requires=[ #Dipendenze
        "altair",
        "geopandas",
        "numpy",
        "pandas",
    ],
    author='Roberto Olinto Barsotti, Angelica Lo Duca, Lorenzo Ferrante',
    author_email='robeolinto.barsotti@gmail.com, angelica.loduca@iit.cnr.it, lorenzo.ferrante04@gmail.com',
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
