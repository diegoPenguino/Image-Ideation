from __future__ import annotations

from io import BytesIO

from PIL import Image, UnidentifiedImageError
import streamlit as st


def render_placeholder(title: str, body: str) -> None:
    with st.container(border=True):
        st.markdown(f"### {title}")
        st.write(body)


def load_image(uploaded_file: st.runtime.uploaded_file_manager.UploadedFile) -> Image.Image:
    image_bytes = uploaded_file.getvalue()
    return Image.open(BytesIO(image_bytes))


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

                with st.container(border=True):
                    st.markdown("### Image preview")
                    st.image(image, use_container_width=True)
                    st.caption(uploaded_file.name)
                    metadata_col_1, metadata_col_2 = st.columns(2)
                    with metadata_col_1:
                        st.metric("File type", uploaded_file.type or "unknown")
                    with metadata_col_2:
                        st.metric("File size", f"{uploaded_file.size:,} bytes")
                    st.write(f"Dimensions: {image.width} × {image.height}")

        render_placeholder(
            "2. Add your own description",
            "A multiline text box will let the user describe the uploaded image.",
        )
        st.button("Imagine", disabled=True, use_container_width=True)

    st.divider()



if __name__ == "__main__":
    main()
