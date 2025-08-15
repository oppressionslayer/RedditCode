I'm working on creating an automatic midi creation to help with creating music. it's actuall really good. It uses Wolfram's Rule30 Automation and i'm going to update it so everytime you can seed it to make a random midi that is actually as good as something you pay for but this is open source



# Rule 30 to MIDI — Enhanced

This project automatically creates unique, high-quality MIDI files using **Wolfram's Rule 30** cellular automaton.  
No AI, no black box — just pure algorithmic generation.  
The goal is to create **4–8 bar MIDI clips** you can modify and use for inspiration — completely **open source**.

Currently supports:
- **Prompt-based seeding** for deterministic output
- **Fully random seeds**
- Multiple scales and timing feels
- Swing and BPM control
- Lead + bass track generation

I plan to add **all ~400 Wolfram rules** and explore their musical potential.

---

## Installation


```bash
git clone https://github.com/yourusername/rule30_to_midi_enhanced.git
cd rule30_to_midi_enhanced
pip install -r requirements.txt
```

with rule30_to_midi_enhanced.py 

try these: it really is quite capable and this is just the start! No AI just Wolfram's Rule 30 and I plan to add all 400 or so rules and see what we can do! My Ultimate goal is to just make 4 to 8 bar midi's that you can modify and use for inspiration without black box AI. This is completely open source!


# Jazz-like with more swing
make_unique_rule30_midi("jazz.mid", "bebop", swing=0.67, bpm=160)

# Ambient/minimal
make_unique_rule30_midi("ambient.mid", "ocean waves", bpm=72, swing=0.52)

# Different scales for genre exploration
# Add to notes_from_bits: scale=[0,2,4,5,7,9,11] for major scale
# or scale=[0,2,3,5,7,8,10] for natural minor
