// Contact background: ReactDrops Topographic Flow on the site red, light
// contours, grain, ring hover. Grain only renders over an elevation gradient
// (textured needs 2+ gradientColors), hence the two close reds; backgroundImage
// is left unset because "none" makes the component ignore gradientColors. Wraps the contact content (as the component
// intends) so pointer moves over the text still reach it for the hover.
import type { ReactNode } from 'react';
import { TopographicFlow } from './reactdrops/topographic-flow';

export default function ContactTopo({ children }: { children?: ReactNode }) {
  return (
    <TopographicFlow
      scale={480}
      density={5}
      speed={1.5}
      distortion={2.4}
      lineWidth={1}
      opacity={1}
      dashLength={7}
      dashGap={8}
      seed={42}
      gradientDiffusion={0}
      paused={false}
      hover={0.85}
      hoverRadius={260}
      hoverFollow={0.16}
      hoverFade={0.8}
      hoverEffect="rings"
      backgroundColor="#e8222b"
      gradientColors={['#c3141d', '#e2262f']}
      grain={0.4}
      lineColor="#ff9da1"
      accentColor="#ffd6d8"
      lineStyle="solid"
    >
      {children}
    </TopographicFlow>
  );
}
