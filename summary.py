import os
from openai import OpenAI
import json

def summarize_incident_transcript(transcript, api_key=None):
    """
    Summarize an incident call meeting transcript into structured JSON.
    
    Args:
        transcript (str): The meeting transcript to summarize
        api_key (str, optional): OpenAI API key. If not provided, uses environment variable.
        
    Returns:
        The OpenAI response containing the structured summary
    """
    # Use provided API key or fall back to environment variable
    if api_key:
        client = OpenAI(api_key=api_key)
    else:
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    
    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": "Summarize the current incident call meeting transcript into a structured JSON outlining the step-by-step progression of the discussion. For each step/discussion point, briefly explain what was discussed or solved. Conclude the summary with a clear description of the current topic being discussed on the call (i.e., what participants are focused on right now). Ensure that the output captures the sequence of events and transitions on the call.\n\nGuidelines:\n- Carefully read through the provided meeting transcript.\n- Identify and list stepwise discussions or actions. Each should capture what was discussed, attempted, or resolved up to that point.\n- For each step, write a concise summary (2-3 sentences) explaining what was addressed or achieved.\n- At the end, summarize in 2-3 sentences what is currently being discussed on the call.\n- Persist through the whole transcript, updating your understanding as the incident unfolds.\n- Think step-by-step to ensure that you do not miss any key discussion or resolution transitions.\n\nOutput format:\n- Use JSON with two keys:\n  - \"steps\": a list where each item is an object with:\n     - \"discussion_step\": a short title for the point or action.\n     - \"description\": 2-3 sentences summarizing that step.\n  - \"currently_discussed\": a short paragraph (2-3 sentences) describing the current focus of the meeting.\n\nExample Input:  \nTranscript:  \nWe noticed the database latency at 09:12 UTC. Restarted replica instances, no improvement yet.  Let's check recent code deploy logs for errors.  Recent deploy at 09:05 UTC, rollback initiated. Latency improving slightly now. Monitor metrics another 10 minutes to confirm resolution.\n\nExample Output:  \n{\n  \"steps\": [\n    {\n      \"discussion_step\": \"Initial Issue Detection\",\n      \"description\": \"The team identified rising database latency at 09:12 UTC.\"\n    },\n    {\n      \"discussion_step\": \"Replica Restart Attempt\",\n      \"description\": \"Bob restarted the database replica instances, but the latency persisted.\"\n    },\n    {\n      \"discussion_step\": \"Review of Deploy Logs\",\n      \"description\": \"Charlie suggested checking deploy logs for errors, noting a recent code deployment.\"\n    },\n    {\n      \"discussion_step\": \"Rollback Deploy\",\n      \"description\": \"Bob initiated a rollback of the recent code deployment at 09:05 UTC, after which slight latency improvement was reported.\"\n    }\n  ],\n  \"current_discussion\": \"The team is currently monitoring database metrics for another ten minutes to confirm whether the rollback fully resolves the latency issues.\"\n}\n\n(Ensure 'current_discussion' always reflects the present focus if the call is ongoing.)\n\nImportant: Only output the JSON as specified\n**Objective:** Output a stepwise JSON summary capturing main discussion points, resolution steps, and current meeting focus from a live incident call transcript."
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": transcript
                    }
                ]
            },
        ],
        text={
            "format": {
                "type": "json_object"
            }
        },
        reasoning={},
        tools=[],
        temperature=1,
        max_output_tokens=2048,
        top_p=1,
        store=True
    )
    json_response = json.loads(response.output[0].content[0].text)
    
    return json_response