# NASA
Practica para hackaton de la nasa.

## Cómo ejecutar (frontend + backend)

### 1. Backend FastAPI
```bash
cd backend
uvicorn main:app --reload --port 8000
```
- Endpoints: `GET /drought-risk` (serie histórica) y `GET /drought-risk/summary` (estado actual).
- Consume datos de temperatura y precipitación de NASA POWER.

### 2. Frontend Streamlit
```bash
cd frontend
streamlit run app.py
```
- Abre http://localhost:8501
- Configura ubicación, periodo y variables en la barra lateral y presiona **Cargar datos**.
- La app consulta el backend (`http://localhost:8000`) y muestra métricas del riesgo de
  sequía, gráficas de evolución, clima diario, medidor y mapa.

> La URL del backend se configura con la variable de entorno `NASA_API_URL`
> (por defecto `http://localhost:8000`).
