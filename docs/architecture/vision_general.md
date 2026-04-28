# Visión General de la Arquitectura: Plataforma de Revenue Automation

## 1. Visión
La plataforma está diseñada para convertir señales predictivas (churn, upsell, riesgo) en acciones automáticas que protegen el revenue, utilizando un sistema multi-agente. Equilibra la autonomía con una gobernanza estricta (guardrails) y aislamiento multi-tenant.

## 2. Componentes Core

### Capa de Inteligencia (Intelligence Layer)
- **Model Gateway**: Punto de entrada FastAPI para predicciones externas.
- **Signal Normalizer**: Limpieza y enriquecimiento de datos basado en PySpark.
- **FIA (Financial Intelligence Agent)**: El "Cerebro". Calcula el impacto económico (ROI) y prioriza acciones.

### Capa de Ejecución (Execution Layer)
- **Workflow Engine**: Orquestado por **LangGraph**. Gestiona la máquina de estados y las transiciones entre agentes.
- **Policy Engine**: Reglas de negocio centralizadas y guardrails.
- **SEA (Sales Execution Agent)**: Las "Manos". Ejecuta acciones a través de adaptadores de CRM, ERP y Mensajería.

### Capa de Infraestructura (Infrastructure Layer)
- **Persistencia**: Base de datos SQL multi-tenant (SQLAlchemy).
- **Memoria**: Almacén de vectores semánticos (ChromaDB) para recuperación de políticas vía RAG.
- **Telemetría**: MLflow para el seguimiento de decisiones, experimentos y resultados de negocio.

## 3. Flujo de Datos
1. **Ingesta**: Las predicciones llegan al Gateway.
2. **Normalización**: Los datos se limpian y convierten en `InternalSignals`.
3. **Decisión**: FIA clasifica las señales y crea un `RevenueCommand` con una justificación.
4. **Validación**: El Policy Engine verifica restricciones (márgenes, topes) y emite un `validation_token`.
5. **Ejecución**: SEA verifica el token e interactúa con SAP (ERP) o Salesforce (CRM).
6. **Seguimiento**: Los resultados (outcomes) se registran en MLflow para análisis de rendimiento.

## 4. Principios de Diseño Clave
- **Multi-tenancy**: Aislamiento estricto a nivel de BD y memoria.
- **Idempotencia**: Evita acciones duplicadas dentro de las ventanas de validez.
- **Auditabilidad**: Cada decisión está justificada y registrada con un trace ID.
