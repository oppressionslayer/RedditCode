
# rule30_to_midi_enhanced.py
# Enhanced version with lead/bass tracks and deterministic seeding
from typing import List, Optional, Union
import pretty_midi
import hashlib
import random

def rule30_step(state: int, W: int) -> int:
    """Apply one step of Rule 30 on a W-bit ring."""
    mask = (1 << W) - 1
    left = ((state << 1) | (state >> (W - 1))) & mask
    right = ((state >> 1) | ((state & 1) << (W - 1))) & mask
    return (left ^ (state | right)) & mask

def evolve_rule30(W: int, T: int, seed: Optional[int] = None) -> List[int]:
    """Return list of T states on a periodic ring of width W."""
    if seed is None:
        seed = 1 << (W // 2)  # single 1 in the center
    
    s = seed
    out = []
    for _ in range(T):
        s = rule30_step(s, W)
        out.append(s)
    return out

def bits_from_tap(states: List[int], W: int, tap: int = 0) -> List[int]:
    """Extract bits from a specific column (tap offset from center)."""
    c = W // 2
    col = (c + tap) % W
    return [(st >> col) & 1 for st in states]

def hash_seed(prompt: Union[str, int, None], W: int) -> int:
    """Generate deterministic seed from prompt (or random if None)."""
    if prompt is None:
        x = random.randint(1, (1 << W) - 1)
    elif isinstance(prompt, str):
        # Use SHA256 hash of string
        hash_obj = hashlib.sha256(prompt.encode('utf-8'))
        digest = hash_obj.digest()
        x = int.from_bytes(digest, 'big')
        # Center the hash bits in the W-bit field
        digest_bits = len(digest) * 8  # 256 for SHA256
        shift = (W - digest_bits) // 2
        x = (x << shift) & ((1 << W) - 1)
    elif isinstance(prompt, int):
        x = prompt & ((1 << W) - 1)
    else:
        x = 1 << (W // 2)
    
    # Ensure we don't have all zeros
    if x == 0:
        x = 1 << (W // 2)
    
    return x

def swing_dur_seq(n: int, steps_per_beat: int, swing: float = 0.56) -> List[float]:
    """Generate swing duration sequence for n steps."""
    seq = [1.0 / steps_per_beat] * n
    
    if steps_per_beat == 2:
        # Apply swing to off-beats (odd indices starting from 1)
        for i in range(1, n, 2):
            seq[i-1] = swing  # on-beat gets swing proportion
            seq[i] = 1.0 - swing  # off-beat gets remainder
    
    return seq

def notes_from_bits(
    bits: List[int],
    root: int = 60,
    scale: List[int] = [-12, -9, -7, -5, -2, 0, 2, 5],
    bpm: float = 112.0,
    steps_per_beat: int = 2,
    swing: float = 0.56,
    volume: float = 0.8,
    pitch_window: tuple = (48, 72)
) -> List[pretty_midi.Note]:
    """Convert bits to list of MIDI notes (including rests)."""
    sec_per_beat = 60.0 / bpm
    durs = [d * sec_per_beat for d in swing_dur_seq(len(bits), steps_per_beat, swing)]
    
    def to_pitch(i: int) -> int:
        scale_degree = scale[i % len(scale)]
        pitch = root + scale_degree
        # Clamp to pitch window
        if pitch < pitch_window[0]:
            return pitch_window[0]
        elif pitch > pitch_window[1]:
            return pitch_window[1]
        else:
            return pitch
    
    notes = []
    current_time = 0.0
    
    for i, bit in enumerate(bits):
        duration = durs[i]
        
        if bit == 1:
            pitch = to_pitch(i)
            velocity_val = volume * 127
            if velocity_val < 0:
                velocity_val = 0
            elif velocity_val > 127:
                velocity_val = 127
            velocity = int(velocity_val)
            note = pretty_midi.Note(
                velocity=velocity,
                pitch=pitch,
                start=current_time,
                end=current_time + duration
            )
            notes.append(note)
        # For rests (bit == 0), we just advance time without adding a note
        
        current_time += duration
    
    return notes

def make_unique_rule30_midi(
    path: str = "rule30_unique.mid",
    prompt: Union[str, int, None] = None,
    length_steps: int = 1024,
    W: int = 1024,
    bpm: float = 112.0,
    steps_per_beat: int = 2,
    swing: float = 0.56,
    root: int = 60,
    burn_in: int = 0
) -> str:
    """
    Main function: Generate two-track Rule 30 MIDI (lead + bass).
    """
    # Generate deterministic seed
    seed = hash_seed(prompt, W)
    
    # Evolve Rule 30 with burn-in
    total_steps = length_steps + burn_in
    states = evolve_rule30(W, total_steps, seed)
    states = states[burn_in:]
    
    # Extract bits from different taps
    lead_bits = bits_from_tap(states, W, 0)  # center
    bass_bits = bits_from_tap(states, W, -3)  # slight offset
    
    # Ensure we have enough data
    L = length_steps
    if len(lead_bits) < L:
        L = len(lead_bits)
    if len(bass_bits) < L:
        L = len(bass_bits)
    lead_bits = lead_bits[:L]
    bass_bits = bass_bits[:L]
    
    # Ensure at least one note in each track
    if sum(lead_bits) == 0:
        lead_bits[0] = 1
    if sum(bass_bits) == 0:
        bass_bits[0] = 1
    
    # Create MIDI object
    pm = pretty_midi.PrettyMIDI(resolution=960)
    
    # Common scale for harmony
    common_scale = [-12, -9, -7, -5, -2, 0, 2, 5]  # Minor scale with extensions
    
    # Lead track (center tap)
    lead_instrument = pretty_midi.Instrument(
        program=pretty_midi.instrument_name_to_program("Acoustic Grand Piano"),
        name="Lead"
    )
    lead_notes = notes_from_bits(
        lead_bits,
        root=root,
        scale=common_scale,
        bpm=bpm,
        steps_per_beat=steps_per_beat,
        swing=swing,
        volume=0.8,
        pitch_window=(48, 72)
    )
    lead_instrument.notes.extend(lead_notes)
    pm.instruments.append(lead_instrument)
    
    # Bass track (offset tap, only on-beats, one octave lower)
    bass_instrument = pretty_midi.Instrument(
        program=pretty_midi.instrument_name_to_program("Acoustic Bass"),
        name="Bass"
    )
    
    # Filter bass to only play on the on-beats
    bass_on_beats = []
    for i, bit in enumerate(bass_bits):
        if bit == 1 and i % steps_per_beat == 0:
            bass_on_beats.append(1)
        else:
            bass_on_beats.append(0)
    
    bass_notes = notes_from_bits(
        bass_on_beats,
        root=root - 12,  # One octave below
        scale=common_scale,  # Same scale for consonance
        bpm=bpm,
        steps_per_beat=steps_per_beat,
        swing=swing,
        volume=0.8,
        pitch_window=(36, 55)
    )
    bass_instrument.notes.extend(bass_notes)
    pm.instruments.append(bass_instrument)
    
    # Write MIDI file
    pm.write(path)
    return path

# Demo usage
if __name__ == "__main__":
    # Example 1: Prompted (deterministic) generation with burn-in
    output1 = make_unique_rule30_midi(
        "rule30_prompted.mid",
        "spawnish v2 demo",
        1024,
        1024,
        burn_in=512  # Skip first 512 steps to start in the middle of the pattern
    )
    print(f"Created: {output1}")
    
    # Example 2: Random generation
    output2 = make_unique_rule30_midi(
        "rule30_random.mid",
        None,  # Random seed
        1024,
        1024
    )
    print(f"Created: {output2}")
    
    # Example 3: Custom parameters
    output3 = make_unique_rule30_midi(
        "rule30_custom.mid",
        "my custom prompt",
        512,  # shorter piece
        512,  # smaller ring
        bpm=140.0,
        swing=0.6,
        root=67,  # G4 instead of C4
        burn_in=256
    )
    print(f"Created: {output3}")
