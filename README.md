I'm working on creating an automatic midi creation to help with creating music. it's actuall really good. It uses Wolfram's Rule30 Automation and i'm going to update it so everytime you can seed it to make a random midi that is actually as good as something you pay for but this is open source



# Jazz-like with more swing
make_unique_rule30_midi("jazz.mid", "bebop", swing=0.67, bpm=160)

# Ambient/minimal
make_unique_rule30_midi("ambient.mid", "ocean waves", bpm=72, swing=0.52)

# Different scales for genre exploration
# Add to notes_from_bits: scale=[0,2,4,5,7,9,11] for major scale
# or scale=[0,2,3,5,7,8,10] for natural minor
