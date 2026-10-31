import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from rag_app import (
    RAGSearchResult,
    buscar_disponibilidad_con_rag,
    buscar_resultados_con_rag,
)


class RagSearchTests(unittest.TestCase):
    @patch("rag_app._crear_componentes_rag")
    def test_returns_answer_and_retrieved_providers(self, create_components):
        documents = [
            SimpleNamespace(
                page_content="Rosa offers deep cleaning.",
                metadata={"provider_id": 2},
            ),
            SimpleNamespace(
                page_content="Ana offers general cleaning.",
                metadata={"provider_id": 1},
            ),
        ]
        retriever = Mock()
        retriever.invoke.return_value = documents
        prompt = Mock()
        llm = Mock()
        llm.invoke.return_value = SimpleNamespace(text="Resultados")

        class PromptChain:
            def invoke(self, values):
                return llm.invoke(values)

        prompt.__or__ = Mock(return_value=PromptChain())
        create_components.return_value = (llm, retriever, prompt)

        result = buscar_resultados_con_rag("  necesito limpieza el lunes  ")

        self.assertIsInstance(result, RAGSearchResult)
        self.assertEqual(result.answer, "Resultados")
        self.assertEqual(
            [provider["id"] for provider in result.providers],
            [2, 1],
        )
        question = "¿Cuáles proveedoras están disponibles para necesito limpieza el lunes?"
        retriever.invoke.assert_called_once_with(question)
        llm.invoke.assert_called_once_with(
            {
                "context": "Rosa offers deep cleaning.\n\nAna offers general cleaning.",
                "question": question,
            }
        )

    @patch("rag_app.buscar_resultados_con_rag")
    def test_existing_search_function_still_returns_answer_text(self, search):
        search.return_value = RAGSearchResult("Resultados", [])

        result = buscar_disponibilidad_con_rag("necesito limpieza")

        self.assertEqual(result, "Resultados")
        search.assert_called_once_with("necesito limpieza")

    def test_rejects_empty_transcription_without_running_rag(self):
        with patch("rag_app._crear_componentes_rag") as create_components:
            with self.assertRaisesRegex(ValueError, "transcripción está vacía"):
                buscar_disponibilidad_con_rag("  ")

        create_components.assert_not_called()


if __name__ == "__main__":
    unittest.main()
