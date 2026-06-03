from __future__ import annotations
from streamlit.runtime.uploaded_file_manager import UploadedFile

import hashlib
from io import BytesIO

from PIL import Image, UnidentifiedImageError
import streamlit as st

from image_ideation.exceptions import ImageDescriptionError
from image_ideation.image_descriptor import describe_image
from image_ideation.image_generator import generate_image
from image_ideation.prompts import build_image_generation_prompt


def render_placeholder(title: str, body: str) -> None:
    with st.container(border=True):
        st.markdown(f"### {title}")
        st.write(body)


def load_image(uploaded_file: UploadedFile) -> Image.Image:
    image_bytes = uploaded_file.getvalue()
    return Image.open(BytesIO(image_bytes))


def make_input_signature(image_bytes: bytes, user_description: str) -> str:
    digest = hashlib.sha256()
    digest.update(image_bytes)
    digest.update(b"::")
    digest.update(user_description.strip().encode("utf-8"))
    return digest.hexdigest()


def main() -> None:
    st.set_page_config(
        page_title="Image Ideation App",
        page_icon="A",
        layout="wide",
    )

    st.title("Image Ideation App")
    st.caption(
        "Compete with an AI to see who can describe better an image! Upload an image, describe it as accurately as possible, and generate two AI interpretations side by side (One generated from your description and one generated from the AI's description)."
    )

    with st.sidebar:
        st.header("Workflow")
        st.markdown(
            "1. Upload an image\n"
            "2. Optionally describe it as accurate as possible\n"
            "3. Click Imagine\n"
            "4. Review two generated images :)"
        )
        st.divider()

    input_col, results_col = st.columns(2, gap="large")

    with input_col:
        st.subheader("Input")
        uploaded_file = st.file_uploader(
            "Upload an image",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=False,
            help="Upload a PNG, JPG, JPEG, or WEBP image",
        )

        if uploaded_file is None:
            render_placeholder(
                "Image preview",
                "Upload an image to see it here.",
            )
        else:
            try:
                image = load_image(uploaded_file)
            except UnidentifiedImageError:
                st.error("The uploaded file could not be read as an image.")
            else:
                st.session_state["uploaded_image"] = {
                    "name": uploaded_file.name,
                    "type": uploaded_file.type,
                    "size": uploaded_file.size,
                    "image": image,
                }
                st.session_state["uploaded_image_bytes"] = uploaded_file.getvalue()
                st.session_state["uploaded_image_hash"] = hashlib.sha256(
                    uploaded_file.getvalue()
                ).hexdigest()

                with st.container(border=True):
                    st.markdown("### Image preview")
                    preview_col, _ = st.columns(2)
                    with preview_col:
                        st.image(image, width="stretch")
                    st.caption(uploaded_file.name)
                    metadata_col_1, metadata_col_2 = st.columns(2)
                    with metadata_col_1:
                        st.metric("File type", uploaded_file.type or "unknown")
                    with metadata_col_2:
                        st.metric("File size", f"{uploaded_file.size:,} bytes")
                    st.write(f"Dimensions: {image.width} x {image.height}")
                
                user_description = st.text_area(
                    "Describe the image",
                    key="user_description",
                    placeholder="Describe as accurate as possible the uploaded image",
                    height=140,
                )

        imagine_clicked = st.button("Imagine", width="stretch")

        if imagine_clicked:
            if uploaded_file is None:
                st.error("Please upload an image before pressing Imagine.")
            else:
                current_user_description = st.session_state.get("user_description", "").strip()
                current_signature = make_input_signature(
                    st.session_state["uploaded_image_bytes"],
                    current_user_description,
                )

                with st.spinner("Describing the uploaded image..."):
                    try:
                        model_description = describe_image(
                            st.session_state["uploaded_image_bytes"],
                            mime_type=uploaded_file.type,
                        )
                    except ImageDescriptionError as exc:
                        st.error(str(exc))
                        model_description = None

                if model_description:
                    results_state: dict[str, object] = {
                        "signature": current_signature,
                        "model_description": model_description,
                    }

                    with st.spinner("Generating image 1 from the model description..."):
                        try:
                            results_state["model_image_bytes"] = generate_image(
                                build_image_generation_prompt(model_description)
                            )
                        except Exception as exc:
                            st.error(str(exc))

                    if current_user_description:
                        with st.spinner("Generating image 2 from your description..."):
                            try:
                                results_state["user_image_bytes"] = generate_image(
                                    build_image_generation_prompt(current_user_description)
                                )
                            except Exception as exc:
                                st.error(str(exc))
                    else:
                        results_state["user_image_bytes"] = None

                    st.session_state["generated_results"] = results_state

    with results_col:
        st.subheader("Results")
        uploaded_image = st.session_state.get("uploaded_image")
        current_user_description = st.session_state.get("user_description", "").strip()
        current_signature = (
            make_input_signature(st.session_state["uploaded_image_bytes"], current_user_description)
            if uploaded_image is not None and "uploaded_image_bytes" in st.session_state
            else None
        )
        generated_results = st.session_state.get("generated_results")

        if uploaded_image is None:
            render_placeholder(
                "Generated images",
                "Upload an image, add an optional description, and press Imagine to generate both results.",
            )
        else:
            if not generated_results or generated_results.get("signature") != current_signature:
                render_placeholder(
                    "Generated images",
                    "Press Imagine to generate the LLM description first, then both images from that description and your optional prompt.",
                )
            else:
                with st.container(border=True):
                    st.markdown("### LLM-generated description")
                    st.write(generated_results["model_description"])

                model_image_bytes = generated_results.get("model_image_bytes")
                user_image_bytes = generated_results.get("user_image_bytes")

                image_col_1, image_col_2 = st.columns(2, gap="medium")
                with image_col_1:
                    with st.container(border=True):
                        st.markdown("**Image 1 (LLM-generated description)**")
                        if isinstance(model_image_bytes, (bytes, bytearray)):
                            st.image(model_image_bytes, width="stretch")
                        else:
                            st.info("Image 1 could not be generated.")
                with image_col_2:
                    with st.container(border=True):
                        st.markdown("**Image 2 (User-generated description)**")
                        if current_user_description:
                            if isinstance(user_image_bytes, (bytes, bytearray)):
                                st.image(user_image_bytes, width="stretch")
                            else:
                                st.info("Image 2 could not be generated.")
                        else:
                            st.info("No user description was provided, so Image 2 was not generated.")

    st.divider()


if __name__ == "__main__":
    main()
