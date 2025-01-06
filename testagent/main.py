import uvicorn
from fastapi import FastAPI, HTTPException, Request
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, MessagesState, StateGraph
from pydantic import BaseModel

# Define the LLM
llm = ChatOpenAI(model="gpt-4o-mini")

# Define the prompt
prompt = ChatPromptTemplate.from_messages(
    [("system", "You are a helpful AI assistant."), ("user", "{input}")]
)


# Define the node
def agent_node(state):
    messages = state.get("messages", [])
    prompt_value = prompt.format_messages(input=messages[-1].content)
    response = llm.invoke(prompt_value)
    return {"messages": messages + [response]}


# Create the graph
builder = StateGraph(MessagesState)
builder.add_node("agent", agent_node)
builder.set_entry_point("agent")
builder.add_edge("agent", END)
graph = builder.compile()

# FastAPI setup
app = FastAPI()


class MessageInput(BaseModel):
    message: str


@app.get("/headers")
async def get_headers(request: Request):
    """
    届いたリクエストのヘッダー情報を表示するエンドポイント
    """
    headers = dict(request.headers)
    return {"headers": headers}


@app.post("/chat/")
async def chat_endpoint(input_data: MessageInput):
    try:
        inputs = {"messages": [HumanMessage(content=input_data.message)]}
        result = graph.invoke(inputs)

        # Extract only the content of the messages
        response_messages = [message.content for message in result["messages"]]
        return {"response": response_messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
