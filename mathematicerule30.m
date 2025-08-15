
ClearAll[rule30Step, evolveRule30, centerBits, bitsToMIDI]

rule30Step[state_Integer, W_Integer] := Module[
  {mask, left, right},
  mask = BitShiftLeft[1, W] - 1;
  left =
   BitAnd[BitOr[BitShiftLeft[state, 1], BitShiftRight[state, W - 1]],
     mask];
  right =
   BitAnd[BitOr[BitShiftRight[state, 1],
       BitShiftLeft[BitAnd[state, 1], W - 1]], mask];
  BitXor[left, BitOr[state, right]]
]

evolveRule30[W_Integer, T_Integer, seed_ : Null] := Module[
  {s, out = {}},
  s = If[seed === Null, BitShiftLeft[1, Floor[W/2]], seed];
  For[i = 0, i < T, i++,
    s = rule30Step[s, W];
    AppendTo[out, s];
  ];
  out
]

(* Extract center bits *)
centerBits[states_List, W_Integer] := Module[
  {c = Floor[W/2]},
  BitGet[#, c] & /@ states
]

bitsToMIDI[bits_List, path_String, bpm_ : 110.0, beatNote_ : 60,
  scaleSteps_ : {-12, -10, -8, -6, -4, -2, 0}, stepsPerBeat_ : 2,
  swing_ : 0.55, velocity_ : 96] := Module[
  {base = beatNote, scale = scaleSteps, dur = 1.0/stepsPerBeat,
   notes, t = 0.0},
  
  notes = MapIndexed[
     If[#1 == 1,
       SoundNote[base + scale[[Mod[#2[[1]] - 1, Length[scale]] + 1]],
         dur, velocity],
       SoundNote[None, dur]
     ] &,
     bits
   ];
  
  Export[path, Sound[notes]];
  path
]

W = 1024;
T = 512;
states = evolveRule30[W, T];
bits = centerBits[states, W];

out = bitsToMIDI[bits, "rule30_wolfram_friendly.mid", 112,
   36,
   {-12, -10, -8, -6, -4, -2, 0, 2, 4}, (* Added some higher notes for variety *)
   2, 0.56, 96];
Print["wrote ", out]
