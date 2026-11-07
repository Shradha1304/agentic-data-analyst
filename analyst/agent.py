import json
import os
import time
from dotenv import load_dotenv
from openai import OpenAI,RateLimitError

from analyst.tool_specs import TOOL_SPECS,run_tool,to_openai_format

load_dotenv()
MAX_STEPS=12

SYSTEM_PROMPT = f"""You are a careful data analyst. You are given tools that analyze a dataset.
Explore the dataset to find the most interesting patterns and data quality issues.
Start with get_schema. You have a budget of {MAX_STEPS} tool-calling rounds, so prioritize.
Never invent numbers: only state values that appear in tool results.
When you have gathered enough, reply with a short plain-text summary and make no more tool calls."""


client=OpenAI(
    api_key=os.environ['LLM_API_KEY'],
    base_url=os.environ['LLM_BASE_URL']
)

MODEL=os.environ['LLM_MODEL']


def call_llm(messages: list):
    for attempt in range(4):
        try:
            return client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=to_openai_format(TOOL_SPECS),
                max_tokens=2000,
            )
        except RateLimitError:
            wait =5*(attempt+1)
            print(f"rate limited waiting for {wait} s")
            time.sleep(wait)
    raise RuntimeError("Still rate limited after 4 tries")



def run_agent(df, task : str ="Explore the dataset and find the most interesting patterns"):
    messages=[
        {"role":"system","content":SYSTEM_PROMPT},
        {"role":"user","content":task}
    ]

    tool_log=[]
    cache={}

    for step in range(1,MAX_STEPS+1):
        response=call_llm(messages)
        msg=response.choices[0].message

        if not msg.tool_calls:
            print(f"{step} done")
            return {"summary":msg.content,"messages":messages,"tool_log":tool_log}

        messages.append({
            "role": "assistant",
            "content": msg.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in msg.tool_calls
            ],
        })

        for tc in msg.tool_calls:
            name=tc.function.name
            try:
                args=json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args=None

            if args is None:
                result={"error": "arguments were not valid json, retry with json object"}
            else:
                key=name+json.dumps(args,sort_keys=True)
                if key in cache:
                    result={"note":"Duplicated call, returning cache result",**cache[key]}
                else:
                    result=run_tool(df,name,args)
                    cache[key]=result

            print(f"[step {step}] {name}({args}) -> {str(result)[:150]}")
            tool_log.append({"step":step,"tool":name,"args":args,"result":result})
            messages.append({
                "role":"tool",
                "tool_call_id":tc.id,
                "content":json.dumps(result),
                })
    print("\nStep limit reached.")
        # Step limit reached: force a final answer with tools disabled
    print("\nStep limit reached. Requesting final summary.")
    messages.append({
        "role": "user",
        "content": "Tool budget is used up. Write your final summary now, using only the tool results above.",
    })
    final = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=2000,
    )
    return {"summary": final.choices[0].message.content, "messages": messages, "tool_log": tool_log}