
import json
import gradio as gr

from src.data_pipeline import process_documents
from src.retrieval import retrieve, build_index_from_file, load_index
from src.eligibility import check_eligibility
from src.rag import generate_answer


KB_READY = False

SCHEMES = [
    "PM_KISAN",
    "AYUSHMAN_BHARAT_PMJAY",
    "PMAY_URBAN",
    "PMAY_GRAMIN",
    "PMJDY",
    "ATAL_PENSION_YOJANA",
    "PMJJBY",
    "PMSBY",
    "PM_MUDRA",
    "PM_UJJWALA",
    "PMFBY",
]


def initialize():
    global KB_READY

    try:
        try:
            load_index()
        except Exception:
            chunks = process_documents()

            if not chunks:
                KB_READY = False
                return "Knowledge base empty. Please add scheme data first."

            build_index_from_file()
            load_index()

        KB_READY = True
        return "Knowledge base initialized successfully!"

    except Exception as exc:
        KB_READY = False
        return f"Initialization error: {type(exc).__name__}: {exc}"


def answer_user(query, profile_text, language, selected_scheme):

    if not KB_READY:
        return "Please click **Initialize Knowledge Base** first."

    if not query or not query.strip():
        return "Please enter a question."

    # Parse optional user profile
    profile = None

    if profile_text and profile_text.strip():
        try:
            profile = json.loads(profile_text)

            if not isinstance(profile, dict):
                return "Profile must be a JSON object."

        except json.JSONDecodeError:
            return 'Invalid JSON. Example: {"state": "Punjab"}'

    try:
        # Retrieve relevant scheme information
        chunks = retrieve(query, top_k=5)

        if not chunks:
            return "No relevant information found. Please try another question."

        # Run eligibility only for the explicitly selected scheme
        eligibility = None

        if profile and selected_scheme:
            eligibility = check_eligibility(selected_scheme, profile)

        # Generate grounded response
        result = generate_answer(
            query,
            chunks,
            eligibility,
            language
        )

        answer = result.get("answer", "No answer generated.")

        output = f"## BharatSahayak\n\n{answer}\n\n"

        # Display preliminary eligibility
        if eligibility:
            output += "### Preliminary Eligibility Assessment\n\n"
            output += "```json\n"
            output += json.dumps(
                eligibility,
                ensure_ascii=False,
                indent=2
            )
            output += "\n```\n\n"

        elif profile and not selected_scheme:
            output += (
                "### Eligibility Assessment\n\n"
                "Select a scheme from the dropdown to check "
                "preliminary eligibility.\n\n"
            )

        # Display sources
        output += "### Sources\n\n"

        sources = result.get("sources", [])

        if sources:
            for source in sources:
                title = source.get("source_title", "Official source")
                url = source.get("source_url", "")

                if url:
                    output += f"- [{title}]({url})\n"
                else:
                    output += f"- {title}\n"
        else:
            output += "Source metadata unavailable.\n"

        # Disclaimer
        disclaimer = result.get(
            "disclaimer",
            "Verify all details on official government portals."
        )

        output += f"\n> {disclaimer}"

        return output

    except Exception as exc:
        return f"Application error: {type(exc).__name__}: {exc}"


# ---------------- GRADIO INTERFACE ----------------

with gr.Blocks(title="BharatSahayak") as demo:

    gr.Markdown(
        """
        # 🇮🇳 BharatSahayak

        ### Hindi-English Government Scheme Assistant

        Discover government schemes, understand benefits,
        and check preliminary eligibility.
        """
    )

    status = gr.Markdown(
        "Knowledge base not initialized. Click the button below."
    )

    init_btn = gr.Button(
        "Initialize Knowledge Base",
        variant="secondary"
    )

    init_btn.click(
        fn=initialize,
        outputs=status
    )

    language = gr.Dropdown(
        choices=[
            ("English", "en"),
            ("हिन्दी", "hi")
        ],
        value="en",
        label="Response Language"
    )

    query = gr.Textbox(
        label="Your Question",
        placeholder=(
            "I am a farmer in Punjab. "
            "Which government schemes may be relevant?"
        ),
        lines=3
    )

    selected_scheme = gr.Dropdown(
        choices=SCHEMES,
        value=None,
        label="Select Scheme for Eligibility Assessment",
        info="Optional. Select a scheme if you want a preliminary eligibility check.",
        interactive=True
    )

    profile = gr.Textbox(
        label="Optional User Profile (JSON)",
        placeholder='{"state": "Punjab", "occupation": "farmer"}',
        lines=4
    )

    submit = gr.Button(
        "Ask BharatSahayak",
        variant="primary"
    )

    output = gr.Markdown()

    submit.click(
        fn=answer_user,
        inputs=[
            query,
            profile,
            language,
            selected_scheme
        ],
        outputs=output
    )

    gr.Markdown(
        """
        ---
        **Disclaimer:** BharatSahayak provides preliminary,
        evidence-grounded guidance only. It does not make
        official eligibility decisions. Always verify details
        with the relevant government authority.
        """
    )


if __name__ == "__main__":
    demo.launch(share=True)
