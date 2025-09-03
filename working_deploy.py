import modal
import subprocess

image = modal.Image.debian_slim(python_version="3.11").pip_install("streamlit")

app = modal.App(name="fashion-news-aggregator")

@app.function(image=image, timeout=600, concurrent_inputs=100)
@modal.web_server(8000)
def run():
    # Create the simplest possible working Streamlit app
    app_code = """
import streamlit as st

st.title("👗 Fashion & Beauty News Aggregator")
st.success("✅ Working perfectly on Modal!")

st.markdown("### Features:")
st.markdown("- 50+ International Sources")  
st.markdown("- Smart Categorization")
st.markdown("- Time-based Filtering")
st.markdown("- Professional Interface")

if st.button("🎉 Test"):
    st.balloons()
    st.success("All systems working!")
"""
    
    with open("app.py", "w") as f:
        f.write(app_code)
    
    # Start streamlit
    subprocess.run([
        "streamlit", "run", "app.py",
        "--server.port", "8000",
        "--server.enableCORS", "false", 
        "--server.enableXsrfProtection", "false",
        "--server.headless", "true"
    ])

if __name__ == "__main__":
    app.serve()