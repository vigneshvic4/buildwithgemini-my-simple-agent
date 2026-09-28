import math
import random
import struct
import wave

SAMPLE_RATE = 44100
DURATION = 30.0  # seconds
NUM_SAMPLES = int(SAMPLE_RATE * DURATION)
BPM = 84
BEAT_DUR = 60.0 / BPM  # ~0.714 sec per beat
BAR_DUR = BEAT_DUR * 4

# Frequencies for Lo-Fi 7th Chord progression (Cmaj7 -> Am7 -> Fmaj7 -> G7)
CHORDS = [
    [261.63, 329.63, 392.00, 493.88, 130.81],  # Cmaj7 + Low C bass
    [220.00, 261.63, 329.63, 392.00, 110.00],  # Am7 + Low A bass
    [174.61, 220.00, 261.63, 329.63, 87.31],   # Fmaj7 + Low F bass
    [196.00, 246.94, 293.66, 349.23, 98.00],   # G7 + Low G bass
]

def generate_lofi():
    print("Generating upbeat lo-fi track...")
    audio_left = [0.0] * NUM_SAMPLES
    audio_right = [0.0] * NUM_SAMPLES

    for i in range(NUM_SAMPLES):
        t = i / SAMPLE_RATE
        bar_idx = int(t / BAR_DUR) % len(CHORDS)
        beat_in_bar = (t % BAR_DUR) / BEAT_DUR
        time_in_bar = t % BAR_DUR

        # 1. Warm Rhodes / Electric Piano Chords
        chord_freqs = CHORDS[bar_idx]
        chord_val = 0.0
        # Soft tremolo/vibrato LFO
        lfo = 1.0 + 0.15 * math.sin(2 * math.pi * 4.5 * t)
        
        # Chord envelope (soft attack & fade)
        env = math.exp(-0.8 * (time_in_bar % BAR_DUR))
        for f in chord_freqs[:4]:
            # Add fundamental + warm 2nd harmonic
            s = math.sin(2 * math.pi * f * t) + 0.3 * math.sin(2 * math.pi * f * 2 * t)
            chord_val += s
        chord_val *= 0.08 * lfo * env

        # 2. Smooth Bassline
        bass_freq = chord_freqs[4]
        bass_env = math.exp(-1.2 * (beat_in_bar % 1.0))
        bass_val = 0.25 * math.sin(2 * math.pi * bass_freq * t) * bass_env

        # 3. Lo-Fi Beat (Kick, Snare, Hi-Hat)
        beat_idx = int(beat_in_bar)
        t_beat = (time_in_bar % BEAT_DUR)

        # Kick on beat 0 and 2.5
        kick_val = 0.0
        if beat_idx in [0, 2] and t_beat < 0.2:
            freq_sweep = 110.0 * math.exp(-25.0 * t_beat)
            kick_val = 0.4 * math.sin(2 * math.pi * freq_sweep * t_beat) * math.exp(-15.0 * t_beat)

        # Soft Snare / Rimshot on beat 1 and 3
        snare_val = 0.0
        if beat_idx in [1, 3] and t_beat < 0.15:
            noise = random.uniform(-1, 1)
            tone = math.sin(2 * math.pi * 180.0 * t_beat)
            snare_val = 0.2 * (0.7 * noise + 0.3 * tone) * math.exp(-20.0 * t_beat)

        # Hi-Hat every half-beat
        eighth_t = t % (BEAT_DUR / 2)
        hat_val = 0.0
        if eighth_t < 0.05:
            hat_val = 0.05 * random.uniform(-1, 1) * math.exp(-80.0 * eighth_t)

        # 4. Vinyl Hiss & Subtle Crackle
        vinyl_val = 0.015 * random.uniform(-1, 1)
        if random.random() < 0.0015:
            vinyl_val += random.uniform(0.08, 0.2)

        # Combine channels
        sample = chord_val + bass_val + kick_val + snare_val + hat_val + vinyl_val
        
        # Soft limiter / master gain
        sample = max(-0.95, min(0.95, sample))
        
        audio_left[i] = sample
        audio_right[i] = sample * 0.98  # subtle stereo width

    # Write WAV file
    output_wav = "/config/Desktop/Session1/my-simple-agent/lofi_track.wav"
    with wave.open(output_wav, "w") as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        
        frames = bytearray()
        for l, r in zip(audio_left, audio_right):
            l_int = int(l * 32767)
            r_int = int(r * 32767)
            frames.extend(struct.pack("<hh", l_int, r_int))
        wav_file.writeframes(frames)
        
    print(f"Lo-fi track generated successfully at: {output_wav}")

if __name__ == "__main__":
    generate_lofi()
