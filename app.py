import openai
import os
import streamlit as st # Import the Streamlit library

# --- OpenAI API Key Setup ---
# Get API key from environment variable (recommended for security)
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Check if API key is set. In a Streamlit app, we show an error message
# directly on the page if it's missing.
if openai.api_key is None:
    st.error("Error: OPENAI_API_KEY environment variable not set.")
    st.warning("Please set it before running the app. You can do this in your terminal:")
    st.code("export OPENAI_API_KEY='your_api_key_here' # macOS/Linux")
    st.code("set OPENAI_API_KEY=your_api_key_here # Windows")
    st.stop() # Stop the Streamlit app from running further if key is missing

# --- Streamlit UI ---
st.set_page_config(page_title="TL;DR", page_icon="📝")
st.title("📝 TL;DR")
st.markdown("Summarize group chats and email threads into clear decisions, unresolved topics, and action items.")
st.markdown("A Ray L. Product")

# Input for the chat/email thread
user_pasted_text = st.text_area(
    "**Paste your group chat or email thread here:**",
    height=300,
    placeholder="Example:\nAlice: Hey team, how's the website redesign?\nBob: I've got a draft, but stuck on the hero image. Product photo or abstract art?\nCarol: Product photo, definitely.\nAlice: Okay, Decision: Product photo. Bob, implement by EOD tomorrow.\nCarol: Also, pricing page: individual feature or tiered plans?\nAlice: Let's defer pricing for now. Action: Alice to research competitor pricing by Friday."
)

# Optional input for key people (for better AI context)
key_people_involved = st.text_input(
    "**Optional: Key People Involved (comma-separated names, e.g., Alice, Bob, Carol):**",
    placeholder="e.g., John, Sarah, Emily"
)

# Button to trigger the summarization
if st.button("Generate TL;DR"):
    if not user_pasted_text.strip():
        st.warning("Please paste some text to summarize.")
    else:
        # Show a spinner while processing
        with st.spinner("Analyzing conversation... This might take a moment."):
            try:
                # Construct the prompt using the system and user roles
                # We'll embed the key_people_involved directly into the system prompt for now
                prompt_messages = [
                    {"role": "system", "content": f"""You are an expert meeting facilitator and summarizer. Your task is to analyze the provided group chat or email thread and extract key information.

Key People Involved (for identifying ownership, if provided): {key_people_involved if key_people_involved else "N/A"}

Instructions:
1.  **Summarize the core topic(s)** discussed in 2-4 sentences. Focus on the main points and progression of the conversation.
2.  **Identify all clear decisions or agreements made.** For each decision, state what was decided and who is responsible (if mentioned). If a decision implies a concrete action, list it under "Action Items" instead.
3.  **List all topics or questions that are still unresolved/undecided.** These are items that were discussed but no final conclusion was reached.
4.  **Identify clear action items**, specifying the task and the person responsible (if mentioned), and any deadlines. If no specific person is mentioned, note it as "Team/Unassigned".
5.  Maintain a professional, objective, and concise tone throughout the summary.
6.  Output the information in the following structured Markdown format:

## Chat Summary:
[Concise, 2-4 sentence overview of the main points and progression of the conversation.]

## Key Decisions Made:
- [Decision 1. Responsible: [Person/Team]]
- [Decision 2. Responsible: [Person/Team]]
... (If no clear decisions, state "No clear decisions made.")

## Unresolved Topics / Open Questions:
- [Unresolved Topic/Question 1]
- [Unresolved Topic/Question 2]
... (If all major topics appear resolved, state "All major topics appear resolved.")

## Action Items (Whose Table It Is On):
- [ACTION]: [Responsible Person/Team] (Due: [Date/Time if specified])
- [ACTION]: [Responsible Person/Team] (Due: [Date/Time if specified])
... (If no explicit action items, state "No explicit action items identified.")
"""},
                    {"role": "user", "content": f"Here is the group chat/email thread to summarize:\n```\n{user_pasted_text}\n```"},
                ]

                response = openai.chat.completions.create(
                    model="gpt-4o", # Using the latest powerful model
                    messages=prompt_messages,
                    max_tokens=1000, # Increased tokens for longer summaries
                    temperature=0.3 # Lower temperature for focused output
                )

                # Display the LLM's response
                summary = response.choices[0].message.content
                st.subheader("🎉 Your Decision Digest:")
                st.markdown(summary) # Use st.markdown to render the Markdown output beautifully

            except openai.APIConnectionError as e:
                st.error(f"Could not connect to OpenAI API: {e}. Please check your internet connection.")
            except openai.RateLimitError as e:
                st.error(f"OpenAI API rate limit exceeded: {e}. You might need to upgrade your OpenAI plan or check your billing on platform.openai.com.")
            except openai.APIStatusError as e:
                st.error(f"OpenAI API returned an error: Status Code {e.status_code} - Response: {e.response.text}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")