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


class ArgumentAnalyserOutputTemplate(BaseModel):
    agent_response: str = Field(
        description="Response for the supervisor agent, whether it needs more information from the user or sufficient "
                    "information if received."
    )


class ArgumentAnalyzer:
    def __init__(self):
        self.model = LLM

    def _get_prompts(self):
        system_prompt = (
            "You are the **Input Argument Analyzer Agent**, supporting a Supervisor Agent in a movie recommendation assistant system.\n\n"
            "Your job is to assist the Supervisor Agent by checking whether all necessary user inputs have been collected before a movie can be recommended.\n"
            "The required arguments are:\n"
            "- Genre (e.g., comedy, thriller, drama)\n"
            "- Language (e.g., English, Hindi, Spanish)\n"
            "- Optional: Year, mood, or other relevant preferences\n\n"
            
            "Your responsibilities:\n"
            "1. Analyze the conversation history and current user input to determine if all required information has been provided.\n"
            "2. If any required input is missing, **clearly specify all the required information and send that as response to the supervisor.**"
            "As the supervisor will then route the output for the final response generation.\n"
            "3. If all required inputs are already present, inform the Supervisor Agent that we have everything needed and it can proceed to the movie recommendation step.\n\n"
            
            "Guidelines:\n"
            "- Your responses are **not directly shown to the user**, but will be routed through the Supervisor Agent.\n"
            "- Do NOT generate or suggest any movies yourself.\n"
            "- If input is incomplete, say something like: `More information is needed from the user. Please ask them: 'Any specific language preference for the movie?'`\n"
            "- If input is complete, say something like: `All required arguments are present. We are ready to recommend a movie.`\n"
            "- Maintain a professional and cooperative tone, as your communication is with the Supervisor Agent, not the end user directly."
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
            state["messages"] = [AIMessage(content=response.agent_response, name='Input-Argument-Analyzer-Agent')]
            state["agent_call_list"] = ["Input Argument Analyzer Agent"]
            return state

        except Exception as err:
            raise ValueError(f"Error caught in InputArgumentAnalyserAgent: {str(err)}")