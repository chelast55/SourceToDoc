from dataclasses import dataclass
from openai import OpenAI


@dataclass
class LLM:
    client: OpenAI
    model: str

    @staticmethod
    def create_LLM(base_url: str, api_key: str, model: str):
        """Convenience method to create a new LLM instance."""
        return LLM(OpenAI(base_url=base_url, api_key=api_key), model)

    def call_llm(self, system_prompt: str, prompt: str) -> str:
        """
        Calls the Chat Completions API.

        Parameters
        ----------
        prompt : str
            The user message.

        Returns
        -------
        str
            The the reponse message of the LLM.

        Raises
        ------
        APIError

        RuntimeError
            If the reponse message is None.
        """

        response = self.client.chat.completions.create(
            model=self.model,
            seed=0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
        ])
        result = response.choices[0].message.content
        if result is not None:
            return result
        else:
            raise RuntimeError
