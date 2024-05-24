# Gestor Codi

## Descripció

Gestor-Codi és una plataforma de gestió de codi font per a projectes de programació. Aquesta plataforma permet la creació de tasques, recollida de trameses i avaluació de codi font. També incorpora una secció de documents i apunts per a la realització de les tasques.

## Instal·lació i posada en marxa

- Descarrega el repositori amb `git clone https://github.com/pgiuli/gestor-codi`.
- Un cop dins la carpeta crea un entorn virtual en aquesta amb `python -m venv .`.
- Activa l'entorn virtual amb `.\Scripts\activate` (Windows) o `source bin/activate` (Linux/macOS).
- Instal·la les dependències amb `pip install -r requirements.txt`.
- Crea la base de dades amb `python db.py`.
- Inicia el servidor amb `python gestor.py`.

### Aplicació WSGI
Si has d'usar aquesta app en un servidor WSGI, has de configurar el servidor per a que executi l'arxiu `gestor.py` amb l'aplicació `gestor` de Flask.

## TO-DO

- Reformulació de l'estructura de la base de dades (una taula per a tots els arxius i enllaços en la resta de taules).
- Unió dels dashboards de d'administrador i usuari general.
- Arxiu de configuració general (noms d'arxiu, títols, estils, etc.).
- Traduccions.
