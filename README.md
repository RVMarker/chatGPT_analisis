# Investment Analyzer v11

Plataforma modular de análisis de inversiones con decisión separada por horizonte:

- **Estratégico:** años
- **Táctico:** semanas
- Scores transparentes y pesos explícitos
- Datos faltantes tratados como `N/D`, no como 50
- Macro y comparables como contexto, no como voto directo
- Reporte reproducible y auditable

## Requisitos

- Python 3.12+
- Para datos Yahoo: `yfinance`

## Instalación recomendada desde VSCode / terminal

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e ".[full,test]"
```

En PowerShell, si la política de ejecución bloquea la activación del entorno, puede usarse directamente:

```powershell
.venv\Scripts\python.exe -m pip install -e ".[full,test]"
```

## Ejecución

Desde la raíz del repositorio:

```bash
python -m investment_analyzer.cli.main AAPL
```

Ejemplo para un activo mexicano:

```bash
python -m investment_analyzer.cli.main FMTY14.MX
```

También puede ejecutarse con el Python del entorno virtual:

```powershell
.venv\Scripts\python.exe -m investment_analyzer.cli.main FMTY14.MX
```

## Validación

Ejecutar toda la suite:

```bash
python -m pytest -q
```

Smoke test:

```bash
python -m pytest -q tests/test_smoke.py
```

## Datos y disponibilidad

Los módulos no deben inventar señales cuando no existe evidencia suficiente. Un componente sin datos se representa como `N/D` y no debe aportar artificialmente 50 puntos al score. Los pesos de los componentes disponibles se renormalizan cuando corresponde.

El resultado debe distinguir siempre entre:

1. **Score de decisión** — qué tan favorable es la evidencia disponible.
2. **Confianza** — qué tan completa, fresca y consistente es esa evidencia.

La existencia de un score alto no implica por sí sola alta confianza.

## Proveedores y símbolos

El sistema conserva el símbolo introducido por el usuario y el símbolo utilizado por cada proveedor cuando son diferentes. Esto permite auditar casos como tickers mexicanos cuya nomenclatura no coincide entre proveedores.

## Estado

**V11 — integración en desarrollo.**

La arquitectura de decisión y las pruebas unitarias/integración están en construcción. Antes de considerar la aplicación lista para producción debe validarse una ejecución E2E con datos reales y comprobar la salida final del reporte.
