import os
import math
import wave
import struct

os.makedirs("assets/audio", exist_ok=True)

def generate_wav(filepath, duration_sec, sample_rate, generator_func):
    """Utility to generate uncompressed 16-bit PCM WAV audio."""
    n_samples = int(duration_sec * sample_rate)
    with wave.open(filepath, 'w') as wav:
        wav.setnchannels(1)  # Mono
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(sample_rate)
        
        frames = bytearray()
        for i in range(n_samples):
            t = float(i) / sample_rate
            sample_val = generator_func(t, duration_sec)
            # Clip between -1.0 and 1.0
            sample_val = max(-1.0, min(1.0, sample_val))
            int_val = int(sample_val * 32767.0)
            frames.extend(struct.pack('<h', int_val))
        wav.writeframes(frames)
    print(f"[+] Generated ASMR SFX: {filepath}")

# 1. Glass Impact / Clink (Crisp resonant bell-like ping)
def glass_clink(t, dur):
    decay = math.exp(-t * 18.0)
    # Fundamental + glass inharmonic overtones
    f1 = math.sin(2 * math.pi * 2400 * t)
    f2 = math.sin(2 * math.pi * 3850 * t) * 0.6
    f3 = math.sin(2 * math.pi * 5620 * t) * 0.3
    return (f1 + f2 + f3) * decay * 0.85

# 2. Gelatin / Jelly Squish (Low frequency squishy damped wobble)
def jelly_squish(t, dur):
    decay = math.exp(-t * 8.0)
    # Pitch drop from 320Hz down to 80Hz + wobble
    freq = 320.0 * math.exp(-t * 12.0) + 80.0
    wobble = math.sin(2 * math.pi * 18.0 * t)
    wave_val = math.sin(2 * math.pi * freq * t + wobble)
    return wave_val * decay * 0.9

# 3. Marble Base Thud (Solid heavy acoustic impact)
def marble_thud(t, dur):
    decay = math.exp(-t * 22.0)
    sub = math.sin(2 * math.pi * 95 * t)
    body = math.sin(2 * math.pi * 180 * t) * 0.5
    return (sub + body) * decay * 0.95

# 4. Viscous Liquid Slump / Drip (Smooth liquid pool splash)
def liquid_slump(t, dur):
    decay = math.exp(-t * 6.0)
    # Bubble/drip frequency sweep
    freq = 150.0 + 400.0 * (t / dur)
    wave_val = math.sin(2 * math.pi * freq * t)
    # Add subtle white noise splash texture
    import random
    noise = (random.random() * 2.0 - 1.0) * math.exp(-t * 15.0) * 0.25
    return (wave_val * decay * 0.75) + noise

# 5. Binaural ASMR Studio Ambient Hum (Relaxing spatial bed)
def asmr_ambience(t, dur):
    # Warm sub-bass binaural hum with gentle pink oscillation
    f1 = math.sin(2 * math.pi * 60.0 * t) * 0.15
    f2 = math.sin(2 * math.pi * 63.5 * t) * 0.12  # 3.5Hz binaural beat
    f3 = math.sin(2 * math.pi * 120.0 * t) * 0.05
    return f1 + f2 + f3

if __name__ == "__main__":
    sr = 44100
    generate_wav("assets/audio/glass_clink.wav", 0.8, sr, glass_clink)
    generate_wav("assets/audio/jelly_squish.wav", 1.2, sr, jelly_squish)
    generate_wav("assets/audio/marble_thud.wav", 0.6, sr, marble_thud)
    generate_wav("assets/audio/liquid_slump.wav", 1.5, sr, liquid_slump)
    generate_wav("assets/audio/asmr_ambience.wav", 30.0, sr, asmr_ambience)
    print("\n[+] Full ASMR sound effect library created successfully!")
