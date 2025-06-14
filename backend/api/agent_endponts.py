import operator
import time

from agents.argument_analyser import ArgumentAnalyzer
from agents.movie_recommender import MovieRecommender
from agents.supervisor_agent import Supervisor
from fastapi import FastAPI, status, Body
from langchain_core.messages import HumanMessage, BaseMessage
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel
from typing import TypedDict, Literal, Optional, Annotated, Sequence

app = FastAPI(
    title="Movie GPT",
)


class DataInput(BaseModel):
    prompt: str
    chat_history: Optional[list]


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    chat_history: list
    next: str
    supervisor_instructions: Annotated[Sequence[str], operator.add]
    agent_call_list: Annotated[Sequence[str], operator.add]
    final_response: str
    usage: list


class MovieRecommendationResponse(BaseModel):
    agent_output: str


@app.get("/")
async def read_root():
    return {"message": "Music GPT"}


@app.get("/ping", status_code=status.HTTP_200_OK)
def ping():
    now = time.time()
    ping = {"api": "MusicGPT", "time-stamp": now}
    return ping


@app.post("/recommend-movie")
async def recommend_movie(
        data: DataInput = Body(...)
):
    try:
        print("Flag-1")
        prompt = data.prompt
        chat_history = data.chat_history

        supervisor_agent = Supervisor()
        argument_analyser_agent = ArgumentAnalyzer()
        movie_recommendation_agent = MovieRecommender()

        print("Flag-2")
        graph = StateGraph(AgentState)
        graph.add_node("Supervisor", supervisor_agent.perform_task)
        graph.add_node("Argument Analyzer Agent", argument_analyser_agent.perform_task)
        graph.add_node("Movie Recommender", movie_recommendation_agent.perform_task)

        conditional_map = {
            "Input Argument Analyzer Agent": "Argument Analyzer Agent",
            "Movie Recommendation Agent": "Movie Recommender",
            "FINISH": END
        }

        print("Flag-3")
        graph.add_edge(START, "Supervisor")
        graph.add_conditional_edges("Supervisor", lambda x: x["next"], conditional_map)

        print("Flag-4")
        # Compile the graph
        app_graph = graph.compile()

        # Initialize state
        initial_state = AgentState(
            messages=[HumanMessage(content=prompt)],
            chat_history=[],
            next="",
            supervisor_instructions="",
            agent_call_list=[],
            final_response="",
            usage=[]
        )

        print("Executing the graph")
        # Execute the graph
        result = app_graph.invoke(initial_state)

        # Return the response
        return MovieRecommendationResponse(
            agent_output=result.get("output_for_user", "No output from the agent."),
        )

    except Exception as err:
        raise err
