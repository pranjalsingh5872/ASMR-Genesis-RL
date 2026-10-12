import os
import math
import random
import wave
import struct

os.makedirs("assets/audio", exist_ok=True)

def write_wav(filename, duration, gen_fn, sr=44100):
    filepath = os.path.join("assets/audio", filename)
    n_samples = int(duration * sr)
    with wave.open(filepath, 'w') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sr)
        frames = bytearray()
        for i in range(n_samples):
            t = float(i) / sr
            s = gen_fn(t, duration)
            s = max(-1.0, min(1.0, s))
            frames.extend(struct.pack('<h', int(s * 32767.0)))
        wav.writeframes(frames)
    print(f"[+] SFX Created: {filename}")

# 1. Glass Ping / Crisp Resonance
def sfx_glass_ping(t, dur):
    decay = math.exp(-t * 14.0)
    return (math.sin(2*math.pi*2800*t) + 0.5*math.sin(2*math.pi*4200*t) + 0.25*math.sin(2*math.pi*7100*t)) * decay * 0.85

# 2. Glass Slide / Friction inside tube
def sfx_glass_slide(t, dur):
    noise = (random.random() * 2 - 1) * math.exp(-t * 4.0) * 0.15
    whine = math.sin(2*math.pi*(1600 + 400*math.sin(t*8))*t) * math.exp(-t * 5.0) * 0.35
    return noise + whine

# 3. Metallic Gold Ping (Lustrous brass impact)
def sfx_gold_ping(t, dur):
    decay = math.exp(-t * 9.0)
    return (math.sin(2*math.pi*1150*t) + 0.7*math.sin(2*math.pi*2320*t) + 0.4*math.sin(2*math.pi*3480*t)) * decay * 0.9

# 4. Heavy Marble Base Thud (Deep solid shockwave)
def sfx_marble_thud(t, dur):
    decay = math.exp(-t * 24.0)
    return (math.sin(2*math.pi*82*t) + 0.6*math.sin(2*math.pi*164*t)) * decay * 0.95

# 5. Pillar Ricochet / Deflection
def sfx_pillar_ricochet(t, dur):
    decay = math.exp(-t * 18.0)
    pitch_bend = 1200 * math.exp(-t * 15.0) + 300
    return math.sin(2*math.pi*pitch_bend*t) * decay * 0.9

# 6. Rubbery Tube Squeeze (25% Soft Jam)
def sfx_tube_squeeze(t, dur):
    decay = math.exp(-t * 6.0)
    f = 380 - 150 * (t / dur)
    wobble = math.sin(2*math.pi*22*t)
    return math.sin(2*math.pi*f*t + wobble*1.5) * decay * 0.85

# 7. Wet Gelatin Squish (50% Soft)
def sfx_gelatin_squish(t, dur):
    decay = math.exp(-t * 10.0)
    f = 240 * math.exp(-t * 8.0) + 70
    squelch = math.sin(2*math.pi*f*t + math.sin(t*30)*2.0)
    bubble = (random.random()*2 - 1) * math.exp(-t * 20.0) * 0.25
    return (squelch + bubble) * decay * 0.9

# 8. Elastic Slime Stretch (75% Soft Jelly Snake)
def sfx_slime_stretch(t, dur):
    decay = math.exp(-t * 4.0)
    f = 160 + 80 * math.sin(2*math.pi*4*t)
    hum = math.sin(2*math.pi*f*t) * decay * 0.7
    pop = math.sin(2*math.pi*800*t) * math.exp(-(t-0.2)**2 / 0.005) if t > 0.2 else 0
    return hum + pop * 0.5

# 9. Viscous Liquid Slump / Melt (100% Soft)
def sfx_liquid_slump(t, dur):
    decay = math.exp(-t * 5.0)
    f = 110 + 220 * math.exp(-t * 6.0)
    ooze = math.sin(2*math.pi*f*t) * decay * 0.8
    splash = (random.random()*2 - 1) * math.exp(-t * 12.0) * 0.3
    return ooze + splash

# 10. Soft Body Wobble Jiggle
def sfx_jiggle_wobble(t, dur):
    decay = math.exp(-t * 5.0)
    wobble_freq = 14.0
    carrier = math.sin(2*math.pi*180*t) * math.sin(2*math.pi*wobble_freq*t)
    return carrier * decay * 0.85

# 11. Suction Tube Pop (Snaking exit from glass tube)
def sfx_suction_pop(t, dur):
    decay = math.exp(-t * 25.0)
    f = 50 + 600 * math.exp(-t * 30.0)
    return math.sin(2*math.pi*f*t) * decay * 0.95

# 12. Deep Binaural ASMR Studio Ambience (Warm relaxing background)
def sfx_binaural_ambience(t, dur):
    left = math.sin(2*math.pi*55.0*t) * 0.12
    right = math.sin(2*math.pi*58.5*t) * 0.12  # 3.5 Hz calming theta beat
    air = (random.random()*2 - 1) * 0.015       # Subdued analog tape warmth
    return left + right + air

if __name__ == "__main__":
    print("[*] Building 12 Specialized ASMR Sound FX Library...")
    write_wav("01_glass_ping.wav", 0.7, sfx_glass_ping)
    write_wav("02_glass_slide.wav", 1.0, sfx_glass_slide)
    write_wav("03_gold_ping.wav", 0.9, sfx_gold_ping)
    write_wav("04_marble_thud.wav", 0.8, sfx_marble_thud)
    write_wav("05_pillar_ricochet.wav", 0.6, sfx_pillar_ricochet)
    write_wav("06_tube_squeeze.wav", 0.9, sfx_tube_squeeze)
    write_wav("07_gelatin_squish.wav", 0.8, sfx_gelatin_squish)
    write_wav("08_slime_stretch.wav", 1.2, sfx_slime_stretch)
    write_wav("09_liquid_slump.wav", 1.5, sfx_liquid_slump)
    write_wav("10_jiggle_wobble.wav", 1.0, sfx_jiggle_wobble)
    write_wav("11_suction_pop.wav", 0.5, sfx_suction_pop)
    write_wav("12_binaural_ambience.wav", 30.0, sfx_binaural_ambience)
    print("\n[+] 12 Core ASMR Audio Effects Successfully Synthesized & Saved to assets/audio/")
