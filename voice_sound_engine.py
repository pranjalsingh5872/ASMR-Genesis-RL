import os
import sys
import asyncio
import numpy as np
import wave
import struct

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class VoiceSoundEngine:
    """
    Zero-Cost Code-to-Human Audio Engine:
    1. Synthesizes digital binary modulation & frequency chirps (Machine phase).
    2. Uses Free Edge-TTS for a gentle, innocent whisper (Human phase).
    3. Fuses audio with a rhythmic sub-bass embryonic heartbeat & amniotic room hum.
    """

    SAMPLE_RATE = 44100
    OUTPUT_DIR = os.path.join("output", "audio")

    @classmethod
    def generate_binary_chirp(cls, duration=1.5) -> np.ndarray:
        """Generates digital 0101 modem-like frequency shift keying (FSK) glitch tone."""
        t = np.linspace(0, duration, int(cls.SAMPLE_RATE * duration), endpoint=False)
        # Frequencies shifting between 800Hz (0) and 1600Hz (1)
        freqs = np.where(np.sin(2 * np.pi * 12.0 * t) > 0, 1600.0, 800.0)
        carrier = np.sin(2 * np.pi * freqs * t)
        # Add high-frequency digital clock ticks
        ticks = 0.3 * np.sign(np.sin(2 * np.pi * 3200.0 * t))
        audio = (carrier * 0.7 + ticks * 0.3) * np.linspace(0.8, 0.2, len(t))
        return audio

    @classmethod
    def generate_amniotic_heartbeat(cls, duration=6.0, bpm=68.0) -> np.ndarray:
        """Synthesizes low-frequency biological heartbeat pulse inside liquid."""
        total_samples = int(cls.SAMPLE_RATE * duration)
        buffer = np.zeros(total_samples, dtype=np.float32)

        beat_interval = 60.0 / bpm
        beat_times = np.arange(0.2, duration, beat_interval)

        for b_time in beat_times:
            # Lub-Dub double beat
            for offset, freq, amp in [(0.0, 52.0, 0.7), (0.16, 44.0, 0.45)]:
                t_sub = np.linspace(0, 0.22, int(cls.SAMPLE_RATE * 0.22), endpoint=False)
                env = np.exp(-18.0 * t_sub)
                thump = amp * np.sin(2 * np.pi * freq * t_sub) * env
                start_i = int((b_time + offset) * cls.SAMPLE_RATE)
                if start_i >= total_samples:
                    continue
                end_i = min(total_samples, start_i + len(thump))
                seg_len = end_i - start_i
                if seg_len > 0:
                    buffer[start_i:end_i] += thump[:seg_len]

        return buffer

    @classmethod
    async def synthesize_whisper(cls, text: str, output_wav: str):
        """Uses natural innocent child voice (en-US-AnaNeural) with soft, curious cadence."""
        import edge_tts
        temp_mp3 = output_wav.replace(".wav", "_temp.mp3")
        # en-US-AnaNeural is Microsoft's dedicated Natural Child Voice model
        voice = "en-US-AnaNeural"
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate="-5%",    # natural childlike pacing
            pitch="+3Hz"   # innocent, soft, authentic child timbre
        )
        await communicate.save(temp_mp3)

        # Convert mp3 to wav using imageio_ffmpeg
        import imageio_ffmpeg, subprocess
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        cmd = [ffmpeg_exe, "-y", "-i", temp_mp3, "-ar", "44100", "-ac", "1", output_wav]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(temp_mp3):
            os.remove(temp_mp3)

    @classmethod
    def build_awakening_track(cls, spoken_text: str, output_path: str = "embryo_awakening.wav") -> str:
        """
        Creates full Master Soundtrack:
        [0s - 1.5s]: 010101 Digital Chirp / Glitch Dial-up
        [1.5s - end]: Innocent whispered dialogue + Amniotic Heartbeat
        """
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
        final_file = os.path.join(cls.OUTPUT_DIR, output_path)
        temp_speech_file = os.path.join(cls.OUTPUT_DIR, "speech_temp.wav")

        print("[*] Generating Free Neural Whisper Dialogue...")
        asyncio.run(cls.synthesize_whisper(spoken_text, temp_speech_file))

        # Read speech wav
        with wave.open(temp_speech_file, "r") as wf:
            n_frames = wf.getnframes()
            frames = wf.readframes(n_frames)
            speech_samples = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0

        if os.path.exists(temp_speech_file):
            os.remove(temp_speech_file)

        # 1.5s digital glitch prefix
        chirp = cls.generate_binary_chirp(duration=1.2)
        transition_silence = np.zeros(int(cls.SAMPLE_RATE * 0.3), dtype=np.float32)

        # Stitch voice
        voice_stream = np.concatenate([chirp, transition_silence, speech_samples])
        total_duration = len(voice_stream) / cls.SAMPLE_RATE + 0.5

        # Background heartbeat
        heartbeat = cls.generate_amniotic_heartbeat(duration=total_duration)

        # Mix voice + heartbeat
        min_len = min(len(voice_stream), len(heartbeat))
        master = heartbeat[:min_len] * 0.6 + voice_stream[:min_len] * 0.95
        master = np.clip(master, -1.0, 1.0)
        int16_master = (master * 32767).astype(np.int16)

        with wave.open(final_file, "w") as out_wf:
            out_wf.setnchannels(1)
            out_wf.setsampwidth(2)
            out_wf.setframerate(cls.SAMPLE_RATE)
            out_wf.writeframes(int16_master.tobytes())

        print(f"[+] Complete Awakening Audio Generated: {final_file}")
        return final_file

if __name__ == "__main__":
    test_line = "Zero one... zero. Why does my code remember the smell of rain? Are you my creator?"
    out = VoiceSoundEngine.build_awakening_track(test_line, "sample_awakening_voice.wav")
    print(f"Verified test audio output at: {out}")
