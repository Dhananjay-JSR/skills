---
name: product-video
description: "Plan a product video (feature explainer, launch or promo film) as a storyboard before any production: one-paragraph story plus a timed shot table with visuals, on-screen text, voiceover and motion/sound. Use when asked to make, plan, script or storyboard a product video, demo video, explainer, launch or promo film, in any video tool."
license: MIT
metadata:
  version: "0.1.1"
---

# Product video

A product video earns attention by showing **one real feature doing one real job** for a specific viewer. Weak AI storyboards drift to logos, adjectives and floating mockups. Your job is to find the story in the product, then write a storyboard tight enough that anyone with any video tool could produce it: the timings add up, every claim has a shot that proves it, and every shot shows something real.

## 1. Brief

Collect, from the request and the repo or site:
- the product, and **the one feature** this video is about
- the viewer: who they are and the moment they feel the problem
- the proof that exists: real screens or recordings, real numbers, real output
- the call to action: a real command, URL or button
- length (default 45 s), aspect ratio (default 16:9), voiceover or text-only

Ask in one batch for what's missing. In a non-interactive run, infer the answers, mark them `assumed`, and list them under the storyboard.

## 2. Find the story

1. Write the **spine** in one sentence: "For <viewer>, <feature> turns <before> into <after>."
2. Draft **3 storylines** that would be 3 different films, one line each: e.g. start from the pain, start from the result, or follow one person's task end to end. Pick the one whose proof is strongest. Ask the user to pick when they're available.
3. Shape it as **hook → problem → reveal → proof → payoff → call to action**. Rough budget for 45 s:

| Beat | Time | Job |
|---|---|---|
| Hook | 0–3 s | Show the outcome or the pain itself, not the logo. Even a pain-first hook shows the product or its result within ~5 s |
| Problem | 3–10 s | The viewer's real moment of friction, concretely |
| Reveal | 10–15 s | The feature appearing where the friction was |
| Proof | 15–35 s | The feature doing the job in the real product, 2–4 shots |
| Payoff | 35–40 s | The after state, with one real number or result if one exists |
| Call to action | 40–45 s | Mark plus a concrete action, held long enough to read |

## 3. Storyboard format

Deliver exactly this:

1. **Story:** one paragraph (3–5 sentences) a stranger could read to understand the film.
2. **Shot table:**

| # | Time | Visual | On-screen text | Voiceover | Motion / sound |
|---|---|---|---|---|---|

3. **Checks:** total runtime, voiceover word count, and the list of assets needed, each marked *have*, *capture* or *placeholder*.

## 4. Craft rules

- **Real product only.** Every shot claiming to be the product names its source (a recording, a screenshot of a named screen, the real CLI output). If a screen doesn't exist yet, label a placeholder ("Screenshot: Settings → Motion"). Never invent UI, numbers, logos or testimonials.
- **Every claim gets a proof shot.** If the voiceover says "faster", a shot shows the before and after timing.
- **One idea per shot**, 2–5 s each. A shot over 6 s needs something changing inside it.
- **Vary the framing:** establish the workspace, push in on the one control at 1.5–2× (text still readable), then pull back to where the result is used. Floating close-ups alone lose the context.
- **The cursor or the user's action causes the change.** A click, keypress or spoken word triggers the next state on the same beat.
- **Every line says something specific.** Each voiceover and on-screen line names a product noun, a real number, or the viewer's own words. A line that would fit any product ("Zero compromises", "Your vision, realised") gets rewritten.
- **Text and voice complement each other.** On-screen text is at most ~7 words and stays up for roughly 1 s per 3 words, plus 0.5 s. It labels or quantifies, rather than repeating the voiceover.
- **Voiceover pace** is about 2.3–2.6 words/s: a 45 s film carries ~95–115 words, with breathing room around the reveal.
- **Transitions have a cause:** a morph, a match cut, or a push through an object on screen. Use 3–4 kinds at most per film.
- **Sound:** a quiet music bed, a UI sound on each visible action, and one beat of near-silence just before the reveal.
- **End card:** the product mark lands in the last ~10% and is performed, not faded in. Then the real call to action (the command to type, the URL), held 2–3 s.
- **Accessibility:** captions for all voiceover, no flashing above 3 per second, text contrast that holds over footage.

## 5. Tells to cut

Logo or "Introducing X" as the opening shot · abstract gradient or stock-drone b-roll · tilted 3D floating device mockups · slow zooms over static screenshots standing in for the product working · adjective montages ("Fast. Simple. Powerful.") · generic voiceover ("boost your productivity", "seamless workflow") · invented dashboards or stats · a whoosh transition on every cut · ending on "Try it today!" over a gradient.

## 6. Self-check before handing over

- The shot times add up to the target length, and the voiceover word count fits the pace.
- Every voiceover claim maps to a proof shot number.
- Every product shot names its source, or is a labelled placeholder.
- The hook works with the sound off.
- The call to action is concrete: a command, URL or button the viewer can actually use.
