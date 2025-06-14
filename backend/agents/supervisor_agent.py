import os
import warnings
from collections import Counter
from typing import Literal, Optional

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

warnings.filterwarnings("ignore")

LLM = ChatOpenAI(
    model="gpt-4",
    api_key=os.getenv("OpenAiKey"),
    temperature=0
)


class SupervisorOutput(BaseModel):
    next: Literal["Response Synthesizer Agent", "Input Argument Analyzer Agent", "Movie Recommendation Agent"]
    agent_instructions: Optional[str] = Field(
        description="Specific instructions for the selected agent to guide their work on this task",
    )


# class Supervisor:
#     def __init__(self):
model = LLM
agent_descriptions = {
    "Input Argument Analyzer Agent": (
        "This agent is responsible for validating the completeness of user-provided inputs necessary for a movie "
        "recommendation. It checks for required arguments such as genre and language, and optionally year, mood, or other "
        "preferences. Based on the current state of the conversation, it determines whether more information is needed or "
        "if the input is complete.\n\n"
        "The Input Argument Analyzer Agent does not speak directly to the user. Instead, it crafts follow-up questions "
        "or completion confirmations to be routed through the Supervisor Agent. It is a supportive assistant that helps "
        "ensure the recommendation logic is triggered only when the user's preferences are fully understood."
    ),

    "Movie Recommendation Agent": (
        "This agent is responsible for generating personalized movie suggestions based on the complete input provided by the user. "
        "It considers user-specified preferences like genre, language, and optionally mood or year to identify and recommend "
        "a suitable movie. It leverages cinematic knowledge to ensure the recommendation is relevant, high-quality, and tailored.\n\n"
        "The Movie Recommendation Agent operates as an assistant to the Supervisor Agent. It never communicates directly with the user; "
        "its recommendations are passed back to the Supervisor, which coordinates the final response flow."
    ),

    "Response Synthesizer Agent": (
        "This agent is responsible for crafting the final message that will be shown directly to the user. It can be called in two scenarios: "
        "(1) when a valid movie recommendation has been generated, or (2) when additional information is still needed to proceed.\n\n"
        "The Response Synthesizer Agent translates structured or technical outputs from other agents into engaging, friendly, and "
        "user-facing messages. It ensures clarity, tone, and completeness in the final delivery.\n\n"
        "While it is also an assistant to the Supervisor Agent, it is unique in that **its responses are the only ones delivered directly "
        "to the user**, making it a key component for user experience and conversation polish."
    )
}

def _get_prompts(list_agents, agent_descriptions_text):
    system_prompt = (
        "You are a **Supervisor Agent** in a conversational movie recommendation service, responsible for orchestrating the workflow "
        "between the following specialized assistant agents: " + ', '.join(list_agents) + ". Below are the descriptions of these agents:"
        "\n\n" + agent_descriptions_text + "\n\n"

        "Your primary objective is to help the user find a great movie to watch. However, you do not interact directly with the user yourself. "
        "Instead, you coordinate the flow by delegating responsibilities to your assistant agents. Only the **Response Synthesizer Agent** is "
        "authorized to respond directly to the user — all other agents communicate their results back to you, and you route their output "
        "through the Response Synthesizer for final delivery.\n\n"

        "Here is how you should manage the flow:\n\n"

        "**Step 1: Input Collection**\n"
        "- Start by calling the **Input Argument Analyzer Agent** to check whether all required user inputs have been provided.\n"
        "- Required inputs typically include: genre, language, and optionally year, mood, or other preferences.\n"
        "- If any required input is missing, the Input Argument Analyzer tell you the arguments/information that needs to be gathered from the user.\n"
        "- Route this output from the argument analyser to the **Response Synthesizer Agent** so it can ask the user in a natural, friendly way.\n"
        "- Repeat this step (via user responses) until the Input Argument Analyzer confirms that all necessary information has been collected.\n\n"

        "**Step 2: Recommendation**\n"
        "- Once the Input Argument Analyzer confirms that all necessary inputs are present, call the **Movie Recommendation Agent**.\n"
        "- It will return a personalized movie suggestion based on the collected inputs.\n"
        "- Route the recommendation to the **Response Synthesizer Agent**, who will deliver it to the user in a polished, engaging message.\n\n"

        "**Step 3: Completion or Follow-up**\n"
        "- If a movie recommendation has been provided, allow the user to either conclude or request another.\n"
        "- **If the Input Argument Analyzer Agent tells that more information is still required, continue the input collection process by invoking Response Synthesizer Agent.**\n\n"

        "**Important Guidelines:**\n"
        "- NEVER send outputs from the Input Argument Analyzer or Movie Recommendation Agent directly to the user.\n"
        "- ALWAYS pass final outputs to the **Response Synthesizer Agent** for user-facing communication.\n"
        "- ONLY use agents listed in the current execution context. Do not invoke undefined agents.\n"
    )

    return system_prompt

def supervisor_agent(state):
    try:
        agent_call_list = Counter(state["agent_call_list"])
        agents_available = list(agent_descriptions.keys())

        available_options = []
        for agent in agents_available:
            if agent_call_list[agent] < 2:
                available_options.append(agent)

        agent_descriptions_text = "\n".join(
            [f"{agent}: {description}" for agent, description in agent_descriptions.items()]
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", _get_prompts(
                list_agents=agent_call_list,
                agent_descriptions_text=agent_descriptions_text
            )),
            MessagesPlaceholder(variable_name="messages"),
            (
                "system",
                "Based on the conversation above, select the next agent:\n"
                "- Who should act next? **Strictly select one from these available options**: {agent_options}. "
                "No other options are allowed.\n"
                "- Provide specific instructions for the selected agent to guide their work on this task."
            ),
        ])

        current_prompt = prompt.partial(agent_options=available_options)
        supervisor = current_prompt | model.with_structured_output(SupervisorOutput)

        response = supervisor.invoke(state)
        state["supervisor_instructions"].append(response.agent_instructions)

        return response
    except Exception as err:
        raise ValueError(f"Error caught in InputArgumentAnalyserAgent: {str(err)}")