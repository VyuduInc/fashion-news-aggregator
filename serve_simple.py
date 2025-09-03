import modal
import subprocess
import shlex

# Simple, reliable image
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "streamlit==1.49.1"
)

app = modal.App(name="fashion-aggregator-simple", image=image)

@app.function(
    timeout=300,
    memory=512,
    concurrent_inputs=100
)
@modal.web_server(8000)
def run():
    # Create a simple working Streamlit app directly
    with open("simple_app.py", "w") as f:
        f.write('''
import streamlit as st

st.set_page_config(
    page_title="Fashion News Aggregator",
    page_icon="👗", 
    layout="wide"
)

st.title("👗 Fashion & Beauty News Aggregator")

st.success("✅ Modal deployment is working!")

st.markdown("## 🎉 Deployment Test Successful")

st.markdown("### Features Ready:")
st.markdown("- ✅ Streamlit running on Modal")
st.markdown("- ✅ Web server responding")
st.markdown("- ✅ No function call errors")

if st.button("Test Button"):
    st.balloons()
    st.success("Button works perfectly!")

st.markdown("---")
st.markdown("**Next step**: Deploy full news aggregator once this simple version is confirmed working.")
''')
    
    # Start Streamlit
    cmd = "streamlit run simple_app.py --server.port 8000 --server.enableCORS=false --server.enableXsrfProtection=false --server.headless=true"
    subprocess.Popen(shlex.split(cmd))

if __name__ == "__main__":
    app.serve()