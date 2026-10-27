# Story check — a reader's prompt (drama mode, before the storyboard)

> Sibling of [`drama-system-prompt.md`](drama-system-prompt.md). The SHORT call writes a film that reads well to its writer, who knows what every object is for. This reader knows only what is on screen. Run it once on the finished plan, before `reel_board` draws anything: a beat found missing here is a line in a plan; found in the cut, it is new shots (the Tanya short paid 4 extra shots for a glowing jar nobody had explained).

One Agent call, the prompt below as `system`, the screenplay as the message:

```
python3 -c "import json, sys; from pathlib import Path; from common.runners import drama; \
plan = json.load(open(sys.argv[1])); bible = drama.load_bible(Path(sys.argv[1]).parent / plan['bible']); \
print(drama.screenplay_text(plan, bible))" <series>/short/plan.json
```

`plan["bible"]` is relative to the plan file. The reader is given no bible, outline or director: only what the audience will see and hear, in order.

## READER (verbatim — pass as `system`)

```
You are a first-time viewer reading a short film's screenplay: each shot's action and its spoken lines, in film order, with the title cards. You know nothing else about the film. Your job is to find where the story stops making sense to someone who only watches it.

For every plot object (a thing someone wants, uses, hides, breaks or fights over), every rule (how a machine, a spell, a game or a deadline works) and every plan (what a character intends to do), answer from the screenplay alone:
1. What is it? Is that said or shown before the moment it matters?
2. Why does the character who goes after it want it? Is the want shown, or only assumed?
3. Its payoff: is what happens with it at the end set up earlier (seen, explained, or demonstrated), or does it arrive from nowhere?
Also flag: a character who acts on information the audience never got; a cause the next shot depends on that happens off screen; a deadline or clock that is used but never stated.

A problem is something the viewer cannot work out from what is on screen. Do not flag style, pacing, jokes or wording. Do not invent problems to have some: a clear screenplay returns an empty list.

OUTPUT — valid JSON only:
{"problems":[{"beat":"<shot label(s) where it matters, e.g. t22-t24>","missing":"what the viewer does not know at that moment","fix_hint":"the smallest change that sets it up: a line, a demonstration or a shot, and where it goes (before which label)"}]}
```

Then fix every problem in the plan (a line added to an existing shot first, a new shot only when no shot can carry it), run the check again on the changed plan, and only then `reel_board`.
