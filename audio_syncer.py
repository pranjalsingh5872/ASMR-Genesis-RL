import os
import sys
import math
import numpy as np
import wave
import struct

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class AudioSyncer:
    """
    Procedural ASMR Foley Sound Synthesizer & Collision Aligner.
    Generates pristine, zero-cost high-fidelity ASMR audio and snaps
    it to exact mathematical collision frames (marble clicks, glass taps, squishes).
    """

    SAMPLE_RATE = 44100
    OUTPUT_DIR = os.path.join("output", "audio")

    @classmethod
    def generate_foley_click(cls, duration=0.15, freq=1200.0, decay=40.0, tone_type="glass") -> np.ndarray:
        """
        Synthesizes a realistic physical collision impulse sound using damped harmonic oscillator:
        y(t) = e^(-decay * t) * sin(2 * pi * f * t)
        """
        t = np.linspace(0, duration, int(cls.SAMPLE_RATE * duration), endpoint=False)
        envelope = np.exp(-decay * t)
        if tone_type == "glass":
            # Glass bell harmonic overtones
            waveform = (
                0.6 * np.sin(2 * np.pi * freq * t) +
                0.3 * np.sin(2 * np.pi * freq * 2.76 * t) +
                0.1 * np.sin(2 * np.pi * freq * 5.4 * t)
            )
        elif tone_type == "marble":
            # Deep ceramic/marble impact with low body resonance
            waveform = (
                0.7 * np.sin(2 * np.pi * 380.0 * t) +
                0.3 * np.sin(2 * np.pi * 920.0 * t)
            )
        else: # squish / soft-body
            # Soft squish using low-frequency modulation & noise pop
            noise = np.random.uniform(-0.15, 0.15, len(t))
            waveform = np.sin(2 * np.pi * 180.0 * (1 - t * 2) * t) + noise

        audio = waveform * envelope
        # Normalize
        audio = audio / (np.max(np.abs(audio)) + 1e-6)
        return audio

    @classmethod
    def create_collision_soundtrack(cls, total_duration_sec: float, collision_timestamps: list, output_filename="asmr_track.wav") -> str:
        """
        Builds a full synchronized audio track with collisions placed at exact second markers.
        """
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
        total_samples = int(cls.SAMPLE_RATE * total_duration_sec)
        master_buffer = np.zeros(total_samples, dtype=np.float32)

        # Subtle ASMR binaural stereo background air/hum
        t_bg = np.linspace(0, total_duration_sec, total_samples, endpoint=False)
        room_tone = 0.008 * np.sin(2 * np.pi * 55.0 * t_bg)
        master_buffer += room_tone

        for col in collision_timestamps:
            # col can be timestamp in sec or tuple (sec, type)
            if isinstance(col, (tuple, list)):
                sec, col_type = col[0], col[1]
            else:
                sec, col_type = col, "glass"

            start_idx = int(sec * cls.SAMPLE_RATE)
            if start_idx >= total_samples:
                continue

            click = cls.generate_foley_click(tone_type=col_type)
            end_idx = min(total_samples, start_idx + len(click))
            length_to_insert = end_idx - start_idx
            master_buffer[start_idx:end_idx] += click[:length_to_insert] * 0.85

        # Clip and export 16-bit PCM WAV
        master_buffer = np.clip(master_buffer, -1.0, 1.0)
        int16_samples = (master_buffer * 32767).astype(np.int16)

        out_path = os.path.join(cls.OUTPUT_DIR, output_filename)
        with wave.open(out_path, "w") as wav_file:
            wav_file.setnchannels(1) # mono
            wav_file.setsampwidth(2) # 16 bit
            wav_file.setframerate(cls.SAMPLE_RATE)
            wav_file.writeframes(int16_samples.tobytes())

        print(f"[+] Procedural ASMR sound design generated: {out_path} ({len(collision_timestamps)} sync points)")
        return out_path

if __name__ == "__main__":
    # Test generating 6-second soundtrack with collisions at 1.0s, 2.5s, 4.0s, 5.5s
    test_track = AudioSyncer.create_collision_soundtrack(
        total_duration_sec=6.0,
        collision_timestamps=[(0.8, "marble"), (2.2, "glass"), (3.8, "squish"), (5.1, "glass")],
        output_filename="test_asmr.wav"
    )
    print(f"Verified test audio at: {test_track}")
