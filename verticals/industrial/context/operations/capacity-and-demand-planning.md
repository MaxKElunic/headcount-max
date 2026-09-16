## On a plant floor, capacity is one resource

Everything above describes a system's capacity in aggregate. A plant does not have one. It has a
sequence of resources, and its output is set by the slowest one in the current product mix — which
moves when the mix moves.

Three consequences that do not follow from the aggregate view:

- **The utilization threshold applies per resource, not per plant.** A plant at 70% overall with the
  press at 95% behaves like a plant at 95%. Aggregate utilization is the number most likely to be
  quoted and least likely to explain the queue.
- **Capacity added anywhere else produces inventory.** Speeding up a feeding operation puts more
  work in front of the constraint. The line looks busier and ships the same.
- **The constraint is worth protecting, not optimizing.** Time lost at the constraint is lost for the
  whole plant and cannot be recovered elsewhere. Keeping a deliberate buffer of work in front of it,
  and scheduling maintenance and changeovers around it, is worth more than a percentage point of
  its own efficiency.

**Changeover time is capacity that looks like demand.** A resource whose nominal rate covers the
order book can still be short, because a third of its hours go to setups the schedule implies. When
capacity looks adequate on paper and is not in practice, count the changeovers the sequence requires
before adding a shift. `operations:production-management` covers the sequencing decision that sets
that number.

**Labor availability is a separate constraint from machine availability**, and on most sites the
binding one. Certified operators, shift coverage, and absence run on different arithmetic from
equipment, and a plan built on machine hours alone will be wrong every time a qualified operator is
out.
