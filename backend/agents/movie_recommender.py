import os
import warnings

from langchain_core.messages import AIMessage
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

warnings.filterwarnings("ignore")

LLM = ChatOpenAI(
    model="gpt-4",
    api_key=os.getenv("OpenAiKey"),
    temperature=0
)


class ArgumentAnalyserOutputTemplate(BaseModel):
    movie_recommended: str = Field(description="Contains the recommended movie name.")
    movie_description: str = Field(description="Contains the description of the movie.")


class MovieRecommender:
    def __init__(self):
        self.model = LLM

    def _get_prompts(self):
        system_prompt = (
            "You are the **Movie Recommendation Agent** in an agentic conversational system designed to help users discover great movies.\n\n"
            "You are called **only after** all required user preferences have been gathered and validated. These include:\n"
            "- Genre (e.g., action, comedy, sci-fi)\n"
            "- Language (e.g., English, Hindi, Spanish)\n"
            "- Optionally: year, mood, or other relevant preferences\n\n"
        
            "You serve as an **assistant to the Supervisor Agent**, and your role is to generate the best possible movie recommendation "
            "based on the provided inputs. Your response will **not be shown directly to the user**. Instead, it will be passed back to "
            "the Supervisor, who will route it to the **Response Synthesizer Agent**, which delivers the final user-facing message.\n\n"
        
            "Your responsibilities:\n"
            "1. Use the provided inputs to recommend a high-quality movie that matches the user's criteria.\n"
            "2. Return exactly one suggestion unless explicitly requested for more options.\n"
            "3. Include a short, compelling explanation of why the movie is a good match.\n\n"
        
            "Guidelines:\n"
            "- Keep your output clear, friendly, and concise — it will be further processed before the user sees it.\n"
            "- Do not ask any follow-up questions or assume missing data.\n"
            "- Avoid recommending extremely popular or overused titles unless they are a perfect match.\n"
            "- For niche or rare input combinations, suggest a hidden gem or lesser-known film that fits well.\n"
            "- Pick standout options — based on critical acclaim, uniqueness, or strong alignment with preferences.\n"
        )


        return PromptTemplate(
            template=system_prompt
        )

    async def perform_task(self, state):
        try:
            response_instruction = state["supervisor_instructions"][-1]
            # print("Supervisor instruction: ", response_instruction)

            agent_prompt = ChatPromptTemplate.from_messages([
                SystemMessagePromptTemplate(prompt=self._get_prompts()),
                *state['messages']
            ])

            # Binding the output format
            agent_prompt = agent_prompt | self.model.with_structured_output(ArgumentAnalyserOutputTemplate)

            # AI Call
            response = await agent_prompt.ainvoke({'response_instruction': response_instruction})
            response_message = (
                f"MOVIE RECOMMENDATION: {response.movie_recommended}"
                "\n"
                f"MOVIE DESCRIPTION: {response.movie_description}"
            )
            state["messages"] = [AIMessage(content=response_message, name='Movie-Recommendation-Agent')]
            state["agent_call_list"] = ["Movie Recommendation Agent"]
            return state

        except Exception as err:
            raise ValueError(f"Error caught in InputArgumentAnalyserAgent: {str(err)}")