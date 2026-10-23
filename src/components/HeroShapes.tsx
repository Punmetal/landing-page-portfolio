// Hero background: ReactDrops Shape Physics on the site red. Defaults from the
// component, except: an opaque red background (the engine repaints its own
// background every frame, so it cannot be transparent) and its default palette
// minus the red, which would disappear on the red.
// Dragging / click-to-add only with a fine pointer: on touch screens the
// interactive canvas sets touch-action: none and would block scrolling past
// the full-height hero, so there the shapes just fall and pile up.
import { useEffect, useState } from 'react';
import { ShapePhysics } from './reactdrops/shape-physics';
import { solidPalette } from './reactdrops/solid-shapes';

export const heroShapesBackground = '#e8222b';
const colors = solidPalette.filter((c) => c !== '#ea4044');

export default function HeroShapes() {
  const [fine, setFine] = useState(false);
  useEffect(() => {
    const mq = matchMedia('(hover: hover) and (pointer: fine)');
    const sync = () => setFine(mq.matches);
    sync();
    mq.addEventListener('change', sync);
    return () => mq.removeEventListener('change', sync);
  }, []);
  return (
    <ShapePhysics
      background={heroShapesBackground}
      colors={colors}
      interactive={fine}
      followCursor={fine}
      aria-label="Playful 3D shapes falling and piling up. With a mouse, drag a shape or click empty space to add one."
    />
  );
}
