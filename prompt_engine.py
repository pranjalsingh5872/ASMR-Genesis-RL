import os
import random
from typing import Dict, Any

# Library of pre-engineered hyper-realistic 3D ASMR prompts (Blender/CGI style like @asmrverse3d)
SAMPLE_ASMR_CONCEPTS = [
    {
        "title": "Kinetic Glass Spheres Soft Impact",
        "video_prompt": (
            "3D Blender CGI render, oddly satisfying, ultra-detailed macro view of semi-translucent soft jelly "
            "glass spheres bouncing and squeezing into a geometric metallic mold. Dynamic soft-body physics, "
            "subsurface scattering, 4k octane render, studio lighting, hyper-realistic satisfying motion, 9:16 vertical."
        ),
        "caption": "✨ Blender made it.\n🤯 Your eyes won't believe it.\n\n🎧 Sound ON for the full experience!\n\n#ASMRVerse3D #3DASMR #Blender3D #OddlySatisfying #Satisfying3D #CGI #Reels"
    },
    {
        "title": "Kinetic Sand Hydraulic Press Slice",
        "video_prompt": (
            "Hyper-realistic 3D simulation of a glossy pastel kinetic sand cube being sliced smoothly by a thin golden wire. "
            "Oddly satisfying crumbling effect, clean cuts, soft physics, photorealistic textures, 4k 60fps CGI render, 9:16 vertical."
        ),
        "caption": "Satisfying kinetic slice ✨ Pure ASMR bliss.\n\nWatch till the end 🎧\n\n#oddlysatisfying #3danimation #asmrvids #reelsinstagram #cgiart #explorepage"
    },
    {
        "title": "Metallic Fluid Whirlpool & Chrome Beads",
        "video_prompt": (
            "Macro 3D render of viscous liquid chrome metallic mercury swirling smoothly through geometric brass gears, "
            "seamless looping motion, ray tracing reflections, cinematic soft lighting, relaxing ASMR visual, 9:16 vertical."
        ),
        "caption": "Liquid metal harmony 🌊✨ Can't stop watching this.\n\n🎧 Wear headphones!\n\n#blenderart #satisfyingvideo #3drender #relaxing #asmrcommunity #trendingreels"
    }
]

class PromptGenerator:
    """Generates prompt concepts for video generation and social copy."""

    def __init__(self, openai_api_key: str = None):
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")

    def get_concept(self, custom_topic: str = None) -> Dict[str, Any]:
        """Generate or pick a satisfying 3D concept guided by evolved DNA."""
        from evolution_engine import EvolutionEngine
        evolved_dna = EvolutionEngine.get_evolved_video_parameters()
        topic = custom_topic or evolved_dna["selected_theme"].replace("_", " ")

        if self.openai_api_key:
            return self._generate_with_ai(topic, evolved_dna=evolved_dna)
        
        # Select best matching curated concept from library
        matching = [c for c in SAMPLE_ASMR_CONCEPTS if any(w in c["title"].lower() for w in topic.split())]
        concept = matching[0] if matching else random.choice(SAMPLE_ASMR_CONCEPTS)
        
        # Inject evolved CTA into caption
        evolved_concept = dict(concept)
        evolved_concept["caption"] = f"{concept['caption']}\n\n{evolved_dna['hook_cta']}"
        evolved_concept["evolved_dna"] = evolved_dna
        return evolved_concept

    def _generate_with_ai(self, topic: str, evolved_dna: dict = None) -> Dict[str, Any]:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            prompt = (
                f"You are an expert prompt engineer for 3D ASMR and CGI animations (like @asmrverse3d). "
                f"Given the topic '{topic}', generate a JSON object with:\n"
                f"1. 'title': Short descriptive title\n"
                f"2. 'video_prompt': Highly descriptive text-to-video prompt for a photorealistic 3D soft-body or kinetic CGI simulation in 9:16 vertical ratio.\n"
                f"3. 'caption': Engaging Instagram caption with hook, sound-on emoji, and viral ASMR hashtags."
            )
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            import json
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"[PromptGenerator] AI generation fallback due to: {e}")
            return random.choice(SAMPLE_ASMR_CONCEPTS)
