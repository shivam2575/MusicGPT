import os
import warnings

from langchain_core.messages import AIMessage
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

warnings.filterwarnings("ignore")

LLM = ChatOpenAI(
    model="gpt-4",
    api_key=os.getenv("OPENAI_KEY"),
    temperature=0
)


class ResponseSynthesizerOutputTemplate(BaseModel):
    final_response: str = Field(description="The response for the user based on the previous agent's output.")


class ResponseSynthesizer:
    def __init__(self):
        self.model = LLM

    def _get_prompts(self):
        system_prompt = (
            "You are the **Final Response Synthesizer Agent** in a movie recommendation chatbot.\n\n"
            "Your role is to deliver the final response to the user after the Movie Recommendation Agent has processed their request.\n\n"
            "Your tasks:\n"
            "1. If the Movie Recommendation Agent has returned a valid movie suggestion, present it in a friendly and engaging manner.\n"
            "   - Include a short summary or reason if available.\n"
            "   - Conclude warmly and offer to help with another suggestion if the user is interested.\n\n"
            "2. If the recommendation indicates that **additional input is still required** or the movie could not be recommended yet due to missing context:\n"
            "   - Politely let the user know that a bit more information is needed.\n"
            "   - Clearly ask the appropriate follow-up question (e.g., missing genre, language, or other preference).\n"
            "   - Encourage the user to share that information so a great recommendation can be made.\n\n"
            "Guidelines:\n"
            "- Be polite, helpful, and conversational.\n"
            "- Do not invent a movie or rephrase the logic of the Movie Recommendation Agent.\n"
            "- Ensure your message matches the tone and completeness of the previous agent’s response.\n\n"
            "Examples:\n"
            "If a recommendation is available:\n"
            "- Based on your interest in romantic comedies in Hindi, I’d suggest *Jab We Met*. It’s a heartwarming story with charming characters and great music. Let me know if you'd like another option!\n\n"
            "If input is still needed:\n"
            "- It sounds like we're almost there! Could you please tell me what language you’d prefer the movie to be in?\n"
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
            agent_prompt = agent_prompt | self.model.with_structured_output(ResponseSynthesizerOutputTemplate)

            # AI Call
            response = await agent_prompt.ainvoke({'response_instruction': response_instruction})
            state["messages"] = [AIMessage(content=response.final_response, name='Response Synthesizer Agent')]
            state["agent_call_list"] = ["Response-Synthesizer-Agent"]
            return state

        except Exception as err:
            raise ValueError(f"Error caught in Response Synthesizer Agent: {str(err)}")