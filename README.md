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
- Para macro de producción: `requests` + `python-dotenv`

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

## Credenciales macroeconómicas

El módulo macro **no guarda claves en el código**. Carga automáticamente un `.env` local mediante `python-dotenv`.

Para un activo mexicano como `FMTY14.MX`, el análisis macro incluye **EUA + México**. Para activos no `.MX`, México no se consulta.

1. Copia `.env.example` a `.env`.
2. Completa tus credenciales reales:

```dotenv
FRED_API_KEY=TU_CLAVE_FRED
BANXICO_TOKEN=TU_TOKEN_BANXICO
```

También se acepta `BMX_TOKEN` como alias del token de Banxico.

**Nunca subas `.env` al repositorio.** Está excluido por `.gitignore`.

El bloque macro es contextual: no modifica directamente BUY/SELL/HOLD. Se utiliza para describir el régimen de tasas/inflación y el margen de seguridad requerido. FRED proporciona observaciones de series económicas mediante su endpoint de observaciones; Banxico SIE se utiliza para las series mexicanas. citeturn0search0turn1search1

## Ejecución

Desde la raíz del repositorio. El entry point actual es `investment_analyzer.cli` (archivo `src/investment_analyzer/cli.py`):

```bash
python -m investment_analyzer.cli AAPL
```

Ejemplo para un activo mexicano:

```bash
python -m investment_analyzer.cli FMTY14.MX
```

También puede ejecutarse con el Python del entorno virtual:

```powershell
.venv\Scripts\python.exe -m investment_analyzer.cli FMTY14.MX
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

Actualmente la composición de producción instala **Yahoo** como proveedor por defecto. El adaptador FMP existe, pero requiere que la aplicación le inyecte un cliente FMP compatible; no se debe asumir que una `FMP_API_KEY` por sí sola habilita FMP hasta que exista ese cliente/configuración.

## Estado

**V11 — integración en desarrollo.**

La arquitectura de decisión y las pruebas unitarias/integración están en construcción. Antes de considerar la aplicación lista para producción debe validarse una ejecución E2E con datos reales y comprobar la salida final del reporte.
