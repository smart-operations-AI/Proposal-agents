# ADR 001: Selección del Motor de Orquestación (LangGraph)

## Estado
Aceptado

## Contexto
Necesitamos un framework para orquestar interacciones complejas entre agentes (FIA, SEA) y servicios externos (Policy Engine). El flujo de trabajo requiere gestión de estado, ciclos (reintentos) y ramificaciones condicionales (escalamiento/guardrails).

## Decisión
Hemos seleccionado **LangGraph** para la orquestación.

## Justificación
- **Persistencia de Estado**: LangGraph ofrece soporte nativo para checkpoints y persistencia del estado a través de los pasos de los agentes.
- **Ciclos y Bucles**: A diferencia de los motores de DAG lineales, LangGraph permite ciclos, esenciales para reintentos y bucles de retroalimentación.
- **Flujo Multi-Agente**: Proporciona una forma clara de definir nodos (agentes) y aristas (transiciones), facilitando la visualización y auditoría del protocolo.
- **Human-in-the-loop**: El soporte integrado para breakpoints facilita el escalamiento humano.

## Consecuencias
- **Positivo**: Alta flexibilidad para protocolos agénticos complejos y observabilidad integrada.
- **Negativo**: Curva de aprendizaje más pronunciada en comparación con scripts lineales simples.
- **Dependencia**: Dependemos del ecosistema de LangChain/LangGraph.
