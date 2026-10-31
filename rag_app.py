"""Módulo RAG experimental e independiente para consultar PROVIDERS con Gemini."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import streamlit as st

from server import PROVIDERS


@dataclass(frozen=True)
class RAGSearchResult:
    answer: str
    providers: list[dict[str, Any]]


def load_key() -> str | None:
    """Carga la clave local y la expone con el nombre que LangChain espera."""
    from dotenv import load_dotenv

    env_path = Path(__file__).resolve().with_name(".env")
    load_dotenv(dotenv_path=env_path, override=False)


    clave = (
        st.secrets.get("GEMINI_API_KEY")
        or st.secrets.get("GOOGLE_API_KEY")
        or os.environ.get("GEMINI_API_KEY")
        or os.environ.get("GOOGLE_API_KEY")
    )
    if clave:
        os.environ["GOOGLE_API_KEY"] = clave
    return clave


def _crear_componentes_rag():
    """Construye el modelo, el recuperador y el prompt cuando se necesitan."""
    if not load_key():
        raise RuntimeError(
            "Configura GEMINI_API_KEY en el archivo .env o como variable de entorno."
        )

    from langchain_chroma import Chroma
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_google_genai import (
        ChatGoogleGenerativeAI,
        GoogleGenerativeAIEmbeddings,
    )

    llm = ChatGoogleGenerativeAI(model="gemini-3.8-flash", temperature=0.2)
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")

    corpus_textos = []
    metadatos = []
    for item in PROVIDERS:
        servicios_str = ", ".join(item["services"])
        dias_str = ", ".join(item["days"])
        texto = (
            f"La proveedora {item['name']} trabaja en la zona de {item['area']}. "
            f"Ofrece servicios de {servicios_str}. Su tarifa es de {item['fee']} "
            f"USD por hora con una calificación de {item['rating']}. Trabaja los "
            f"días {dias_str} en horario de {item['start']} a {item['end']}."
        )
        corpus_textos.append(texto)
        metadatos.append({"provider_id": item["id"]})

    vectorstore = Chroma.from_texts(
        texts=corpus_textos,
        embedding=embeddings,
        collection_name="techcorp_docs",
        metadatas=metadatos,
        ids=[f"doc-{i}" for i in range(len(corpus_textos))],
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Responde en español usando SOLO este contexto. "
                "Si no está, di que no lo sabes.\n\n{context}",
            ),
            ("human", "{question}"),
        ]
    )
    return llm, retriever, prompt


def _unir_documentos(documentos) -> str:
    return "\n\n".join(documento.page_content for documento in documentos)


def crear_cadena_rag():
    """Construye la cadena RAG al invocarla, no al importar este módulo."""
    from langchain_core.runnables import RunnableLambda, RunnablePassthrough

    llm, retriever, prompt = _crear_componentes_rag()
    return (
        {"context": retriever | _unir_documentos, "question": RunnablePassthrough()}
        | prompt
        | llm
        | RunnableLambda(lambda message: message.text)
    )


def buscar_resultados_con_rag(transcripcion: str) -> RAGSearchResult:
    """Devuelve la respuesta RAG y las proveedoras que la sustentan."""
    pregunta = transcripcion.strip()
    if not pregunta:
        raise ValueError("La transcripción está vacía.")

    pregunta_rag = f"¿Cuáles proveedoras están disponibles para {pregunta}?"
    llm, retriever, prompt = _crear_componentes_rag()
    documentos = retriever.invoke(pregunta_rag)
    respuesta = (prompt | llm).invoke(
        {
            "context": _unir_documentos(documentos),
            "question": pregunta_rag,
        }
    )

    providers_by_id = {provider["id"]: provider for provider in PROVIDERS}
    proveedores = []
    ids_agregados = set()
    for documento in documentos:
        provider_id = documento.metadata.get("provider_id")
        if provider_id in providers_by_id and provider_id not in ids_agregados:
            proveedores.append(providers_by_id[provider_id])
            ids_agregados.add(provider_id)

    return RAGSearchResult(answer=respuesta.text, providers=proveedores)


def buscar_disponibilidad_con_rag(transcripcion: str) -> str:
    """Consulta el RAG y devuelve solo su respuesta en texto."""
    return buscar_resultados_con_rag(transcripcion).answer
