class OllamaService:
    @staticmethod
    def ask_model(query: str, context: str) -> dict:
        """Запрос к модели Ollama с учетом контекста.
        
        Args:
            query (str): Вопрос пользователя.
            context (str): Контекст для формирования ответа.
        
        Returns:
            dict: Ответ от модели или информация об ошибке.
        """
        import requests
        import json
        from src.helpers.configs_hub import ollama_config
        
        # Формирование промпта с учетом контекста
        prompt = ollama_config.ollama.prompt.format(query=query, context=context)
        
        # Запрос к модели
        response = requests.post(
            ollama_config.ollama.generate_url,
            data=json.dumps({
                "model": ollama_config.ollama.models.llama3,
                "prompt": prompt,
                "stream": False,
            }),
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == requests.codes.ok:
            result = response.json()
            return {"response": result.get("response", "")}
        else:
            return {"error": f"Ошибка {response.status_code}: {response.text}"}
