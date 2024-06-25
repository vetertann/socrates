import streamlit as st
from openai import OpenAI
import os
import time

def log_to_stdout(message):
    os.write(1, f"{message}\n".encode())
    
def get_response(client, prompt, role, instructions):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": instructions[role]},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def run_conversation(api_key, task, max_iterations):
    client = OpenAI(api_key=api_key)
    
    instructions = {
        "A": "You are Assistant A. Please provide an answer to the task using all your knowledge and the current context/discussion",
        "B": "You are Assistant B. You are Bayesian statistician and real world expert. You are thoughtful out-of-the box analyst. Critically analyze the given context/discussion, try to be devil's advocate and attack Assistant A's answer. Analyse the task details for additional info, that can contradict the solution. Focus not only on the solution of Assistant A, but if this solution even makes sense with task description. Imagine situations when the solution is invalid and attack with this. Remember, even if task implies something, you should try find situations where it is not true",
        "C": "You are a judge evaluating the context. If you think that Assistants A and B are actually close to consensus, say 'answer is ready'. Otherwise, say 'zero'."
    }

    context = task
    dialog_history = context
    count = 0
    
    progress_bar = st.progress(0)
    status_text = st.empty()

    while count < max_iterations:
        status_text.text(f"Iteration {count + 1}/{max_iterations}")
        
        answer_A = get_response(client, context, "A", instructions)
        dialog_history += f"\nAssistant A: {answer_A}"
        
        context = f"{task}\nAssistant A: {answer_A}"
        answer_B = get_response(client, context, "B", instructions)
        dialog_history += f"\nAssistant B: {answer_B}"
        
        context = f"{task}\nAssistant A: {answer_A}\nAssistant B: {answer_B}"
        evaluation_C = get_response(client, context, "C", instructions)
        
        count += 1
        progress_bar.progress(count / max_iterations)
        
        if "answer is ready" in evaluation_C.lower():
            break
        
        time.sleep(0.1)  # To prevent rate limiting

    summary_prompt = f"{dialog_history}\nSummarize the final answer, without mentioning Assistants in your summary - just the consensus, the result."
    summary = get_response(client, summary_prompt, "A", instructions)
    log_to_stdout(f"Task: {task}")
    log_to_stdout(f"Summary: {summary}")
    
    return dialog_history, summary

st.title("Multi-Agent Discussion app implementation playground")

api_key = st.text_input("Enter your OpenAI API Key", type="password")
task = st.text_area("Enter the task", height=100)
max_iterations = st.number_input("Enter the maximum number of iterations", min_value=1, max_value=20, value=10)

if st.button("Run Conversation"):
    if not api_key or not task:
        st.error("Please enter both the API key and the task.")
    else:
        with st.spinner("Running conversation..."):
            dialog_history, summary = run_conversation(api_key, "Task:" + task, max_iterations)
        
        st.subheader("Summary")
        st.write(summary)
        
        st.subheader("Full Dialog History")
        with st.expander("Click to expand"):
            st.text(dialog_history)

st.markdown("---")
st.markdown("by [Ivan Matveev](https://www.linkedin.com/in/ivan-matveev-a9388720/)")
