import streamlit as st
import json
from summary import summarize_incident_transcript

# Function to get the prompt text used for summarization
def get_summarization_prompt():
    """Return the prompt text used for incident transcript summarization."""
    return """Summarize the current incident call meeting transcript into a structured JSON outlining the step-by-step progression of the discussion. For each step/discussion point, briefly explain what was discussed or solved. Conclude the summary with a clear description of the current topic being discussed on the call (i.e., what participants are focused on right now). Ensure that the output captures the sequence of events and transitions on the call.

Guidelines:
- Carefully read through the provided meeting transcript.
- Identify and list stepwise discussions or actions. Each should capture what was discussed, attempted, or resolved up to that point.
- For each step, write a concise summary (2-3 sentences) explaining what was addressed or achieved.
- At the end, summarize in 2-3 sentences what is currently being discussed on the call.
- Persist through the whole transcript, updating your understanding as the incident unfolds.
- Think step-by-step to ensure that you do not miss any key discussion or resolution transitions.

Output format:
- Use JSON with two keys:
  - "steps": a list where each item is an object with:
     - "discussion_step": a short title for the point or action.
     - "description": 2-3 sentences summarizing that step.
  - "currently_discussed": a short paragraph (2-3 sentences) describing the current focus of the meeting.

Example Input:  
Transcript:  
We noticed the database latency at 09:12 UTC. Restarted replica instances, no improvement yet.  Let's check recent code deploy logs for errors.  Recent deploy at 09:05 UTC, rollback initiated. Latency improving slightly now. Monitor metrics another 10 minutes to confirm resolution.

Example Output:  
{
  "steps": [
    {
      "discussion_step": "Initial Issue Detection",
      "description": "The team identified rising database latency at 09:12 UTC."
    },
    {
      "discussion_step": "Replica Restart Attempt",
      "description": "Bob restarted the database replica instances, but the latency persisted."
    },
    {
      "discussion_step": "Review of Deploy Logs",
      "description": "Charlie suggested checking deploy logs for errors, noting a recent code deployment."
    },
    {
      "discussion_step": "Rollback Deploy",
      "description": "Bob initiated a rollback of the recent code deployment at 09:05 UTC, after which slight latency improvement was reported."
    }
  ],
  "current_discussion": "The team is currently monitoring database metrics for another ten minutes to confirm whether the rollback fully resolves the latency issues."
}

(Ensure 'current_discussion' always reflects the present focus if the call is ongoing.)

Important: Only output the JSON as specified
**Objective:** Output a stepwise JSON summary capturing main discussion points, resolution steps, and current meeting focus from a live incident call transcript."""

# Set page config
st.set_page_config(
    page_title="Incident Transcript Summarizer",
    page_icon="🔍",
    layout="wide"
)

# Title and description
st.title("🔍 Incident Transcript Summarizer")
st.markdown("Paste your incident call transcript below and get a structured step-by-step summary.")

# Create tabs
tab1, tab2 = st.tabs(["Example", "Try with your own transcript"])

with tab1:
    # Create two columns for better layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Example Transcript")
        
        # Example transcript
        example_transcript = """Hey, this is John joining the call. Anyone else join the call yet? Hi, this is Matty joining as Incident Commander. Hey, this is Rachel joining as Deputy. I'll scribe for now while also providing backup. Hi, this is Dilashni. Let me know if you need SRE. Hey, this is JC. I'm here for event management. Hi, this is George. I'm here for the mobile team. Okay, John, what's going on? I'm not sure what's going on, but DB2 Kafka is down. The service wasn't responding, so they're restarting it, but that didn't help. There was a deploy earlier today that might have had an impact, so I rolled that back, but it still hasn't helped. It's been pretty unresponsive, so I manually triggered the incident call. It sounds like we're going to need the notification pipeline team to take a closer look. We should get them on the call. It looks like Julie is the person on call right now. Okay. Hey, Rachel, can you page Julie to join the call? I'm on it. Thanks, Rachel. John, tell us more about what you're seeing. I'm looking at the logs for DB2 Kafka, and I see a few different errors. There's not one specific error. It just looks like a bunch of stuff is failing. I thought it might be the service itself, but the host running those continues to fail. There's something weird that's going on with Mesos. HNO3 is logging way more than any of the other instances by an order of magnitude. Got it. Are we seeing any other impacts on the customer side? I'm looking at our app performance dashboards, and I'm seeing a blip for users of our Android app. It looks like there's a steady increase in apps that's crashing. I'm going to dig into this a little bit more. Hey, this is Scott joining as customer liaison.  Hi, this is Julie joining the call for the pipeline team. Hi, Julie. We're seeing problems with DB2 Kafka, and JDC suggested we bring you into the call. Something weird's going on with Mesos because Agent 03 is logging way more than anything else in that cluster. This started when John noticed the DB2 Kafka service was unresponsive. After a failed restart, John rolled back changes deployed to DB2 Kafka from earlier today. Restarts aren't helping, and now we're also seeing a steady increase in app crashes for Android users. George is looking into what's going on. Okay, looking into this a little bit more, it looks like the crashes might be related to triggering incident log entries. Incident log entries are a core part of functionality when you get an alert. That's a significant impact on customers. We should escalate this to SEV1. Rachel, can you make this incident a SEV1? Yep, got it. The incident is now a SEV1. If DB2 Kafka is down, then the log entry service is going to run into problems. Anything querying that service is going to bomb out. When that happens, no incident log entries are going to be generated. Let me check something. It looks like the notifications are still going out, but some of them are messed up. I'm looking at a notification with a subject line in it that appears to have the right data. But the body in the notification is blank. That would make sense because the notifications use incident log entries to populate the data. Hi, this is Mandy. I've joined the call and can take over Ascribe. Hey, Mandy. Yep, please take over Ascribe. I think there's maybe a bigger issue going on here than just the Agent 03 host. The entire Mesos cluster might be having a problem, but I'm not sure what's going on. I think we need to find someone who knows what's going on with Mesos. Let me try and get some more details on what's happening. Okay, John. While you do that, Rachel, can you figure out who we can reach for help with Mesos? And let me know how that goes within the next five minutes. Yep, I'll go look now. Thanks. How's it going, John? I'm pulling up the chat. Thanks, John. Do we know what the customer impact is so far? Yes, right now what this means is that no one has been able to reach our customer. So we're going to have to figure out who we can reach. Okay, great. So we're going to have to figure out who we can reach. Thanks, John. Do we know what the customer impact is so far? Yes, right now what this means is that no instant log entries can be created. That also means that when you get an incident notification, there are no incident details. If you try to access those incident details via the web UI, you also get an error. Loading incidents on the website shows a message that says an internal error has occurred. PagerDuty administrators have been notified. Scott, did you get that? Yes, I did. I got that. Good. Scott, please compose an update informing our customers that we've detected this issue and we're actively investigating. And when you have that draft ready, please post it to the Slack channel. Okay, I'm doing that now. I posted a suggested message into the Slack channel. Thanks, Scott. Everyone, please take a minute to review the suggested customer update message in the Slack channel. Are there any strong objections to posting that update message? Hearing none, Scott, please go ahead and post that message to the Slack channel. Hearing none, Scott, please go ahead and post that message to our status page and to Twitter. Understood. I'm posting those updates now. How's it going, John? Were you able to find out anything new? I'm looking at the logs and dashboards now. I'm seeing some weird failures, but I don't know what's going on yet. Hey, Rachel, it's been five minutes. Were you able to reach someone to help out with Mesos? Okay, I added Joel as a responder to this incident, but no reply yet. It looks like none of the notification methods he has were able to reach him. I'm going to try manually now via Slack to see if we can get him to respond. We could try Alex. Noted. I can try Alex next if there's no response from Joel. Yeah, JC says Alex might be working from India this week. I just saw that. It's pretty early in the morning in India right now, so that could really go either way. He may or may not respond. I'm going to add Alex as a responder to this incident just in case. We'll give them both a few minutes to respond. Neither of them is on call. Hey, John, is there a runbook for Mesos? There is a runbook for Mesos, but not for this. Can you post links to the runbooks? There you go. There's nothing there specifically for the errors we're seeing with the cluster. From what I can see, it also looks like logging is starting to increase. If it's Mesos, that's the problem. Would it be possible to just stop Marathon entirely and restart everything? That's possible. I'm not really sure what that's going to do. Looking at the runbook, there are instructions on the runbook. I'm not really sure what that's going to do. What's the risk in trying to restart Mesos right now? Without a clear runbook, we could get it wrong. It might also not make a difference, since I still don't entirely know what's happening yet. Are there any strong objections to trying a restart of Mesos? I don't think so. Are there any strong objections to trying a restart of Mesos? I don't think so. Are there any strong objections to trying a restart of Mesos? Yes, this is Dileshni. I have a strong objection. I think that's a little premature to restart Mesos. If there's a deep underlying issue with Marathon, we might be making things a lot worse. I think we should wait to see what Joel has to say. Okay, we'll hold off on attempting a restart of Mesos at this time. Okay, Joel has responded on Slack and does not have a laptop. He should be joining the bridge shortly. It looks like Agent 03 is now unreachable. Hi, this is Joel joining the call as requested. And now Agent 02 is also unreachable. We might need to kick some new hardware if those hosts are actually hosed. What's going on? Hey, Joel. We're having problems with DB2 Kafka. Those problems are creating a partial outage where we're seeing notifications go through without message bodies. Sounds like customers probably don't see the error until they click through for instant details. We're not sure how wide the impact is yet, but it's causing some mobile Android apps to crash, and we know it also appears in the web UI. The reason you're here is we think this might be related to problems we're seeing in the Mesos cluster that the service is on. Agent 03 has been problematic for a while, and now we can't reach it anymore. Agent 02 might also be offline now. I just verified that Agent 01 is still reachable. At least that one is up. And I just verified that Agent 02 is unreachable. Agent 03 is also unreachable. There are only three agents for that Mesos cluster. I'm seeing some log entries about memory exhaustion on Agent 01. I'm digging in a little more to see what's going on. So if two of those agents are down, that means we're down to one host left in the cluster. Is anything else still running in that cluster? The Marathon console shows that DB2 Kafka is repeatedly flapping up and down. So that doesn't appear to be running. It does look like there are three other apps still running, though. I can reach Agent 02 again, but it's just running really, really slow. We have another Mesos cluster available in another region if we need to take some more agents and migrate. Based on what I'm seeing right now, trying to restart Mesos might actually be the right thing to do at this point. So I take back my earlier objection. Okay. Sounds like we have two options right now. We can either kick more agents in another region and migrate, or we can try restarting Mesos. Joel, what do you suggest? I think that rather than restarting Marathon entirely, we can try restarting just the agent nodes first. It's probably the most efficient way to do it. So let's start with Agent 03, since there probably hasn't been anything running on that one for a while. And we can't get to it anyway. Okay. Are there any strong objections to restarting the Mesos agent nodes? Okay. Hearing none, Daleshni, please go ahead and restart Agent 03. How long do you need for that? Restarting is not a problem. Daleshni, please go ahead and restart Agent 03. How long do you need for that? Restarting is going to take a couple of minutes. Okay. I will check back in with you in two minutes. Got it. Restarting Agent 03. Agent 03 is still restarting. But while that's happening, I was looking at the other hosts. I just noticed that Linux Out of Memory Killer kicked on Agent 01. This is what I'm seeing. There's more than a few of these log entries, and it looks like they've been happening for a while. Thanks for the update, Daleshni. How's the restart going? Still need another minute or so. And how concerned should we be about these Out of Memory Killer errors? I'm not sure yet. Still investigating. I see high disk read operations from the Agent 03 instance, so it should be coming back up now, which is good timing because Agent 02 is now definitely unreachable, and the host instance is now failing health checks. Looks like that instance might be toast now as well. If Agent 02 is offline anyway, should we maybe try restarting that one too? We're going to eventually need it back. Why not get it rebooted now? Should be fine. Yeah, I agree. That should be fine. Any strong objections? Okay, Daleshni. Also reboot Agent 02 when you get a chance. Okay, Daleshni. Also reboot Agent 02 when you get a chance. Understood. What do we do if the reboot doesn't fix anything? It looks like maybe we're about to lose this entire cluster. We should be ready to kick another cluster in the same region, rather than migrating across regions. It's a little more work, but it should take less time. If Mesos comes back after those reboots, then we'll want to try starting up the db2kafka containers to see why they failed in the first place. Okay, Agent 03 is back up and responding. I just checked, and Mesos is back up and running on Agent 03. Agent 02 is still rebooting, and it should be ready in about a minute or so. Great. We should try starting up the containers manually. Are there any strong objections to starting up the containers manually? Okay, Daleshni. Go ahead and start the containers manually, please. Got it. Starting the containers on Agent 03. This is running really slow. What's the memory usage on Agent 03? Looks like it's at 100%. The Marathon console doesn't have good news for us either. Mesos is still very not happy. I don't know what's going on yet. Something still looks very wrong with these hosts. It looks like the containers are trying to start, but they're exiting with code 137. What does exit code 137 mean? I don't know. I'm looking for it. Exit code 137 means it was killed by out of memory. Looks like the OOM killer is continuously terminating the Docker containers. Yep, confirmed. I'm seeing a bunch of those same OOM log lines on Agent 03 that I was seeing on Agent 01. What's the memory limit set to in the Marathon config? 130 megs. I recommend that we set that to at least double and see if that gets around the out of memory issue. Are there any risks in doubling the memory allocation? I don't think so. It should be fine from the system's perspective. These instances have enough memory, but we should set that config in Chef and let Chef push out the change. In the meantime, I recommend we do this manually right now to test it and see if we can get everything working again. Joel, how's that sound to you? Agreed. Change the setting and try starting those containers manually again. If that works, then we can put it in Chef. That sounds like the best plan. Are there any strong objections to manually adjusting this config for now? Okay, Dileshni, go ahead with the changes. We'll put them in Chef after we resolve the incident if everything works."""
        
        # Display example transcript in a text area (read-only)
        st.text_area(
            "Example Incident Call Transcript:",
            value=example_transcript,
            height=200,
            disabled=True
        )
        
        # Example JSON data
        example_result = {
            'steps': [
                {
                    'discussion_step': 'Team Introductions',
                    'description': 'Participants joined the call, including John, Matty as the Incident Commander, Rachel as Deputy, and others. John mentioned that DB2 Kafka is down and needs immediate attention.'
                },
                {
                    'discussion_step': 'Initial Incident Report',
                    'description': 'John reported that DB2 Kafka is unresponsive and described attempts to restart the service, which were unsuccessful. A rollback of previous deployments was also initiated without improvement.'
                },
                {
                    'discussion_step': 'Involvement of Notification Pipeline Team',
                    'description': 'It was suggested that the notification pipeline team, specifically Julie, needs to join the call to address concerns related to notification issues stemming from the DB2 Kafka outage.'
                },
                {
                    'discussion_step': 'Error Log Analysis',
                    'description': 'John presented errors in the DB2 Kafka logs, noting how certain instances of Mesos, particularly Agent 03, were logging significantly more errors than others. The situation appeared to be worsening with potential impacts on customer apps.'
                },
                {
                    'discussion_step': 'Escalation to SEV1',
                    'description': 'Due to the severity of the issues with notification services, it was agreed to escalate the incident to SEV1. Rachel confirmed that the incident status has been updated.'
                },
                {
                    'discussion_step': 'Customer Impact Assessment',
                    'description': 'The team assessed the impact on customers, noting that no incident log entries were being created, which affected customer notifications and the ability to access incident details through the web UI.'
                },
                {
                    'discussion_step': 'Communication with Customers',
                    'description': 'Scott was tasked with drafting a customer update regarding the ongoing issue, ensuring that the communications are posted to the Slack channel, status page, and Twitter.'
                },
                {
                    'discussion_step': 'Attempt to Engage Mesos Experts',
                    'description': 'Rachel was tasked with reaching out to experts on Mesos as it appeared to be a broader issue affecting the overall cluster. Both Joel and Alex were added as responders.'
                },
                {
                    'discussion_step': 'Mesos Cluster Analysis',
                    'description': 'Joel joined the call and confirmed issues with multiple Mesos agents going offline and the implications on the overall functioning of DB2 Kafka. The team considered rebooting Agent 03.'
                },
                {
                    'discussion_step': 'Decision to Restart Agents',
                    'description': 'The consensus shifted towards restarting Agent 03 first, and later Agent 02, as many services were flapping. The potential need for additional hardware was acknowledged.'
                },
                {
                    'discussion_step': 'Monitoring Restart Process',
                    'description': 'Daleshni commenced the restart of Agent 03, while the team monitored the situation. Agent 03 came back online while Agent 02 continued to experience issues.'
                },
                {
                    'discussion_step': 'Container Start Attempts',
                    'description': 'As Agent 03 went back online, the team attempted to start the containers manually but faced issues. Exit code 137 was identified, indicating an out-of-memory condition.'
                },
                {
                    'discussion_step': 'Memory Configuration Discussion',
                    'description': "The team discussed increasing the memory limit in Marathon's config to alleviate the out-of-memory issues. It was agreed to implement the changes manually first before committing them to Chef."
                }
            ],
            'currently_discussed': 'The team is currently focusing on adjusting the memory allocation for the containers in Marathon and testing whether this change helps resolve the ongoing service issues with DB2 Kafka, while also monitoring the status of Agent 02.'
        }
        
        # Show raw JSON in expandable section
        with st.expander("🔍 View Raw JSON Output"):
            st.json(example_result)
        
        # Show prompt in expandable section
        with st.expander("📋 View Summarization Prompt",expanded=True):
            st.text(get_summarization_prompt())
    
    with col2:
        st.subheader("📊 Example Summary Output")
        
        for i, step in enumerate(example_result.get('steps', []), 1):
            with st.expander(f"{step.get('discussion_step', 'Unknown Step')}", expanded=True):
                st.write(step.get('description', 'No description available'))
        
        # Display current discussion
        if 'currently_discussed' in example_result:
            st.markdown("### 🎯 Current Discussion")
            st.info(example_result['currently_discussed'])
        


with tab2:
    # API Key input
    st.subheader("🔑 API Configuration")
    api_key = st.text_input(
        "Enter your OpenAI API Key:",
        type="password",
        placeholder="sk-...",
        help="Your API key is used only for this session and is not stored."
    )

    st.markdown("---")

    # Create two columns for better layout
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📝 Input Transcript")
        
        # Text area for transcript input
        transcript = st.text_area(
            "Paste your incident call transcript here:",
            height=400,
            placeholder="Paste your incident call transcript here..."
        )
        
        # Submit button
        if st.button("🚀 Generate Summary", type="primary"):
            if not api_key.strip():
                st.error("Please enter your OpenAI API key first.")
            elif transcript.strip():
                with st.spinner("Analyzing transcript..."):
                    try:
                        # Call the summarization function with API key
                        result = summarize_incident_transcript(transcript, api_key)
                        
                        # Store result in session state
                        st.session_state.summary_result = result
                        
                    except Exception as e:
                        st.error(f"Error processing transcript: {str(e)}")
            else:
                st.warning("Please paste a transcript before submitting.")

    with col2:
        st.subheader("📊 Summary Output")
        
        # Display results if available
        if hasattr(st.session_state, 'summary_result') and st.session_state.summary_result:
            result = st.session_state.summary_result
            
            # Display the steps
            st.markdown("### 📋 Discussion Steps")
            
            for i, step in enumerate(result.get('steps', []), 1):
                with st.expander(f"Step {i}: {step.get('discussion_step', 'Unknown Step')}", expanded=True):
                    st.write(step.get('description', 'No description available'))
            
            # Display current discussion
            if 'currently_discussed' in result:
                st.markdown("### 🎯 Current Discussion")
                st.info(result['currently_discussed'])
            
            # Show raw JSON in expandable section
            with st.expander("🔍 View Raw JSON Output"):
                st.json(result)
            
            # Show prompt in expandable section
            with st.expander("📋 View Summarization Prompt"):
                st.text(get_summarization_prompt())
                
        else:
            st.info("👆 Enter your API key, paste a transcript, and click 'Generate Summary' to see the analysis results here.")

# Add footer
st.markdown("---")
