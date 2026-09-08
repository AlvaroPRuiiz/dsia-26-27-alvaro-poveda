1. Diferencia entre Python global y `.venv`.  

    Python se encuentra instalado en el ordenador de forma global mientras que .venv crea un entorno aislado asociado a un solo proyecto. En este se pueden descargar herramientas y versiones de las mismas diferentes para cada entorno.

2. ¿Para qué sirve `python -m pip` frente a llamar solo a `pip`?

    Realiza el pip pero usando el interprete de python que este seleccionado en ese entorno. 

3. Explica working tree / staging / commit.  

    El working tree contiene toda la estructura de ficheros del proyecto.
    El staging area son todos los cambios que se han producido desde el ultimo git add. 
    El commit guarda un cierto título que asignes los cambios nuevos que se van a realizar tras el último git add.

4. ¿Clone y pull son lo mismo? ¿Por qué?  

    No, clone sirve para poder modificar un repositorio y contribuir a los cambios del mismo junto con otras personas mientras que el pull duplica el proyecto pero no permite realizar cambios compartidos con otras personas en el repositorio principal. 

5. Lista cuatro cosas que no se suben a GitHub y justifica una.  

    .venv
    .env 
    API keys o contraseñas
    Información personal o clasificada

6. Reescribe a buen estilo: `update`, `fix final`, `cambios varios`.  

7. ¿Qué haces si el IDE no importa `pandas` pero la terminal sí?  

    python -c "import sys; print(sys.executable)"
    .venv\Scripts\python.exe
    python -m pip install pandas

8. ¿Qué haces si subiste `.env` por error?

    git rm --cached .env y volver a hacer commit y push de los cambios 