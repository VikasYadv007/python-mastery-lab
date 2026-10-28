# Your Python observatory

Overview combines a local particle sculpture with your actual study signals.
Orbit, Double Helix, and Wings are visual formations; the dots are decorative,
not a fabricated measure of mastery. The labelled numbers and topic details use
saved attempts and the currently installed question packs.

## Explore

- Drag the particle scene to rotate it. Focus the scene and use the arrow keys
  for keyboard rotation, Space to toggle motion, or Escape to reset the view.
- Use **Orbit**, **Double helix**, and **Wings** to change the formation.
- Click a floating signal or a progress card to explain its current value.
- Use **Explore a concept** for a quick topic summary. The native topic launchpad
  below provides the actions to start practice, open a coding task, or review that
  topic. Exploring the sculpture itself never saves or grades an attempt.
- The flight plan points to due revision when it exists. Smart Mix, mistake retry,
  and unfinished-session resume remain available.

## Read the signals

Explored means a question has been attempted. Accuracy counts correct results
across attempts and includes self-assessed coding. Mastered means a streak of at
least three correct attempts. Revision totals include overdue questions. Current
practice streaks use IST and remain active through yesterday. Unavailable question
packs are excluded from the overview's signals.

## Motion and accessibility

The scene respects reduced-motion preferences on its first visit. Use **Enable
motion** to opt in, or **Pause motion** to stop it. Only the formation and explicit
motion preference are stored in browser session storage; no study history is put
there. The renderer stops when it leaves the viewport or the document is hidden,
and disconnects its animation loop, event listeners, and observers on navigation.
Particle count and display resolution are bounded for smaller screens.

The native study controls are separate from the decorative canvas and remain
available without its interaction. All topic names are inert escaped data, and
all executable JavaScript is authored in `mastery_lab/assets/overview.js`. No
imported question code, remote script, or graphics service is executed.

## Checks

Run the Python suite for rendering data, escaping, and native study actions.
Run `node --test tests/overview_scene.test.cjs` for formations, keyboard pause,
reduced motion, visibility handling, rerender freshness, and teardown behavior.
Node.js LTS is only a development-test dependency, not a server dependency.
