# Diseño de ventas_app

- **SRP (Single Responsibility Principle)** — validator.py se encarga únicamente de aplicar las reglas de validación y separar las ventas válidas de las inválidas. La lectura pertenece a loader.py y las agregaciones a metrics.py.

- **OCP (Open/Closed Principle)** —`metrics.py permite añadir nuevas agregaciones o KPIs sin modificar la lógica de carga ni las reglas de validación existentes.

- **DIP (Dependency Inversion Principle)** — la orquestación utiliza el contrato SalesRepository para obtener los datos, mientras que CsvSalesRepository contiene el detalle concreto de lectura del CSV. De este modo podría añadirse otra fuente de datos sin modificar las reglas de negocio.