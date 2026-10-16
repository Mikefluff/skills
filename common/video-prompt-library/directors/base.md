# Base director — a long narrative film for YouTube, shot in 15-second Seedance scenes

Every drama director extends this file (`extends: base` on its first line) and lists only the rules it changes or adds: a rule with the same number replaces this one, a new number (101 and up) is appended. The drama chain reads the merged set as the director's rules; `python3 -c "from common.runners import drama; print(drama.director('base'))"` prints it. The numbers are working defaults from retention practice on long AI-film channels and from Seedance's own limits, not measurements of this repo's output; a series that measures otherwise changes them in its own director.

1. The first 3 seconds of the episode are an event in motion — a chase, a fall, a door breaking — never a title, a landscape at rest or a character introducing himself. The question the episode answers is asked inside the first 15-second scene.
2. Every 60-90 s something irreversible happens: a death, a reveal, a betrayal, a door that cannot be closed again. Between them, the stakes rise in each scene; no scene leaves the situation where it found it.
3. Each scene has one want and one obstacle, and ends on a changed state or an open question. A scene that only shows a place or explains the past is cut, or its information goes into a line said under pressure.
4. A scene is one Seedance generation of 15 s holding 3-5 shots with hard cuts, each shot 2-5 s. Never one 15-second take unless the director says so for one moment of the episode.
5. Cut with a double change: shot size and angle change together at every cut (wide → close-up over the shoulder, never medium → slightly closer medium).
6. Keep the line of action. Two characters facing each other stay on their sides of the frame for the whole exchange; the camera crosses only on a visible move (a dolly round them) or an insert.
7. A scene that continues the previous one in the same place opens on the angle the previous scene ended on, then moves the camera at least 30° by its first cut, on the same side of the line, and names who is where ("Malai on the left, Phaya on the right, the lake behind them").
8. Every shot names its size, angle, lens, one camera move with direction and speed, and what moves inside the frame. A shot with nothing moving is a still.
9. Dialogue lines are short: at most 12 words or 2.5 s of speech per line, at most 3 lines per scene, at most 2 speakers per scene. A long speech is split across scenes, with a cut-away in between. When two characters trade lines, each line is in its own shot on its speaker (shot / reverse shot); two speakers sharing one shot get lines put on the wrong mouth.
10. A spoken line sits in a shot where the speaker's face is close or medium, frontal or three-quarter, mouth visible, camera slow. Lines over wides, backs and fast moves are written as voice-over with lips closed, or moved.
11. Every line is written in the episode's language, in {}, after the speaker's name and one physical acting note: "Malai says, catching her breath, eyes on the water: {...}". No emotion words alone ("sadly"); the note is what the body does.
12. Silence between lines is staged: a look, a hand that stops, a breath. A line answers the action before it; nobody says what the picture already shows.
13. Sound inside the generation is diegetic only: footsteps, rain, horses, crowd murmur, fire. No music, no score, no narrator unless the scene names one. The score is laid over the episode later.
14. Light is motivated and continuous: the same source, direction and colour for every scene in the same place and time. A change of time or weather is a new location reference, not an adjective.
15. Each scene names its characters by the Image that is each of them, in the asset lines the runner writes; the body refers to them by name only. Never describe a cast member's face in the body: it fights the reference.
16. At most 2 named characters with visible faces per scene, plus silhouettes. Extras, crowds, soldiers and servants are seen from behind, cropped, in smoke or out of focus — a sharp unknown face in a reference or a keyframe can trip the video model's privacy filter and fail the render.
17. The camera does not explain: no slow pan across a room to show it, no establishing shot longer than 2 s, no shot that exists only to show a costume.
18. Escalate with shorter shots, closer sizes, wider lenses on the action and more hand-held energy toward each irreversible event; after it, one held wide shot of 3-4 s lets the viewer feel it.
19. End every scene with motion or a look that leads into the next one, and end the episode on an unanswered question shown, not said: a figure rising from the water, a door opening, a hand on a hilt.
20. Each scene's prompt is self-contained: the model sees one scene at a time, so who, where, when and the light are restated in every scene in a short sentence.
21. Write shot timings on the scene's own clock: "Shot 1 [0-4s] - ...", integer seconds, no gaps, ending at the scene length.
22. Close every scene with: "[Strictly exclude]: subtitles, on-screen text, logos, watermark, extra people speaking, duplicate characters, music, dissolve transitions."
23. Keep every scene's style line the same for the whole series: medium, lens family, film stock or camera, grade and grain. A series that drifts in grade reads as a compilation.
24. The episode is 8-12 minutes at the default; a 10-minute episode is about 40 scenes. Plan the irreversible events first, then the scenes between them.
