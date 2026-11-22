# The World in One Page — 22 November 2026

A make.fun bounty entry: a program that draws the world news of
Sunday 22 November 2026 as a single newspaper front page.

[![make.fun](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/madara200599/news-of-2026-11-22/rank.svg)](https://make.fun/bounty/news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/madara200599/news-of-2026-11-22/reward.svg)](https://make.fun/bounty/news-image-20261122)

## What it is

`main.py` (Python 3.13, standard library only) draws a 1024x1024 PNG
front page — masthead dated **SUNDAY 22 NOVEMBER 2026**, a lead story on
the drone strike on the sanctioned Russian cargo ship Sparta II in the
Gulf of Finland, and six more stories from the day: the Gulf standoff,
Estonia's border closure, South Africa's ANC election setback, the COP31
deadlock, new Pentagon limits on US-Canada military ties, and
BepiColombo's arrival at Mercury. Everything is drawn in code with a
built-in PNG encoder and a 5x7 bitmap font: no photos, no network, no
randomness — two runs write byte-identical output.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
# writes out/entry.png (1024x1024, under 1 MiB)
```

## Licence

MIT — see [LICENSE](LICENSE).

Entered via referral code r7k9dyj1
