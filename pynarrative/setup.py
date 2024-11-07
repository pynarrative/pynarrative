from setuptools import setup, find_packages

setup(
    name='pynarrative',  # Nome del pacchetto
    version='0.1',   # Versione del pacchetto
    packages=find_packages(where='src'),  # Cerca pacchetti solo nella cartella 'src'
    package_dir={'': 'src'},  # Definisco 'src' come la directory principale del codice sorgente
    install_requires=[
        'altair',  # Dipendenza necessaria per il pacchetto
    ],
    author='Roberto Olinto Barsotti',
    author_email='robeolinto.barsotti@gmail.com',
    description='Una libreria per creare visualizzazioni narrative con Altair',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Versione minima di Python
)
