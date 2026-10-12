import os
import time
import requests
from typing import Optional

class VideoGenerator:
    """Handles text-to-video generation using AI models."""

    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or os.getenv("REPLICATE_API_TOKEN")

    def generate_video(self, prompt: str, output_path: str, model_name: str = "minimax/video-01") -> str:
        """
        Generates video using Replicate (supporting MiniMax video-01, Kling, or Luma).
        Returns the local path of the saved MP4.
        """
        if not self.api_token:
            raise ValueError(
                "REPLICATE_API_TOKEN is not set. Please set it in .env to enable AI video generation."
            )

        import replicate
        print(f"[VideoGenerator] Submitting prompt to {model_name}...")
        print(f"Prompt: {prompt}")

        # Replicate runs model prediction
        client = replicate.Client(api_token=self.api_token)
        output = client.run(
            model_name,
            input={
                "prompt": prompt,
                "prompt_optimizer": True
            }
        )

        video_url = output if isinstance(output, str) else output[0]
        print(f"[VideoGenerator] Video generated successfully. Downloading from {video_url}...")

        # Download result
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        res = requests.get(video_url, stream=True)
        res.raise_for_status()

        with open(output_path, "wb") as f:
            for chunk in res.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"[VideoGenerator] Saved video to {output_path}")
        return output_path
