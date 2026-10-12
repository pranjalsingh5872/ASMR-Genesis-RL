import os
import wave
import numpy as np
import scipy.signal

SR = 44100
TOTAL_DURATION = 5.0  # 300 frames at 60 FPS
TOTAL_SAMPLES = int(TOTAL_DURATION * SR)

left_channel = np.zeros(TOTAL_SAMPLES, dtype=np.float32)
right_channel = np.zeros(TOTAL_SAMPLES, dtype=np.float32)

def load_wav(filepath):
    if not os.path.exists(filepath):
        print(f"[!] Warning: Audio file not found: {filepath}")
        return None, None
    
    with wave.open(filepath, 'rb') as w:
        n_ch = w.getnchannels()
        sampwidth = w.getsampwidth()
        framerate = w.getframerate()
        n_frames = w.getnframes()
        data = w.readframes(n_frames)
        
        if sampwidth == 2:
            samples = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
        else:
            samples = np.frombuffer(data, dtype=np.uint8).astype(np.float32) / 128.0 - 1.0

        if n_ch == 2:
            l = samples[0::2]
            r = samples[1::2]
        else:
            l = samples
            r = samples
            
        if framerate != SR:
            num = int(len(l) * SR / framerate)
            l = scipy.signal.resample(l, num)
            r = scipy.signal.resample(r, num)
            
        return l, r

def place_sfx(filepath, start_time, volume=1.0, pan=0.0):
    l, r = load_wav(filepath)
    if l is None:
        return
    
    start_idx = int(start_time * SR)
    length = len(l)
    end_idx = min(TOTAL_SAMPLES, start_idx + length)
    sfx_len = end_idx - start_idx
    
    if sfx_len <= 0 or start_idx >= TOTAL_SAMPLES:
        return
    
    left_gain = volume * (1.0 - max(0.0, pan))
    right_gain = volume * (1.0 + min(0.0, pan))
    
    left_channel[start_idx:end_idx] += l[:sfx_len] * left_gain
    right_channel[start_idx:end_idx] += r[:sfx_len] * right_gain
    print(f"[+] SFX Synced: {os.path.basename(filepath)} at {start_time:.3f}s (pan: {pan:+.2f}, vol: {volume:.2f})")

# 1. Warm ASMR Binaural Studio Room Ambience
t = np.linspace(0, TOTAL_DURATION, TOTAL_SAMPLES, endpoint=False)
binaural_l = np.sin(2 * np.pi * 108.0 * t) * 0.025
binaural_r = np.sin(2 * np.pi * 112.0 * t) * 0.025
tape_air = (np.random.rand(TOTAL_SAMPLES) - 0.5) * 0.005

left_channel += binaural_l + tape_air
right_channel += binaural_r + tape_air

# 2. Synchronized Foley Events (Exact Frame Timings at 60 FPS)
# Frame 12 (0.20s): Nozzle release suction pop
place_sfx("assets/audio/11_suction_pop.wav", 0.20, volume=1.1, pan=0.0)

# Frame 20 (0.33s): Optical glass glide
place_sfx("assets/audio/02_glass_slide.wav", 0.33, volume=0.8, pan=0.0)

# Frame 30 (0.50s): Marble contact impact
place_sfx("assets/curated_sfx/marble_impact.wav", 0.50, volume=1.3, pan=-0.05)

# Frame 35 (0.58s): Juicy hydrostatic pancake squish
place_sfx("assets/audio/07_gelatin_squish.wav", 0.58, volume=1.5, pan=0.0)
place_sfx("assets/curated_sfx/slime_squish.wav", 0.60, volume=1.2, pan=0.05)

# Frame 48 (0.80s): Elastic rebound & airborne stretch
place_sfx("assets/curated_sfx/slime_stretch.wav", 0.80, volume=0.9, pan=-0.05)

# Frame 60 (1.00s): Secondary contact bounce
place_sfx("assets/curated_sfx/rubber_squish.wav", 1.00, volume=1.1, pan=0.0)

# Frame 75 (1.25s): Harmonic jiggle wobble
place_sfx("assets/audio/10_jiggle_wobble.wav", 1.25, volume=1.3, pan=0.0)

# Frame 95 (1.58s): Liquid slump settling into marble basin
place_sfx("assets/audio/09_liquid_slump.wav", 1.58, volume=1.0, pan=0.0)

# 3. Master Soft Limiting & Normalization
max_peak = max(np.max(np.abs(left_channel)), np.max(np.abs(right_channel)))
if max_peak > 0.95:
    scale = 0.92 / max_peak
    left_channel *= scale
    right_channel *= scale

# Convert to 16-bit PCM
left_int16 = (np.clip(left_channel, -1.0, 1.0) * 32767.0).astype(np.int16)
right_int16 = (np.clip(right_channel, -1.0, 1.0) * 32767.0).astype(np.int16)

interleaved = np.empty((TOTAL_SAMPLES * 2,), dtype=np.int16)
interleaved[0::2] = left_int16
interleaved[1::2] = right_int16

out_dir = os.path.abspath("output/rendered")
os.makedirs(out_dir, exist_ok=True)
out_wav = os.path.join(out_dir, "cloth_jelly_60fps_foley.wav")

with wave.open(out_wav, 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(interleaved.tobytes())

print(f"[SUCCESS] Foley audio exported: {out_wav} ({TOTAL_DURATION}s, 44.1kHz stereo)")
