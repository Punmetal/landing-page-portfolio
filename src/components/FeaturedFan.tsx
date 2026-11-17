// Fan of project covers above the bookshelf (ReactDrops Fan Gallery, configured
// as specified; items come from projects.ts via ProjectIndex.astro).
import { FanGallery, type FanGalleryItem } from './reactdrops/fan-gallery';

export default function FeaturedFan({ items }: { items: FanGalleryItem[] }) {
  return (
    <FanGallery
      items={items}
      cardWidth={162}
      aspectRatio={0.8}
      spacing={0.69}
      curve={0.14}
      tilt={14.5}
      lift={42}
      spread={0.2}
      stackFrom="left"
      speed={0.7}
      stagger={0.09}
      bounce={0.35}
      hoverSpeed={0.28}
      radius={18}
      entrance="stack"
      trigger="scroll"
      viewportStart={75}
      once={true}
      showTitle={false}
      ariaLabel="Project covers"
    />
  );
}
