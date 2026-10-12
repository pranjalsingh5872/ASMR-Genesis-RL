import os
import wave
import struct
import numpy as np

# Audio parameters: 44.1kHz, 16-bit stereo
SR = 44100
TOTAL_DURATION = 26.0  # 780 frames / 30fps
TOTAL_SAMPLES = int(TOTAL_DURATION * SR)

# Initialize stereo mix buffers
left_channel = np.zeros(TOTAL_SAMPLES, dtype=np.float32)
right_channel = np.zeros(TOTAL_SAMPLES, dtype=np.float32)

def load_wav(filename):
    filepath = os.path.join("assets/curated_sfx", filename)
    if not os.path.exists(filepath):
        # Fallback to assets/audio if not in curated_sfx
        filepath = os.path.join("assets/audio", filename)
    if not os.path.exists(filepath):
        print(f"[!] File not found: {filename}")
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
            
        # Resample if needed
        if framerate != SR:
            import scipy.signal
            num = int(len(l) * SR / framerate)
            l = scipy.signal.resample(l, num)
            r = scipy.signal.resample(r, num)
            
        return l, r

def place_sfx(filename, start_time, volume=1.0, pan=0.0):
    l, r = load_wav(filename)
    if l is None:
        return
    
    start_idx = int(start_time * SR)
    length = len(l)
    end_idx = min(TOTAL_SAMPLES, start_idx + length)
    sfx_len = end_idx - start_idx
    
    if sfx_len <= 0 or start_idx >= TOTAL_SAMPLES:
        return
    
    # Calculate panning gains (-1.0 = full left, +1.0 = full right, 0.0 = center)
    left_gain = volume * (1.0 - max(0.0, pan))
    right_gain = volume * (1.0 + min(0.0, pan))
    
    left_channel[start_idx:end_idx] += l[:sfx_len] * left_gain
    right_channel[start_idx:end_idx] += r[:sfx_len] * right_gain
    print(f"[+] SFX Synced: {filename} at {start_time:.2f}s (pan: {pan:+.2f}, vol: {volume:.2f})")

# -------------------------------------------------------------
# 1. Warm ASMR Binaural Studio Room Ambience
# -------------------------------------------------------------
t = np.linspace(0, TOTAL_DURATION, TOTAL_SAMPLES, endpoint=False)
# Subtle 432Hz harmonic warm drone with 4Hz theta wave binaural beat
binaural_l = np.sin(2 * np.pi * 108.0 * t) * 0.03
binaural_r = np.sin(2 * np.pi * 112.0 * t) * 0.03
# Subtle air tape warmth
tape_air = (np.random.rand(TOTAL_SAMPLES) - 0.5) * 0.006

left_channel += binaural_l + tape_air
right_channel += binaural_r + tape_air

# -------------------------------------------------------------
# 2. EXACT ACTION-SYNCHRONIZED ASMR FOLEY EVENTS
# -------------------------------------------------------------
# Stage 0: 0% SOFT (Rigid metallic gold)
# Frame 24 (0.80s): Ricochets off curved glass bend
place_sfx("glass_ping.wav", 0.80, volume=1.2, pan=-0.2)
place_sfx("metal_ping.wav", 0.82, volume=1.0, pan=-0.1)

# Frame 36 (1.20s): Hard collision with left marble pillar
place_sfx("marble_impact.wav", 1.20, volume=1.4, pan=-0.6)
place_sfx("metal_clank_wobble.wav", 1.22, volume=0.8, pan=-0.5)

# Stage 1: 25% SOFT (Stiff Rubber / Wedged Jam)
# Frame 80 (2.67s): Enters glass funnel
place_sfx("glass_ping.wav", 2.67, volume=0.6, pan=-0.1)
# Frame 108 (3.60s): Wedges tight in curve with friction squeeze
place_sfx("rubber_squish.wav", 3.60, volume=1.3, pan=-0.3)
place_sfx("metal_clank_wobble.wav", 3.65, volume=0.5, pan=-0.3)

# Stage 2: 50% SOFT (Dense Jelly / Elastic Flex)
# Frame 185 (6.17s): Glides through glass tube
place_sfx("marbles_collide.wav", 6.17, volume=0.7, pan=-0.2)
# Frame 230 (7.67s): Suction pop exiting tube
place_sfx("slime_squish.wav", 7.67, volume=0.9, pan=-0.4)
# Frame 248 (8.27s): Strikes left pillar with pancake squish
place_sfx("marble_impact.wav", 8.27, volume=1.2, pan=-0.6)
place_sfx("rubber_squish.wav", 8.29, volume=1.0, pan=-0.6)
# Frame 288 (9.60s): Lands in marble basin with satisfying thud & wobble
place_sfx("marble_drop.wav", 9.60, volume=1.3, pan=0.0)
place_sfx("tactile_clicks.wav", 9.68, volume=0.7, pan=0.0)

# Stage 3: 75% SOFT (Super-Stretchy Jelly Snake)
# Frame 415 (13.83s): Slime stretches through tube
place_sfx("slime_stretch.wav", 13.83, volume=1.4, pan=-0.3)
# Frame 525 (17.50s): Wet gelatin slumps into marble basin
place_sfx("slime_squish.wav", 17.50, volume=1.5, pan=0.0)
place_sfx("tactile_clicks.wav", 17.65, volume=0.8, pan=0.0)

# Stage 4: 100% SOFT (Molten Liquid Gold)
# Frame 705 (23.50s): Liquid stream pours from tube
place_sfx("water_drip.wav", 23.50, volume=1.1, pan=-0.4)
# Frame 718 (23.93s): Splashes and pools in marble funnel depression
place_sfx("water_drip.wav", 23.93, volume=1.3, pan=0.0)
place_sfx("slime_squish.wav", 24.05, volume=0.8, pan=0.0)

# -------------------------------------------------------------
# 3. Master Limiter & Normalization
# -------------------------------------------------------------
# Soft-clip saturation to prevent digital distortion
left_channel = np.tanh(left_channel * 0.95)
right_channel = np.tanh(right_channel * 0.95)

# Normalize to -1.0 dB peak
peak = max(np.max(np.abs(left_channel)), np.max(np.abs(right_channel)))
if peak > 0:
    gain = 0.89 / peak
    left_channel *= gain
    right_channel *= gain

# Write 16-bit Master Stereo WAV
out_wav = "output/MASTER_SCENE1_ASMR_SOUNDTRACK.wav"
with wave.open(out_wav, 'wb') as wav:
    wav.setnchannels(2)
    wav.setsampwidth(2)
    wav.setframerate(SR)
    
    interleaved = np.empty((TOTAL_SAMPLES * 2,), dtype=np.int16)
    interleaved[0::2] = (left_channel * 32767.0).astype(np.int16)
    interleaved[1::2] = (right_channel * 32767.0).astype(np.int16)
    wav.writeframes(interleaved.tobytes())

print(f"[SUCCESS] Action-Driven ASMR Master Audio generated: {out_wav}")
