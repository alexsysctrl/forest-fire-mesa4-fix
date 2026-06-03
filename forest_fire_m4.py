"""Forest Fire model — Mesa 4.x compatible version.

Adapted from the original Mesa tutorial example to work with Mesa 4.x APIs.
Replaces BatchRunner with batch_run(), fixes DataCollector access,
and updates column name handling.
"""

from mesa import Model, Agent
from mesa.space import MultiGrid
from mesa.datacollector import DataCollector
from mesa.time import RandomActivation
import pandas as pd


class FireAgent(Agent):
    """A tree on the grid. Can be unburned, burning, or burned."""

    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.pos = pos
        self.state = "unburned"  # unburned, burning, burned

    def step(self):
        if self.state != "burning":
            return

        # Spread to neighbors
        neighbors = self.model.grid.get_neighbors(
            self.pos, moore=True, include_center=False
        )
        for nx, ny in neighbors:
            cell = self.model.grid.get_cell_list_contents([(nx, ny)])
            if cell and cell[0].state == "unburned":
                if self.model.random.random() < self.model.spread_prob:
                    cell[0].state = "burning"

        # This tree burns out after 1 step
        self.state = "burned"


class ForestFire(Model):
    """Forest fire simulation."""

    def __init__(self, width=100, height=100, density=0.4, spread_prob=0.5):
        super().__init__()
        self.width = width
        self.height = height
        self.spread_prob = spread_prob

        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)

        # Place trees
        for _, pos in self.all_cells:
            if self.random.random() < density:
                agent = FireAgent(1, self, pos)
                agent.state = "unburned"
                self.grid.place_agent(agent, pos)
                self.schedule.add(agent)

        # Light a random tree on fire
        burning_trees = [
            a for a in self.schedule.agents if a.state == "unburned"
        ]
        if burning_trees:
            self.random.choice(burning_trees).state = "burning"

        self.datacollector = DataCollector(
            model_vars={"unburned", "burning", "burned"},
            agent_vars={"state"},
        )

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)


def run_batch(width=100, height=100, density=0.4, spread_prob=0.5, steps=50):
    """Run forest fire with batch_run (Mesa 4.x API)."""
    model = ForestFire(
        width=width, height=height, density=density, spread_prob=spread_prob
    )
    df = model.batch_run(
        schedule_iterative=None,
        max_steps=steps,
        data_collection_period=-1,
        display_name="Forest Fire",
    )

    # Fix column name: batch_run uses "Burned Out" not "BurnedOut"
    if "Burned Out" in df.columns:
        df["burned"] = df["Burned Out"]

    return df


if __name__ == "__main__":
    df = run_batch(density=0.5, spread_prob=0.6, steps=30)
    print(df.tail())
    print(f"\nFinal avg unburned: {df['unburned'].iloc[-1]:.1f}")
    print(f"Final avg burned: {df['burned'].iloc[-1]:.1f}")
