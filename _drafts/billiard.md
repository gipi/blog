---
layout: post
comments: true
title: "Physics of billiard pool"
tags: [physics,]
---
<style>

.axis {
  font: 10px sans-serif;
}

.axis-title {
  text-anchor: end;
}

.axis path,
.axis line {
  fill: none;
  stroke: #000;
  shape-rendering: crispEdges;
}

.axis--x path {
  display: none;
}

.axis--y .tick:not(.tick--one) line {
  stroke-opacity: .15;
}

.line {
  fill: none;
  stroke: steelblue;
  stroke-width: 1.5px;
  stroke-linejoin: round;
  stroke-linecap: round;
}

</style>

Physics is everywhere, and can be used to understand how a simple
game as billiard works.

Consider that the dynamics behind its simple elastic collisions,
name the white ball as \\(\vec{v}\_w\\), then

$$
{1\over2}m\left(\vec{v}\_w\right)^2 = {1\over2}m\left(\vec{v}\_w\right)^2 + {1\over2}m\left(\vec{v}\_w\right)^2
$$

if we cancel out the common factor in each term (i.e. \\({m\over 2}\\)) we obtain a simple
relation

$$
\vec{v}\_{w, in}^2 = \vec{v}\_{w, out}^2 + \vec{v}\_{x, out}^2
$$
that is the geometric definition of the **Pitagorean theorem**: so the
angle between the final velocities of the two balls must be of \\(\pi/2\\)! This
is a result that I learnt when I started studying Physics and amazed me a lot.

So the first relation give us a constraint involving the two final velocities:
i.e. the angle as said above. Following the figure below we now have to know
the angle \\(\beta\\) between the initial velocity (of the white ball) and the
final velocity of the other ball:

To resolve that we can come back to the previous relation and know that it's
not valid when the angle \\(\alpha\\) is zero or \\(\pi/2\\): in the first case
the white ball has a final velocity equal to zero, meanwhile the other ball
has as velocity the initial velocity of the white ball: i.e. the two velocities
are swapped. Confronting these facts with the diagram above we can say that
\\(\alpha=\beta\\) without losing generality. Indeed in the case \\(\alpha=\pi/2\\)
we have the white ball that doesn't touch the other ball, in that case the velocities
remain unchanged.

Now we have the final step: placing correctly the velocities with respect to the
model: we know that the force must act along the perpendicular of the contact surface
so the velocity of the other ball must be directed along the line connecting the two
balls center; from this is easily derived that the final velocity of the white ball
must directed at right angle with respect of this.

Below a simple [D3](https://www.d3js.org) model to play with

<div id='d3'></div>

<script src="//d3js.org/d3.v3.min.js"></script>
<script src="{{ site.baseurl }}/public/billiard.js"></script>
<script>
d3.xml("{{ site.baseurl }}/public/billiard.svg", "image/svg+xml", function(error, xml) {
  if (error) throw error;
  document.getElementById('d3').appendChild(xml.documentElement);
    initialize();
});

</script>
