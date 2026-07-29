# 07 — Transcript acquisition

**What to build:** Every Source ends up with a transcript carrying speaker labels,
acquired as cheaply as possible.

Three paths in strict order of preference: a transcript the publisher already provides
via the podcast transcript RSS tag; then free captions where the Source exists on
YouTube; then paid ASR as a fallback. Paying to transcribe audio that is already
transcribed is the main way this budget escapes, so the cheap paths must genuinely be
tried first.

Speaker labels are not optional. The Recommender is usually the guest and not the host,
so ticket 08 cannot attribute a claim to the right person without knowing who is
speaking. Free captions typically carry no speaker information — those Sources need a
diarization step or they are not usable downstream.

**Blocked by:** 06 — Feed and Source from RSS.

**Status:** ready-for-agent

- [ ] A Source with a publisher transcript uses it and incurs no ASR cost
- [ ] A Source without one falls back to captions, then to ASR
- [ ] Every usable transcript carries speaker-attributed segments with timestamps
- [ ] Transcripts lacking speaker attribution are marked unusable rather than passed
      downstream unlabelled
- [ ] Which path was used is recorded per Source, so acquisition cost is measurable
- [ ] ASR spend is observable and bounded — a runaway backlog cannot silently drain the account
- [ ] A failed transcription is retried and surfaced, and does not block other Sources
